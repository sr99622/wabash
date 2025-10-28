import os
import cv2
import time

from py_utils.coco_utils import COCO_test_helper
import numpy as np
from py_utils.rknn_executor import RKNN_model_container
from torchvision.transforms import functional

OBJ_THRESH = 0.25
NMS_THRESH = 0.45
INF_DIMENSION = 640

class Model():
    def __init__(self, mw):
        self.mw = mw
        self.name = "YOLOX"
        self.model = RKNN_model_container('model/yolox.rknn', 'rk3588', None)
        self.co_helper = COCO_test_helper(enable_letter_box=True)

    def __call__(self, ary):
        #ary = np.array(thread.frame, copy=False)
        #ary = np.ascontiguousarray(ary)
        #img_src = ary

        img = self.preprocess(ary)
        outputs = self.model.run([img])
        boxes, classes, scores = self.post_process(outputs)

        if boxes is not None:
            h = ary.shape[0]
            w = ary.shape[1]
            if w > h:
                y_offset = INF_DIMENSION * (1-h/w)/2
                boxes[:, 1::2] -= y_offset
                scale = w/INF_DIMENSION
            else:
                x_offset = INF_DIMENSION * (1-w/h)/2
                boxes[:, 0::2] -= x_offset
                scale = h/INF_DIMENSION
            boxes *= scale
            boxes = boxes.astype(int)

        #return boxes, classes, scores
        #thread.detections = boxes
        return boxes

    def filter_boxes(self, boxes, box_confidences, box_class_probs):
        box_confidences = box_confidences.reshape(-1)
        candidate, class_num = box_class_probs.shape

        class_max_score = np.max(box_class_probs, axis=-1)
        classes = np.argmax(box_class_probs, axis=-1)

        _class_pos = np.where(class_max_score* box_confidences >= OBJ_THRESH)
        scores = (class_max_score* box_confidences)[_class_pos]

        boxes = boxes[_class_pos]
        classes = classes[_class_pos]

        return boxes, classes, scores

    def nms_boxes(self, boxes, scores):
        """Suppress non-maximal boxes.
        # Returns
            keep: ndarray, index of effective boxes.
        """
        x = boxes[:, 0]
        y = boxes[:, 1]
        w = boxes[:, 2] - boxes[:, 0]
        h = boxes[:, 3] - boxes[:, 1]

        areas = w * h
        order = scores.argsort()[::-1]

        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(i)

            xx1 = np.maximum(x[i], x[order[1:]])
            yy1 = np.maximum(y[i], y[order[1:]])
            xx2 = np.minimum(x[i] + w[i], x[order[1:]] + w[order[1:]])
            yy2 = np.minimum(y[i] + h[i], y[order[1:]] + h[order[1:]])

            w1 = np.maximum(0.0, xx2 - xx1 + 0.00001)
            h1 = np.maximum(0.0, yy2 - yy1 + 0.00001)
            inter = w1 * h1

            ovr = inter / (areas[i] + areas[order[1:]] - inter)
            inds = np.where(ovr <= NMS_THRESH)[0]
            order = order[inds + 1]
        keep = np.array(keep)
        return keep


    def box_process(self, position):
        grid_h, grid_w = position.shape[2:4]
        col, row = np.meshgrid(np.arange(0, grid_w), np.arange(0, grid_h))
        col = col.reshape(1, 1, grid_h, grid_w)
        row = row.reshape(1, 1, grid_h, grid_w)
        grid = np.concatenate((col, row), axis=1)
        stride = np.array([INF_DIMENSION//grid_h, INF_DIMENSION//grid_w]).reshape(1,2,1,1)

        box_xy = position[:,:2,:,:]
        box_wh = np.exp(position[:,2:4,:,:]) * stride

        box_xy += grid
        box_xy *= stride
        box = np.concatenate((box_xy, box_wh), axis=1)

        # Convert [c_x, c_y, w, h] to [x1, y1, x2, y2]
        xyxy = np.copy(box)
        xyxy[:, 0, :, :] = box[:, 0, :, :] - box[:, 2, :, :]/ 2  # top left x
        xyxy[:, 1, :, :] = box[:, 1, :, :] - box[:, 3, :, :]/ 2  # top left y
        xyxy[:, 2, :, :] = box[:, 0, :, :] + box[:, 2, :, :]/ 2  # bottom right x
        xyxy[:, 3, :, :] = box[:, 1, :, :] + box[:, 3, :, :]/ 2  # bottom right y

        return xyxy

    def post_process(self, input_data):
        boxes, scores, classes_conf = [], [], []

        input_data = [_in.reshape([1, -1]+list(_in.shape[-2:])) for _in in input_data]
        for i in range(len(input_data)):
            boxes.append(self.box_process(input_data[i][:,:4,:,:]))
            scores.append(input_data[i][:,4:5,:,:])
            classes_conf.append(input_data[i][:,5:,:,:])

        def sp_flatten(_in):
            ch = _in.shape[1]
            _in = _in.transpose(0,2,3,1)
            return _in.reshape(-1, ch)

        boxes = [sp_flatten(_v) for _v in boxes]
        classes_conf = [sp_flatten(_v) for _v in classes_conf]
        scores = [sp_flatten(_v) for _v in scores]

        boxes = np.concatenate(boxes)
        classes_conf = np.concatenate(classes_conf)
        scores = np.concatenate(scores)

        # filter according to threshold
        boxes, classes, scores = self.filter_boxes(boxes, scores, classes_conf)

        # nms
        nboxes, nclasses, nscores = [], [], []
        keep = self.nms_boxes(boxes, scores)
        if len(keep) != 0:
            nboxes.append(boxes[keep])
            nclasses.append(classes[keep])
            nscores.append(scores[keep])

        if not nclasses and not nscores:
            return None, None, None

        boxes = np.concatenate(nboxes)
        classes = np.concatenate(nclasses)
        scores = np.concatenate(nscores)
        return boxes, classes, scores
    
    def preprocess(self, img_src):
        img = self.co_helper.letter_box(img_src, new_shape=(INF_DIMENSION, INF_DIMENSION), pad_color=(0,0,0))
        #img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img

if __name__ == '__main__':

    model = Model()

    img_path = os.path.join('../model', 'portrait.jpg')
    img = cv2.imread(img_path)

    for i in range(100):
        start_time = time.perf_counter()
        boxes, classes, scores = model(img)
        print(boxes)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"count {i} Function executed in: {elapsed_time:.6f} seconds")
    model.model.release()

    for box in boxes:
        left, top, right, bottom = [b for b in box]
        cv2.rectangle(img, (left, top), (right, bottom), (255, 0, 0), 2)

    cv2.imshow("full post process result", img)
    cv2.waitKeyEx(0)

    # release
