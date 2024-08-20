# Software Installation
To get the most out of this class, you will need to come prepared with a laptop computer that has Python installed. **If you are familiar with conda environments and know how to create a new conda environment using an environment.yml file, then skip ahead to Part 2**. For all others, we recommend using the Miniforge software to download and install Python and required dependencies needed for the class. 

The following instructions will guide you through the installation process and setup of a mfandmore2024 environment.

## Part 1 -- Install Miniforge
1. Go to the miniforge website and download the installer (https://github.com/conda-forge/miniforge) for your platform.

2. Run the installer program that you downloaded. On Windows the installer is called `Miniforge3-Windows-x86_64.exe`.

3. Click through the installer options, and select "Just Me (recommended)" if asked. Default installation options should be fine, with the exception that you should select an installation location that does not have any special characters or spaces in it.

4. After installation, you should see "Miniforge Prompt" as a program under the Windows Start menu.

## Part 2 -- Create an Environment File
We will use an environment file to create a containerized version of Python and the Python packages needed for the class. An environment file is simply a list of packages that we want to install in our environment.

1. Using a text editor, such as Notepad or Notepad++, create a file called `environment.yml`. It should contain the information in [this environment file](./environment.yml). Save this file to your hard drive, preferably in your user home folder so that it can be easily accessed in the next step. (Caution!  Notepad will automatically append a .txt suffix to your file name; you don't want this to happen.)

2. **For MacOS and Linux users only!** You will need to add seven additional dependencies to the `environment.yml` file from step 1. The following dependencies are also required: 

   **MacOS**
   ```
   - pkg-config
   - openmpi<5.0.0
   - gfortran
   - petsc
   - netcdf-fortran
   - meson>=1.1.0
   - ninja
   ```  

   **Linux**
   ```
   - pkg-config
   - openmpi
   - gfortran
   - petsc
   - netcdf-fortran
   - meson>=1.1.0
   - ninja
   ```  


## Part 3. Create the `gw3099` Environment

1. Start the miniforge prompt from the Windows start menu (or equivalent on MacOS or Linux) to bring up a terminal.

2. At the terminal prompt enter the following command, where `<path to file>` is the location of the `environment.yml` file that you created in Part 2. You will need to be connected to the internet for this to work properly. The installation process may take a couple of minutes.
    ```
    mamba env create --file <path to file>/environment.yml
    ```

    **If you installing the class environment in an existing python distribution, you will need to use the** `conda` **command if** `mamba` **is not installed.**


3. After the environment has been installed, you may activate this new class environment with the following command
    ```
    mamba activate gw3099
    ```

4. The windows terminal prompt should reflect the current environment:
    ```
    (gw3099) C:\Users\JaneDoe>
    ```

5. We will be using jupyter notebooks in the class. To test if jupyter is installed and working properly use the following command. After entering this command, the default web browser should open to a Jupyter Lab page.
    ```
    jupyter lab
    ```

For most users, the setup is complete at this point. For those working on a MacOS or Linux laptop, please proceed to Part 4.


## Part 4. Obtaining MODFLOW 6

We will be using the extended version of MODFLOW 6 in this class. If you are working on Windows, we will be using the latest nightly-build of the extended version of [MODFLOW 6](https://github.com/MODFLOW-USGS/modflow6-nightly-build/releases) in the class. We will also walk through this step during the class. The distribution file for Windows that includes the extended version is called `win64xtd.zip`.

If you are using a MacOS or Linux laptop for the class, then you will need to build the extended version of MODFLOW. We have simplified the build process, which can be completed in just a few minutes. Instructions for building the extended version of MODFLOW 6 are located [here](./build_extended_mf6.md).


# Preparation for the Class
If you have never used Python before, there are many online resources for getting started. A recommendation is to start with the tutorial at https://cscircles.cemc.uwaterloo.ca/.


# If Software Installation Fails

Contact jdhughes@usgs.gov
