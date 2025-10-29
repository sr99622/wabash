# wabash

This repo demonstrates the integration of c++ into python using pybind11. The c++ program includes the use of threads and zero-copy binary data access. It is designed to measure the memory consumption of running YOLO inference on a video file. Running OpenVINO on a recent Intel CPU with an integrated graphics chip will work best. The iGPU driver should be pre-installed with windows. Pytorch on NVIDIA will run as well, you might need to modify the installation to get the proper pytorch version to match your CUDA version.

### Currently only windows is supported

* System Requirements

To build the project, you need to install Visual Studio, git, CMake and Python.


The project requires FFMPEG shared libraries, which are available courtesy of [GyanD](https://github.com/GyanD/codexffmpeg). The FFMPEG shared binaries and all other necessary components are set up by the script below. To configure the project, open a ***Windows PowerShell*** prompt and run the following commands.

```
git clone https://github.com/sr99622/wabash
cd wabash
Invoke-WebRequest -Uri 'https://github.com/GyanD/codexffmpeg/releases/download/8.0/ffmpeg-8.0-full_build-shared.zip' -OutFile 'ffmpeg-8.0-full_build-shared.zip'
Expand-Archive -Path ffmpeg-8.0-full_build-shared.zip -DestinationPath .
move ffmpeg-8.0-full_build-shared ffmpeg
copy ffmpeg\bin\*.dll wabash
del ffmpeg-8.0-full_build-shared.zip
python -m venv env
env\Scripts\activate
```

* Compilation and Runtime

Compile the project using the build.bat script.

```
scripts\windows\build
```

The program can now be run independent of the virtual environment. The executable is located in the env\Scripts directory as wabash.exe. To run

```
env\Scripts\wabash
```

* Development

To develop the python domain of the program, it is necessary to uninstall the wabash python module from the current environment. This is required because the python code will look for the module in the environment first, which has the effect of ignoring changes made to the python source code. The following assumes that you have activated the python environment as shown above. To observe changes made to python code, use the following

```
pip uninstall wabash
python run.py
```

Any changes made in the C++ domain require re-building the project to be observed. Note that the build will install a copy of the python module binary into the local wabash directory alongside the ffmpeg binaries required for runtime. This enables local development when the python module is un-installed from the current environment. The binary filename is prefixed with an underscore, which is namespace translated by ```__init__.py```. As an aside, it is not necessary to use powershell after the initial configuration, a standard command prompt works fine.

* Distribution

To build the distribution files, install the build module into the environment. For CMake to successfully find ffmpeg in this scenario, it is necessary to set the environment variable first before running build on the source directory. The files will populate in the dist folder.

```
pip install build
set FFMPEG_INSTALL_DIR=%CD%\ffmpeg
python -m build --sdist --wheel
```

The distribution whl file can be used to install the program on an arbitrary machine within a python environment. It includes all the necessary runtime binaries so no further configuration is required to run the program on the target machine. The file can be uploaded to pypi or installed using the pip command directly on the local filename. 

### License

Copyright (c) 2025  Stephen Rhodes

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.



