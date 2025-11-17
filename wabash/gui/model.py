#********************************************************************
# wabash/gui/model.py
#
# Copyright (c) 2025  Stephen Rhodes
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#*********************************************************************

import os
import sys
import platform
import hashlib
import requests
from PyQt6.QtWidgets import QMainWindow
from wabash import Stream
import numpy as np
from torchvision.transforms import functional
import torch
import torch.nn as nn
from wabash.gui.yolox.models import YOLOX, YOLOPAFPN, YOLOXHead
from wabash.gui.yolox.utils import postprocess
from loguru import logger
from pathlib import Path
import threading
from time import sleep
import traceback

if (sys.platform != "darwin") and (platform.machine() != "aarch64"):
    import openvino as ov


NUM_CLASSES = 80
INF_DIMENSION = 640

class Model():
    def __init__(self, mw: QMainWindow):
        print("MODEL INIT", os.getcwd())
        print(mw.getCachePath())

        self.mw = mw
        self.loaded = False

        thread = threading.Thread(target=self.load_model)
        thread.start()
        mw.waitDialog.signals.show.emit("Please wait while the model is initialized")
        #self.load_model()

    def __call__(self, ary):
        # collect the thread frame image data
        if len(ary.shape) < 3:
            return
        h = ary.shape[0]
        w = ary.shape[1]

        # collect parameters needed for image resize and padding to meet model input specs
        inf_size = (INF_DIMENSION, INF_DIMENSION)
        ratio = min(inf_size[0] / h, inf_size[1] / w)
        inf_shape = (int(h * ratio), int(w * ratio))
        bottom = inf_size[0] - inf_shape[0]
        side = inf_size[1] - inf_shape[1]
        pad = (0, 0, side, bottom)

        # resize and pad (on hardware if available)
        timg = functional.to_tensor(ary).to(self.torch_device)
        timg *= 255
        timg = functional.resize(timg, inf_shape)
        timg = functional.pad(timg, pad, 114)
        timg = timg.unsqueeze(0)

        # model is run on the image, outputs are raw data and need post processing
        if self.api == "PyTorch":
            with torch.no_grad():
                outputs = self.model(timg)
            boxes = self.postprocess(outputs, w, h)
            return boxes
        if self.api == "OpenVINO":
            infer_request = self.compiled_model.create_infer_request()
            infer_request.set_input_tensor(ov.Tensor(np.asarray(timg)))
            infer_request.infer()
            outputs = infer_request.get_output_tensor(0).data
            boxes = self.postprocess(outputs, w, h)
            return boxes

    def postprocess(self, outputs, w, h):
        confthre = 50 / 100
        nmsthre = 0.65
        if isinstance(outputs, np.ndarray):
            outputs = torch.from_numpy(outputs)
        outputs = postprocess(outputs, NUM_CLASSES, confthre, nmsthre)
        
        boxes = []
        inf_size = (INF_DIMENSION, INF_DIMENSION)
        ratio = min(inf_size[0] / h, inf_size[1] / w)

        if outputs[0] is not None:
            output = outputs[0].cpu().numpy().astype(float)
            output[:, 0:4] /= ratio
            output[:, 4] *= output[:, 5]
            output = np.delete(output, 5, 1)

            labels = output[:, 5].astype(int)
            for i in range(len(labels)):
                # object type filtering goes here
                boxes.append(output[i, 0:4])

        return np.array(boxes)

    def load_model(self):
        try:
            self.api = self.mw.streamPanel.cmbAPI.currentText()
            self.torch_device = None
            self.ov_device = "AUTO"
            ov_model = None
            if self.api == "OpenVINO":
                ov_model_name = self.mw.getCachePath() / "model.xml"
                print("ov_model_name", ov_model_name)
                if os.path.exists(ov_model_name):
                    ov_model = ov.Core().read_model(ov_model_name)

            # if using openvino, the model needs to be converted on the first pass
            if self.api == "PyTorch" or (self.api == "OpenVINO" and not ov_model):
                # find the hardware for the model
                self.torch_device_name = "cpu"
                if torch.cuda.is_available():
                    self.torch_device_name = "cuda"
                if torch.backends.mps.is_available():
                    self.torch_device_name = "mps"
                self.torch_device = torch.device(self.torch_device_name)

                # get_model is an internal yolox command for creating the model framework, create on device
                model_size = [0.33, 0.50]
                self.model = self.get_model(NUM_CLASSES, model_size[0], model_size[1], None).to(self.torch_device)
                # model is set to inference mode, rather than training
                self.model.eval()

                # model weights are assigned, download the file from github if needed
                self.model_name = "yolox_s"
                self.ckpt_file = ckpt_path = self.mw.getCachePath() / f"{self.model_name}.pth"
                if not os.path.exists(self.ckpt_file):
                    print("DID NOT FIND FILE", self.ckpt_file, ckpt_path)
                    self.download_ckpt()
                self.model.load_state_dict(torch.load(self.ckpt_file, map_location="cpu")["model"])

                # intialize the model with random data
                initializer_data = torch.rand(1, 3, INF_DIMENSION, INF_DIMENSION)
                self.model(initializer_data.to(self.torch_device))

            if self.api == "OpenVINO":
                if not self.torch_device:
                    self.torch_device = torch.device("cpu")
                initializer_data = torch.rand(1, 3, INF_DIMENSION, INF_DIMENSION)
                if not ov_model:
                    ov_model = ov.convert_model(self.model, example_input=initializer_data)
                    ov.save_model(ov_model, ov_model_name)
                ov_model.reshape({0: [1, 3, INF_DIMENSION, INF_DIMENSION]})
                ov_config = {}
                #if "GPU" in self.ov_device or ("AUTO" in self.ov_device and "GPU" in ov.Core().available_devices):
                #    ov_config = {"GPU_DISABLE_WINOGRAD_CONVOLUTION": "YES"}
                self.compiled_model = ov.compile_model(ov_model, self.ov_device, ov_config)
                self.compiled_model(initializer_data)
            
            self.loaded = True
        except Exception as ex:
            logger.error("Model load failure: {ex}")
            logger.debug(traceback.format_exc())
        self.mw.waitDialog.signals.hide.emit()

    def get_model(self, num_classes, depth, width, act):
        def init_yolo(M):
            for m in M.modules():
                if isinstance(m, nn.BatchNorm2d):
                    m.eps = 1e-3
                    m.momentum = 0.03

        in_channels = [256, 512, 1024]
        backbone = YOLOPAFPN(depth, width, in_channels=in_channels)
        head = YOLOXHead(num_classes, width, in_channels=in_channels)
        model = YOLOX(backbone, head)

        model.apply(init_yolo)
        model.head.initialize_biases(1e-2)
        return model

    def calculate_sha256(self, filename):
        try:
            with open(filename, 'rb') as file:
                hasher = hashlib.sha256()
                while chunk := file.read(4096):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as ex:
            print(f'An error occurred computing the hash for {filename}: {ex}')
            return None

    def download_ckpt(self):
        link = "https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/" + f'{self.model_name}.pth'
        logger.debug(f"Dowloading model weights {link}")
        response = requests.get(link, allow_redirects=True, timeout=(10, 120))
        if not response:
            raise RuntimeError(f'Error downloading {link}: {response.status_code}')
        with open(self.ckpt_file, 'wb') as content:
            content.write(response.content)
        if os.path.isfile(self.ckpt_file):
            hashes = {
                "yolox_tiny": "9de513de589ac98bb92d3bca53b5af7b9acfa9b0bacb831f7999d0f7afaee8f0",
                "yolox_s": "f55ded7181e1b0c13285c56e7790b8f0e8f8db590fe4edb37f0b7f345c913a30",
                "yolox_m": "60076992b32da82951c90cfa7bd6ab70eba9eda243e08b940a396f60ac2d19b6",
                "yolox_l": "1e6b7fa6240375370b2a8a8eab9066b3cdd43fd1d0bfa8d2027fd3a51def2917",
                "yolox_x": "5652330b6ae860043f091b8f550a60c10e1129f416edfdb65c259be6caf355cf"
            }

            verified = False
            if hash := self.calculate_sha256(self.ckpt_file):
                if hash == hashes.get(self.model_name, None):
                    verified = True
            if not verified:
                os.remove(self.ckpt_file)
                raise RuntimeError(f'Error verifying {self.ckpt_file}')

            logger.debug(f'model {self.ckpt_file} was downloaded succesfully')

