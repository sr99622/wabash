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

To configure the project, open a command prompt and run the following commands. Please note the command `cd wabash` which makes the project directory current. The balance of commands shown here are intended to be run from the project directory.

```
git clone https://github.com/sr99622/wabash
cd wabash
```

The project additionally requires FFmpeg shared libraries, which are available courtesy of [GyanD](https://github.com/GyanD/codexffmpeg). The script below will download the FFmpeg shared runtime binaries and necessary development components and install them in the project directory.

```
scripts\windows\install_ffmpeg
```

Create a virtual environment for the project and activate

```
python -m venv env
env\Scripts\activate
```

&nbsp;
### Compilation and Runtime
---

Compile the project using the compile.bat script.

```
scripts\windows\compile
```

The program can now be run independent of the virtual environment. The executable is located in the env\Scripts directory as wabash.exe. Note that it may take a moment for the application to start on the initial run.

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

Any changes made in the C++ domain require re-compiling the project in order to be observed. Note that the build will install a copy of the python module binary into the local wabash directory alongside the FFmpeg binaries required for runtime. This enables local development when the python module is un-installed from the current environment. The binary filename is prefixed with an underscore, which is namespace translated by `__init__.py`.

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

It may be necessary to install multiple Python versions on the development machine for distribution and testing purposes. A selection of Python installation executables is available by script. To install a particular version of Python, use the following command.

```
scripts\windows\install_python <XXX>
```

where `<XXX>` represents the Python version as one of the following choices `[310, 311, 312, 313]`, each of which represents a Python version without the dot between major and minor versions.

Note that the installer will not alter the system PATH to include the Python executable. The Python installation can be started using the command

```
scripts\windows\start_python <XXX>
```

To create a virtual environment using one of these Python installations

```
scripts\windows\create_venv <XXX> <name>
```

&nbsp;
### Creating a Windows Icon in Gimp
---

Create a new png file with transparent background using 256 x 256 size. After the icon has been drawn in the application and saved as `wabash.png`, use the Layers menu to select Duplicate Layers. This will create another layer with the same image. Click the Layers menu again and select Scale Layer and resize the new layer to 128 x 128. Repeat for other sizes e.g. 64, 32 and 16. Export the file using the File menu and Export As `wabash.ico`. When the dialog prompt appears, rename the file to use the .ico extension. Gimp will automatically format the exported file for ico. The earlier saved .png file is used for the application window icon. These files should be placed in the wabash\gui\resources folder.

&nbsp;
### Building the Installer Program
---

The project includes scripts for building an executable installer using [NSIS](https://sourceforge.net/projects/nsis/). The installed version of the program requires a re-distributable Python version which is supplied by [Astral](https://github.com/astral-sh). The basic philosophy of the installer is to create a copy of a portable python virtual environment on the target system and run the installed env\scripts\wabash.exe executable file from there. 

The installer will copy the post-compilation contents of the local `wabash\wabash` directory into the installation location on the target machine. This is a double edged sword in that any files to be installed onto the target machine can easily be placed in the local wabash\wabash directory, but also any stray artifacts that are generated during development will be installed as well, so it is worthwhile to review the contents of the directory prior to building the installer. The script will automatically remove the local `__pycache__` directories and any pre-exsiting `_wabash.cp*-win_amd64.pyd` files, so those can safely be ignored. The ffmpeg dlls should be included in the installation.

The installer is built from the project directory using the following command.

```
scripts\windows\build_installer
```

The executable installer itself can be found in the `installer` subdirectory.

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









