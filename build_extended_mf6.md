# Building the Extended Version of MODFLOW 6

These are the instructions for obtaining the MODFLOW 6 source code and building the extended version of MODFLOW 6. Note that requires adding additional dependencies to the `environment.yml` file described on the [software](./SOFTWARE.md) page.

## Step 1. Activate your `gw3099` Conda Environment

Activate the `gw3099` environment:

```
conda activate gwf3099
```

## Step 2. Update the `gw3099` environment

Using a text editor, create a file called `update_pc_files.py`. It should contain the information in [this python script file](.scripts/update_pc_files.py). Save this file to your hard drive in the directory where you activated the `gw3099` environment in the previous step.

Run the python script using:

```python
python update_pc_files.py
```


## Step 3. Clone the modflow6 repository from GitHub
The following command can be used to clone the modflow6 repository.

```
git clone https://github.com/MODFLOW-USGS/modflow6.git
```

This will download the repository and create a new folder called `modflow6` in the working directory.

## Step 4. Build MODFLOW

To build the extended version of MODFLOW, simply run the following commands from a terminal.

```
cd modflow6
```

```
meson setup builddir -Ddebug=false -Dextended=true --prefix=$CONDA_PREFIX --libdir=bin
```

```
meson install -C builddir
```

```
meson test --verbose --no-rebuild -C builddir
```

If everything is working properly, then the last command should show that the tests completed ok and without errors. The message should look something like the following:

```
――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――
5/5 Parallel simulation test - 2 cores OK 0.20s
 
 
Ok: 5
Expected Fail: 0
Fail: 0
Unexpected Pass: 0
Skipped: 0
Timeout: 0
 
Full log written to /Users/runner/work/GW3099-2024/GW3099-2024/modflow6/builddir/meson-logs/testlog.txt has context menu
```
