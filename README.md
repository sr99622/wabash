# wabash

This repo demonstrates the integration of C++ into python using pybind11. The C++ program includes the use of threads and zero-copy binary data access. It is designed to measure the memory consumption of running YOLO inference on a video file. Running OpenVINO on a recent Intel CPU with an integrated graphics chip (iGPU) will work best. The iGPU driver should be pre-installed with windows. Pytorch on NVIDIA will run as well, although the installation may require modification to get the proper pytorch version to match the CUDA version installed on the machine.

<b><i>Currently only windows is supported</i></b>

&nbsp;
### System Requirements
---

To build the project, Windows development tools are required. The following components are needed. The primary link points to the Homepage for each tool. To download a recent version of the tool known to work with this project, use the .EXE link to get the executable installer.

   | Tool Homepage | Download |
   |-----------|:--------:|
   |[C++ Desktop Development Tools for Visual Studio](https://visualstudio.microsoft.com/downloads/) | [.EXE](https://aka.ms/vs/17/release/vs_BuildTools.exe) |
   |[git](https://git-scm.com/install/windows) | [.EXE](https://github.com/git-for-windows/git/releases/download/v2.51.2.windows.1/Git-2.51.2-64-bit.exe) |
   |[CMake](https://cmake.org/download/) | [.EXE](https://github.com/Kitware/CMake/releases/download/v4.2.0-rc2/cmake-4.2.0-rc2-windows-x86_64.msi) |
   |[Python](https://www.python.org/downloads/windows/) | [.EXE](https://www.python.org/ftp/python/3.13.9/python-3.13.9-amd64.exe) |

&nbsp;
### Project Configuration
---

The project additionally requires FFmpeg shared libraries, which are available courtesy of [GyanD](https://github.com/GyanD/codexffmpeg). Because the FFmpeg components are installed relative to the project source files, the project is first set up with git. The script below will download the project source code along with the FFMPEG shared runtime binaries and necessary development components. After completion of the code installation, the script will create and activate a python virtual environment within the source directory.

To configure the project, open a ***Windows PowerShell*** prompt and run the following commands. Please note that the script will locate the repository in the user's home directory, then cd to the wabash directory to execute the balance of commands from there.

```
cd $env:HOMEPATH
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

&nbsp;
### Compilation and Runtime
---

Compile the project using the build.bat script.

```
scripts\windows\build
```

The program can now be run independent of the virtual environment. The executable is located in the env\Scripts directory as wabash.exe.

```
env\Scripts\wabash
```

&nbsp;
### Development
---

To develop the python domain of the program, it is necessary to uninstall the wabash python module from the current environment. This is required because the python code will look for the module in the environment first, which has the effect of ignoring changes made to the python source code. The following assumes that the python environment has been activated as shown above. To observe changes made to python code, use the following.

```
pip uninstall wabash
python run.py
```

Any changes made in the C++ domain require re-building the project in order to be observed. Note that the build will install a copy of the python module binary into the local wabash directory alongside the FFmpeg binaries required for runtime. This enables local development when the python module is un-installed from the current environment. The binary filename is prefixed with an underscore, which is namespace translated by ```__init__.py```. As an aside, it is not necessary to use powershell after the initial configuration, a standard command prompt works fine.

&nbsp;
### Distribution
---

To build the distribution files, install the build module into the environment. For CMake to successfully find FFmpeg in this scenario, it is necessary to set the environment variable first before running build on the source directory. The files will populate in the dist folder.

```
pip install build
set FFMPEG_INSTALL_DIR=%CD%\ffmpeg
python -m build --sdist --wheel
```

The distribution .whl file can be used to install the program on an arbitrary machine within a python environment. It includes all the necessary runtime binaries so no further configuration is required to run the program on the target machine. The file can be uploaded to pypi or installed using the pip command directly on the local filename. 

&nbsp;
### Installing Arbitrary Python Versions
---

It is necessary to install multiple Python versions on the development machine for distribution and testing purposes. A selection of Python installation executables is available by script. To install a particular version of Python, use the following command.

```
scripts\windows\install_python <XXX>
```

where `<XXX>` represents the Python version as one of the following choices `[310, 311, 312, 313]`, each of which represents a Python version without the dot between major and minor versions.

Note that the installer will not include the Python executable in the system PATH. The Python installation can be started using the command

```
scripts\windows\start_python <XXX>
```

To create a virtual environment using one of these Python installations

```
scripts\windows\create_venv <XXX> <name>
```

&nbsp;
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








