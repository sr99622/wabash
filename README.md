# wabash

This repo demonstrates the integration of C++ into python using pybind11. The C++ program includes the use of threads and zero-copy binary data access. It is designed to measure the memory consumption of running YOLO inference on a video file. Running OpenVINO on a recent Intel CPU with an integrated graphics chip (iGPU) will work best. The iGPU driver should be pre-installed with windows. Pytorch on NVIDIA will run as well, although the installation may require modification to get the proper pytorch version to match the CUDA version installed on the machine.

### Installation and Operating Instructions

<details><summary><b>Windows</b></summary>

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

Any changes made in the C++ domain require re-compiling the project in order to be observed. Note that the compile script will install a copy of the python module binary into the local wabash directory alongside the FFmpeg binaries required for runtime. This enables local development when the python module is un-installed from the current environment. The binary filename is prefixed with an underscore, which is namespace translated by `__init__.py`.

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

The build_installer script will download NSIS if the program is not already present on the development machine. If this is the case, some user interaction will be required as the script executes. When the NSIS installer shows it's installation dialog, it is recommended to accept all defaults during installation, then decline the automatic startups at the conclusion by de-selecting the presented checkboxes. This will allow the script to continue without interruption.

The installer will copy the post-compilation contents of the local `wabash\wabash` directory into the installation location on the target machine. This is a double edged sword in that any files to be installed onto the target machine can easily be placed in the local wabash\wabash directory, but also any stray artifacts that are generated during development will be installed as well, so it is worthwhile to review the contents of the directory prior to building the installer. The script will automatically remove the local `__pycache__` directories and any pre-exsiting `_wabash.cp*-win_amd64.pyd` files, so those can safely be ignored. The ffmpeg dlls should be included in the installation.

The installer is built from the project directory using the following command.

```
scripts\windows\build_installer
```

The executable installer itself can be found in the `installer` subdirectory.
&nbsp;

---
&nbsp;
</details>


<details><summary><b>Linux</b></summary>

&nbsp;
### Project Configuration
---

A Python version greater than or equal to 3.10 and less than or equal to 3.13 with the ability to create virtual environments is required. Linux distributions ship with a default Python pre-installed and the version can be verified using the command `python3 --version`. In the instructions that follow, some commands may be Python version dependent, and are described using the notation `X.XX` to represent the version. Additionally, some basic tools are required to build the program. Select from the instructions below for your distribution.
&nbsp;

### Install build tools
---

Choose the instructions for your package manager

<details><summary><b>apt</b></summary>
&nbsp;

Install the Python devlopment libraries based on the Python version, substituting the Host Python version for `X.XX`

```
sudo apt install pythonX.XX-dev pythonX.XX-venv
```

Install the build tools

```
sudo apt install curl git cmake g++
```

Install the X11 development libraries if necessary (not needed for Wayland only configuration)

```
sudo apt install '^libxcb.*-dev'
```
---
&nbsp;
</details>

<details><summary><b>dnf</b></summary>
&nbsp;

Install the Python developement libraries based on the Python version. If you are on Fedora 43, please note that some dependencies (OpenVINO) will not work with the installed Python version 3.14, so it is necessary to install Python version 3.13.

---
#### Fedora 43 Only

```
sudo dnf install python3.13-devel
```

#### Fedora 42 and Earlier

```
sudo dnf install python3-devel
```
---
Install the build tools

```
sudo dnf install git cmake g++
```

---
&nbsp;
</details>

<details><summary><b>pacman</b></summary>
&nbsp;

Install build tools

```
sudo pacman -S cmake base-devel
```

---
&nbsp;
</details>

&nbsp;

After installing the build tools, clone the repository and set the current working directory to the project directory.

```
git clone https://github.com/sr99622/wabash
cd wabash
```
&nbsp;

### Install Dependency Libraries and Build Program
---
Dependency libraries are needed on the Host development machine in order to compile and run the program. There are two options for installing these libraries. One option is to use the operating system package manager. This has the advantage of being very simple to implement. The disadvantage is that this type of configuration is non-portable, meaning that the operation of the program is subject to the whims and quirks of the package library which may introduce issues when installed on a particular machine. The other approach is to build portable libraries that can be integrated into a single Python module and will work on a wide variety of linux distributions. The portable library version is recommended and has been developed with script tools to ease the process of creation.

<details><summary><b>Package Manager Libraries (Quick and Easy)</b></summary>
&nbsp;

Choose the instructions for your package manager.

<details><summary><b>apt</b></summary>
&nbsp;

```
sudo apt install libavdevice-dev
```

---
&nbsp;
</details>

<details><summary><b>dnf</b></summary>
&nbsp;

```
sudo dnf -y install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
sudo dnf -y install https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm
sudo dnf -y install ffmpeg-devel --allowerasing
```

---
&nbsp;
</details>

<details><summary><b>pacman</b></summary>
&nbsp;

```
sudo pacman -S ffmpeg
```

&nbsp;
</details>
&nbsp;

With the dependency libraries in place, the program can be built on the host using the following commands.

First create a Python virtual environment. It is recommended to use the full Python version name explicitly when creating the virtual environment. The command below uses `X.XX` in place of the python version on the machine. The python version must be >=3.10 and <=3.13.

```
pythonX.XX -m venv env
source env/bin/activate
```

Now compile and install the program.

```
pip install -v .
```

The program can now be run. The executable is located in the env/bin directory as wabash.exe.

```
env/bin/wabash
```

---
&nbsp;

</details>
&nbsp;

<details><summary><b>Portable Libraries (Recommended)</b></summary>
&nbsp;

A portable version of FFmpeg containing only the necessary library components for the wabash program can be created by compiling from source. There are scripts to do this included with the repository. An important consideration when building a portable program is the version of the Linux kernel on which the library components are built. The Linux kernel is designed to be backward compatible such that programs and libraries built on older versions of the kernel will work on newer versions without modification. This is a very important property of the kernel design. The practical implication is that the program or library under development should be compiled on the oldest version of the kernel as possible in order to achieve maximum compatibility.

There exist several methods to achieve the goal of maximum compatibilty through compilation on older kernel versions. Experience with these methods has led to the following suggestion, which is to create a virtual machine and install the oldest maintained version of Linux Mint onto the virtual machine and compile there. Because Linux Mint is based on older versions of Ubuntu, it will provide the legacy version of the kernel which is maintained to avoid security and stability issues. At the time of this writing, [Linux Mint 21 Vanessa](https://linuxmint.com/edition.php?id=299) is the oldest maintained version. It provides the 5.15 kernel along with glibc version 2.35, which should be compatible with most modern Linux versions.

&nbsp;
### Install QEMU (libvirt) on the Host Development Machine
---

A script has been set up to install [QEMU](https://www.qemu.org/) virtual machine for a variety of Linux distributions. Those using apt, dnf and pacman are supported. In some cases, the script may not be able to identify the family of the distribution, in which case manual instructions are available for reference.

To install by script

```
scripts/linux/vm_install
```

<details><summary>Manual installation</summary>
&nbsp;

---

Choose the instructions for your package manager

<details><summary><b>apt</b></summary>
&nbsp;

```
sudo apt install qemu-kvm libvirt-daemon-system virtinst libvirt-clients bridge-utils virt-manager virt-viewer virtiofsd
sudo setfacl -m u:libvirt-qemu:--x /home
sudo setfacl -m u:libvirt-qemu:--x $HOME
```
&nbsp;

</details>

<details><summary><b>dnf</b></summary>
&nbsp;

```
sudo dnf install @virtualization qemu-kvm libvirt-client libvirt-daemon-kvm virt-manager
```
&nbsp;

</details>

<details><summary><b>pacman</b></summary>
&nbsp;

```
sudo pacman -S --needed virt-manager virt-viewer virtiofsd qemu-desktop libvirt edk2-ovmf dnsmasq iptables-nft
```
&nbsp;

</details>

&nbsp;
### Configure libvirt
---

Configure libvrt to run as a service, then add the user to the groups for non-root access.

```
sudo systemctl start libvirtd
sudo systemctl enable libvirtd
sudo systemctl status libvirtd
sudo usermod -aG libvirt $USER
sudo usermod -aG kvm $USER
```

For Ubuntu or Arch based system, (apt or pacman), the following commands are needed to start the virtual network. 

```
sudo virsh net-start default
sudo virsh net-autostart default
```

Make temporary directories

```
mkdir -p vm/iso vm/hda vm/shared
```

</details>

&nbsp;

Re-boot the machine in order to initialize the configuration for libvirtd.

```
sudo reboot now
```

&nbsp;
### Download ISO
---
The virtual machine is set up with a Linux Mint ISO. The ISO is a few GB in size, so it will take some time to download. There is a script included with the project for this purpose.

```
cd wabash
scripts/linux/vm_download
```

&nbsp;
### Create the Virtual Machine
---
Once the download completes, the virtual machine can be created with following script. Performance of the virtual machine can be improved by editing the script to increase the settings for `--vcpus=4` and `--memory=8192` to values appropriate for the host.


```
scripts/linux/vm_create
```

This will bring up the virtual machine in a window, from where the operating system can be installed. At the conclusion of the operating system installation, the virtual machine should be rebooted.

&nbsp;
### Other Optional Commands For Controlling the Virtual Machine
---
If the virtual machine is shut down, use the following command to start it.

```
sudo scripts/linux/vm_start
```

If you would like to delete the virtual machine, 

```
scripts/linux/vm_delete
```

To list installed virtual machines

```
virsh list --all
```

&nbsp;
### Build the Program on the Virtual Machine
---
After installing Linux Mint 21 on the virtual machine, it is optional to update the software as recommended by the operating system. If the intention is to maintain the project with updates to the code, it can be worthwhile to update the virtual machine operating system, as there is a nag screen that pops up pretty frequently after the machine has been running for a while. If updating, it is recommended to look through the alternate download locations to find a fast server. The update does take some time, about same amount of time as the installation.

To start the build, open a terminal on the virtual machine and install git to download the repository as follows. Please note the `cd wabash` command to change the current directory to `wabash`. This is the location from which repository scripts should be run.

```
sudo apt install -y git
git clone https://github.com/sr99622/wabash
cd wabash
```

Run the following script to build the project portable libraries and distribution wheels for Python versions from 3.10 through 3.13. 

Please note that the script takes some time to run and will stop at points to collect user input for each Python installation as provided by [deadsnakes](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa). Once all the Python versions are installed, subsequent runs of the script do not require user intervention. As a note, it was observed that if the script were to override the user input prompt during Python installation, the process may become corrputed.

```
scripts/linux/build_libs
```

At the completion of the script, there will be a virtual environment folder named for the version X.XX for each of the Python versions, each of which will have the program installed. To test a version of the program, use the command following where ```X.XX``` represents a Python version e.g 3.12

```
X.XX/bin/wabash
```

An installable package for each Python version can be found in the ```wheelhouse``` subdirectory. The script produces a distribution agnostic installer package for each Python version that includes the portable libraries and can be uploaded to the PyPi server. Additionally, a ```stock``` subdirectory is produced that contains portable versions of the dependency libraries and can be used on a development machine for building the project. The following steps will set up a shared directory to transfer these products back to the host machine for further use.

&nbsp;
### Restart the Virtual Machine
---

In order to mount the shared directory, it is necessary to restart the virtual machine. To stop from within the virtual machine, use the command.

```
shutdown now
```

Then from the Host, use the command.

```
sudo scripts/linux/vm_start
```

&nbsp;
### Mount the Shared Directory from the Virtual Machine
---

The virtual machine can mount a shared directory so that files may be passed between the host and the virtual machine. The following script run from inside the virtual machine will do this.

```
cd wabash
sudo scripts/linux/vm_mount_host
```

&nbsp;
### Transfer the Dependency Libraries to the Host
---

The dependency libraries and package wheels can be transferred from the virtual machine to the Host for development of the program. Run the following from the virtual machine.

```
scripts/linux/vm_tar_libs
```

The shared directory resides at `vm/shared`. You should be able to observe files on the Host from the virtual machine at the same location relative to the project directory. 

```
ls vm/shared
```

The file `stock.tar.gz` and the package installer directory `wheelhouse` should be observable in the shared directory. Please note that if files are added to the shared directory by the Host, they may not be immediately observable from the virtual machine. To refresh the directory view in the virtual machine, use `umount vm/shared`, then repeat the `vm_mount_host` command from above.

At this point, the virtual machine is no longer needed and can be shut down.

```
shutdown now
```

&nbsp;
### Install the Dependency Libraries and Build the Program on the Host
---
Create a Python virtual environment on the Host development machine. It is recommended to use the full Python version name explicitly when creating the virtual environment. The version of the system Python can be found with the command `python3 --version`. The command below uses `X.XX` in place of the python version on the machine. The following snippets are intended to be run from the project directory on the Host.

```
pythonX.XX -m venv env
source env/bin/activate
```

The tar package created in the virtual machine should be visible on the Host at `vm/shared/stock.tar.gz`. To install the libraries in the correct locations and build the program, use the following command from the Host.

```
scripts/linux/vm_unpack_libs
```

To test that the build was successful, run the command

```
wabash
```

</details>

&nbsp;
### Development on the Host
---
Program development may include efforts in both Python and C++. There are different methods for observing changes made to the program in these two domains. Further, there is a difference in the compilation procedure for the C++ domain depending on whether the dependency libaries have been installed using the package manager or the portable libraries.

&nbsp;
### Python Code Development
---
To develop the Python domain of the program, it is necessary to uninstall the wabash python module from the current environment. This is required because the python code will look for the module in the environment first, which has the effect of ignoring changes made to the python source code. The following assumes that the python environment has been activated like `source env/bin/activate`. 

To develop the Python code and observe changes made, use the following.

```
pip uninstall wabash
python run.py
```

&nbsp;
### C++ Code Development
---
Any changes made in the C++ domain require re-compiling the project in order to be observed. Note that the compile process will install a copy of the Python module binary into the local wabash directory. This enables local development when the Python module is un-installed from the current environment. The binary filename is prefixed with an underscore, which is namespace translated by `__init__.py`. If the portable libraries are being used, the ffmpeg binaries will also be present in the wabash directory.

To develop C++ code using the portable libraries

```
scripts/linux/compile
env/bin/wabash
```

To develop C++ code using the package manager libraries

```
pip install -v .
env/bin/wabash
```
&nbsp;

<details><summary><b>Notes for Linux Configurations</b></summary>

&nbsp;
### Install VSCode on Manjaro Linux

```
sudo pacman -Syu code
```

&nbsp;
### Fixing the Python Linter in VSCode on Fedora
---

Unfortunately, this can be an issue if you are working on Fedora using VSCode. Add these snippets to your settings.json file if the linter is not picking up the virtual environment.

```
{
    "terminal.integrated.defaultProfile.linux": "bash",
    "terminal.integrated.profiles.linux": {
        "bash": {
            "path": "/bin/bash"
        }
    }
}
```
</details>

&nbsp;

---

</details>

<details><summary><b>Mac OS</b></summary>

&nbsp;

### Project Configuration
---

The project requires dependency libraries on the development machine in order to compile and run. There are two options for installing these libraries. One option is to use the Homebrew package manager to install dependencies. This has the advantage of being very simple to implement. The disadvantage is that this type of configuration is non-portable, meaning that any target machine on which the program would run would require a Homebrew installation. The other approach is to build portable libraries that can be integrated into a single Python module and will work on an arbitrary target machine. The portable library version is recommended and has been developed with script tools to ease the process of creation. Note that the portable libaries require a virtual machine installation for which instructions are included.

Regardless of which type of libraries will be used, the development machine will require some tools in order to be able to compile and run the program. Xcode, Homebrew and Python are required to build the project. 

### Install Xcode Tools
----

To verify if Xcode is installed, use ```xcode-select --version```, which will return a valid version in response if installed. If not installed already, use the command.

```
xcode-select --install
```

### Download the Project Repository
---

Download the repository using git and change the working directory to the project directory.

```
git clone https://github.com/sr99622/wabash
cd wabash
```

### Install Homebrew
---

To verify if Homebrew is installed, use the command ```brew --version```, which will return a valid version if installed. If not installed, the following script will install Homebrew. Source the .zprofile to enable brew environment variables, then install cmake and ninja using brew.

```
scripts/mac/install_brew
source $HOME/.zprofile
brew install cmake ninja
```

### Install Python and Create Virtual Environment
---

A Python version greater than or equal to 3.10 and less than or equal to 3.13 with the ability to create virtual environments is required. There are many ways to install Python on Mac, so if a qualified version of Python installed already, that is fine. The Python version can be observed using the command ```python3 --version```. Alternatively, a script is included to install Python from the official site without adding it to the system PATH. This will allow installation of different Python versions without creating conflicts with existing installed versions. To use the script, enter the desired Python version X.XX as shown below, where X.XX represents the verison e.g. 3.13

```
scripts/mac/install_python <X.XX>
```

Once the Python version has been installed, a virtual environment can be created using the Python version as above and a name for the environment. If some other existing Python installation is being used, please refer to the instructions for that installation to create the virtual environment.

```
scripts/mac/create_venv <X.XX> <env_name>
```

### Activate the Virtual Environment
---

To activate the environment

```
source <env_name>/bin/activate
```

&nbsp;

### Select Desired Library Type and Set Up Project
---

<details><summary><b>Homebrew Library Installation</b></summary>

&nbsp;

### Install the Dependency Libraries and CMake

```
brew update
brew upgrade
brew install cmake ninja
brew tap homebrew-ffmpeg/ffmpeg
brew install homebrew-ffmpeg/ffmpeg/ffmpeg
```

<i>Please note that the standard Homebrew core ffmpeg version is incompatible with this project. For this reason, the install procedure calls for the 3rd party tap homebrew-ffmpeg. If you already have another version of ffmpeg installed, this will create a conflict. In order to install this version, it is necessary to run</i> ```brew uninstall ffmpeg``` <i>before this tap can be installed.</i>


### Compile and Run the Program

```
pip install -v .
wabash
```

---

&nbsp;

</details>

<details><summary><b>Portable Library Installation</b></summary>

&nbsp;

### Building Portable Libraries on a Virtual Machine
---

Similar to the Linux environment, Mac programs require special consideration in order to be portable to an arbitrary machine. Dependency libraries should be compiled in a virtual machine using an older operating system for maximum compatibility. A good choice for creating virtual machines is [UTM](https://mac.getutm.app). 

An OS image is needed to create the virtual machine. By default, UTM will atomatically download the latest Mac OS for your machine. However, using an older Mac OS image has the benefit of greater compatability with other machines. Older images can be downloaded from [ipsw.me](https://ipsw.me/product/mac#google_vignette). Experimentation may be required to discover the oldest possible version of compatible OS, those within the same development family can be expected to have the greatest compatibility. Starting with an early version of the Sequoia Operating System as a starting point is suggested.

### Create the Virtual Machine
---

Install UTM and create a virtual machine using an OS image, setting a memory size and CPU count appropriate for the host computer. Add a shared directory so that files can be transferred to and from the virtual machine, which can be done on the last screen shown before the virtual machine creation starts. Inside the virtual machine, there will be a Shared Directory folder on the sidebar of the Finder app. Note that the Shared Directory will only show files that were present on the host at the time the virtual machine was started.

### Project Configuration on the Virtual Machine
---

The virtual machine requires Xcode command line tools to compile the project.

```
xcode-select --install
```

Following the installation of Xcode tools, download the repository using git and change the working directory to the project directory.

```
git clone https://github.com/sr99622/wabash
cd wabash
```

### Install Prerequisites
---

Several tools are needed to compile the libraries. The following script will install Homebrew which is then used to install the necessary tools after sourcing the .zprofile to enable brew environment variables.

```
scripts/mac/install_brew
source $HOME/.zprofile
brew install wget automake nasm libtool pkgconfig ninja
```

### Install Python
---

A Python version greater than or equal to 3.10 and less than or equal to 3.13 with the ability to create virtual environments is required. A script is included to install Python from the official site without adding it to the system PATH. This will allow installation of different Python versions without creating conflicts with existing installed versions. To use the script, enter the desired Python version X.XX as shown below, where X.XX represents the verison e.g. 3.13

```
scripts/mac/install_python <X.XX>
```

Once the Python version has been installed, a virtual environment can be created using the Python version as above and a name for the environment.

```
scripts/mac/create_venv <X.XX> <env_name>
```

To activate the environment

```
source <env_name>/bin/activate
```

### Compile the Project
---

The following script will compile the dependency libraries and install them to a local subdirectory named ```build``` in the project folder. The dependency libraries will then be used during compilation of the Python module which is installed into the virtual environment and scanned using the ```otool``` utility to recursively enumerate all dependencies. 

During the ```otool``` scan, system libraries are ignored as they are provided by default in the Operating System. This has implications for the choice of Operating System under which the compilation is performed, in the sense that older Operating Systems can be expected to be forward compatible within their family so that older software can be used on newer systems. 

Once a list of dependencies has been collected, the dependency files themselves are manipulated using the ```install_name_tool``` utility to change the loader headers in the binary files such that the loader can be invoked in a portable manner. The binary file header and dependency links are changed to display ```@loader_path``` as their location, which gives the consuming executable the ability to invoke the dependency from within its local directory.

Following manipulation of the binary file headers, the project is re-compiled with the new loader path settings to bake in the changes. The modified binaries are copied to the project Python staging area, in this case the ```wabash``` subdirectory, so that they will be installed along side the Python module executable in the virtual environment. This configuration allows arbitrary machines to install the Python module and it's dependencies in a portable way such that the Python module can run on the target machine without the requirement to pre-install those dependencies.

Additionally, the script will populate the ```stock``` subdirectory with portable versions of the dependencies for use in project development. The ```stock``` subdirectory can be copied to a develpment machine to facilitate compilation of the project with portable libraries.

```
scripts/mac/make_module
```

The products of this script are

* a working version of the Python module in the current virtual environment 
* an installation wheel that can be found in the ```dist``` subdirectory
* a ```stock``` subdirectory containing portable libraries with include headers

### Test the Build
---

```
wabash
```

### Test the Python Wheel
---

The installation wheel can be tested by creating a new virtual environment and installing it there. The new installation will be self sufficient and contains its own compiled dependency libraries. In the following script, use the same Python version X.XX as the virtual environment used to compile the wheel. If there is an existing virtual environment in effect, it should be deactivated first before conducting the test.

```
deactivate
scripts/mac/create_venv X.XX test_env
source test_env/bin/activate
pip install dist/*.whl
wabash
```

### Transfer Portable Libraries to Development Host
---

Copying the Portable libraries to the Host will depend on the location of the Shared directory set up in the UTM virtual machine configuration. The default case is "My Shared Files/Documents", which corresponds to the Documents folder of the Host machine. From within the virtual machine, copy the ```stock``` folder from the project directory to this location, then from the Host machine, copy that folder to the local copy of the project directory. The top level directory structure of the project should look something like

```
wabash
    assets
    cmake
    include
    scripts
    src
    stock
    wabash
    ...
```

### Compile the Module on the Development Host
---

The virtual machine is no longer needed and can be shut down. The following assumes that the development machine has been configured as described above in the Project Configuration section. It assumes further that the virtual environment described there has been activated and the current working directory is the project directory.

```
scripts/mac/compile
wabash
```

### Building an Installer Image
---

Using portable dependencies will facilitate the creation of an installable DMG app image of the program. Additionally, there are some requirements for the DMG app image in order for it to pass Apple security screening such that it can be installed on a target machine with minimal disruption. It will need to be codesigned with the Devloper's keychain and notarized on the Apple server which requires a Developer Account and Certificate. This is a process that involves some complex steps, so a helper application is recommended. [DMG Canvas](https://www.araelium.com/dmgcanvas) is one such app that has been used successfully. An excellent resource for helping to understand this process can be found at [Xojo](https://blog.xojo.com/2024/08/22/macos-apps-from-sandboxing-to-notarization-the-basics/).

The first step in this process is to build the app on the development machine. The following script will perform this build. Please note that the script should not be run from inside a virtual environment, it will be looking for it's own version of Python.

```
deactivate
scripts/mac/make_app
```

The script will compile Python and OpenSSL along with some supporting libraries into the /Applications/wabash.app folder, then it will use it's local pip version to install the necessary components into it's own local virtual environment. A compiled launcher executable is needed for the application as well and will be built and installed into the local folder. Upon completion of the script, a working version of the program should be visible in the Applications folder. Please note that if the program is launched from this location, it can no longer be used for notarization, as it will create artifacts that pollute the codesigned file structure.

Once the app has been assembled in situ, the DMG Canvas application is used to build the DMG file and notarize it on the Apple Developer site. A valid developer subscription and certificate are required for this operation. If the app has been previously launched as discussed above, the notarization will fail, so it is necessary to assemble the DMG image from a virgin /Applications/wabash.app folder. 

</details>

&nbsp;

### Development of the Project
---
Project development may include efforts in both Python and C++. There are different methods for observing changes made to the program in these two domains. Furthermore, there is a difference in the compilation procedure for the C++ domain depending on whether the dependency libaries have been installed using the package manager or the portable libraries.

### Developing Python Code
---

To develop the Python domain of the program, it is necessary to uninstall the wabash python module from the current environment. This is required because the python code will look for the module in the environment first, which has the effect of ignoring changes made to the python source code. The following assumes that the python environment has been activated like `source <env_name>/bin/activate`. 

To develop the Python code and observe changes made, use the following.

```
pip uninstall wabash
python run.py
```

### Developing C++ Code
---

Any changes made in the C++ domain require re-compiling the project in order to be observed. Note that the compile process will install a copy of the Python module binary into the local wabash directory. This enables local development when the Python module is un-installed from the current environment. The binary filename is prefixed with an underscore, which is namespace translated by `__init__.py`. If the portable libraries are being used, the dependency binaries will also be present in the wabash directory.

To develop C++ code using the portable libraries

```
scripts/mac/compile
env/bin/wabash
```

To develop C++ code using the Homebrew libraries

```
pip install -v .
env/bin/wabash
```

</details>

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

