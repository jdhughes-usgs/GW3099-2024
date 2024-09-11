# # U.S. Geological Survey Class GW3099
#
# Advanced Modeling of Groundwater Flow (GW3099) <br>
# Boise, Idaho <br>
# September 16 - 20, 2024 <br>

# # ![title](../../images/ClassLocation.jpg)

# # PRT example 1: backwards tracking in steady flow field

# ![title](../../images/ex-prt-mp7-p01-config.png)

import pathlib as pl
import flopy
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyvista as pv
import warnings
from flopy.export.vtk import Vtk
from flopy.utils.gridgen import Gridgen
from flopy.utils.gridintersect import GridIntersect
from flopy.discretization import VertexGrid
from flopy.utils.triangle import Triangle as Triangle
from flopy.utils.voronoi import VoronoiGrid
from shapely.geometry import LineString, Point, MultiPoint, Polygon
from matplotlib import colormaps as cm

# Ignore some warnings.

warnings.simplefilter("ignore", UserWarning)
warnings.simplefilter("ignore", DeprecationWarning)

# Make sure executables are installed.

flopy.utils.get_modflow(":python", subset="mf6,mp7,gridgen,triangle")

# Create a workspace.

example_name = "prt_mp7_ex2"
base_ws = pl.Path("temp") / example_name
base_ws.mkdir(exist_ok=True)

## A
#
# Define the groundwater flow
 
# Define the model name and workspace.

gwf_name = f"{example_name}-gwf"
gwf_ws = base_ws / "gwf"
gwf_ws.mkdir(exist_ok=True, parents=True)

# Define model units.

length_units = "feet"
time_units = "days"

# Define model parameters.

nper = 1  # Number of periods
nlay = 3  # Number of layers (base grid)
nrow = 21  # Number of rows (base grid)
ncol = 20  # Number of columns (base grid)
delr = 500.0  # Column width ($ft$)
delc = 500.0  # Row width ($ft$)
top = 400.0  # Top of the model ($ft$)
botm = [220.0, 200.0, 0.0]  # Layer bottom elevations ($ft$)
porosity = 0.1  # Soil porosity (unitless)
rrch = 0.005  # Recharge rate ($ft/d$)
kh = [50.0, 0.01, 200.0]  # Horizontal hydraulic conductivity ($ft/d$)
kv = [10.0, 0.01, 20.0]  # Vertical hydraulic conductivity ($ft/d$)
wel_q = -150000.0  # Well pumping rate ($ft^3/d$)
riv_h = 320.0  # River stage ($ft$)
riv_z = 317.0  # River bottom ($ft$)
riv_c = 1.0e5  # River conductance ($ft^2/d$)

# Define the grid discretization.

Lx = 10000.0
Ly = 10500.0
nlay = 3
nrow = 21
ncol = 20
delr = Lx / ncol
delc = Ly / nrow
top = 400
botm = [220, 200, 0]

# Define the time discretization.

nstp = 1
perlen = 1000.0
tsmult = 1.0
tdis_rc = [(perlen, nstp, tsmult)]

# Construct a simulation for the flow model.

sim = flopy.mf6.MFSimulation(
    sim_name=gwf_name, exe_name="mf6", version="mf6", sim_ws=gwf_ws
)

# Create the time discretization.

tdis = flopy.mf6.ModflowTdis(
    sim, pname="tdis", time_units="DAYS", perioddata=tdis_rc, nper=len(tdis_rc)
)

# Create the flow model.

gwf = flopy.mf6.ModflowGwf(
    sim, modelname=gwf_name, model_nam_file="{}.nam".format(gwf_name)
)
gwf.name_file.save_flows = True

# Create the discretization package.

dis = flopy.mf6.ModflowGwfdis(
    gwf,
    length_units=length_units,
    nlay=nlay,
    nrow=nrow,
    ncol=ncol,
    delr=delr,
    delc=delc,
    top=top,
    botm=botm
)

# Create the initial conditions package.

ic = flopy.mf6.ModflowGwfic(gwf, pname="ic", strt=riv_h)  # initial heads at river stage

# Create the node property flow package.

npf = flopy.mf6.ModflowGwfnpf(
    gwf,
    xt3doptions=[("xt3d")],
    icelltype=[1, 0, 0],
    k=kh,
    k33=kv,
    save_saturation=True,
    save_specific_discharge=True,
)

# Define the model's boundary conditions. These include a well, a river, and recharge. Instead of manually setting cell IDs for the well and river, we will determine cell IDs by defining boundary coordinates and intersecting them with the grid.

# Create intersection object.

ix = GridIntersect(gwf.modelgrid, method="vertex", rtree=True)

# Create the well package.

wel_coords = [(4718.45, 5281.25)]
welcells = ix.intersects(MultiPoint(wel_coords))
welcells = [icpl for (icpl,) in welcells]
welspd = [[(2, icpl), -150000.0] for icpl in welcells]
wel = flopy.mf6.ModflowGwfwel(gwf, print_input=True, stress_period_data=welspd)

# Create the river package.

riv_iface = 6
riv_iflowface = -1
riverline = [(Lx - 1.0, Ly), (Lx - 1.0, 0.0)]
rivcells = ix.intersects(LineString(riverline))
rivcells = [icpl for (icpl,) in rivcells]
rivspd = [
    [(0, icpl), riv_h, riv_c, riv_z, riv_iface, riv_iflowface] for icpl in rivcells
]
riv = flopy.mf6.ModflowGwfriv(
    gwf, stress_period_data=rivspd, auxiliary=[("iface", "iflowface")]
)

# Create the recharge package.

rch_iface = 6
rch_iflowface = -1
rch = flopy.mf6.ModflowGwfrcha(
    gwf,
    recharge=rrch,
    auxiliary=["iface", "iflowface"],
    aux=[rch_iface, rch_iflowface],
)

# Create the output control package.

headfile_name = "{}.hds".format(gwf_name)
budgetfile_name = "{}.cbb".format(gwf_name)
oc = flopy.mf6.ModflowGwfoc(
    gwf,
    pname="oc",
    budget_filerecord=[budgetfile_name],
    head_filerecord=[headfile_name],
    headprintrecord=[("COLUMNS", 10, "WIDTH", 15, "DIGITS", 6, "GENERAL")],
    saverecord=[("HEAD", "ALL"), ("BUDGET", "ALL")],
    printrecord=[("HEAD", "ALL"), ("BUDGET", "ALL")],
)

# Create the iterative model solution (IMS) package and register it with the model.

ims = flopy.mf6.ModflowIms(
    sim,
    pname="ims",
    outer_dvclose=1.0e-5,
    outer_maximum=100,
    under_relaxation="NONE",
    inner_maximum=100,
    inner_dvclose=1.0e-6,
    rcloserecord=0.1,
    linear_acceleration="BICGSTAB",
    scaling_method="NONE",
    reordering_method="NONE",
    relaxation_factor=0.99,
)
sim.register_ims_package(ims, [gwf.name])

# Write and run the flow model.

sim.write_simulation(silent=False)
sim.run_simulation(silent=False)






# Create a "dummy" discretization
ms = flopy.modflow.Modflow()
dis = flopy.modflow.ModflowDis(
    ms,
    nlay=nlay,
    nrow=nrow,
    ncol=ncol,
    delr=delr,
    delc=delc,
    top=top,
    botm=botm,
)

# Create gridgen workspace and object
gridgen_ws = base_ws / "gridgen"
gridgen_ws.mkdir(parents=True, exist_ok=True)
gridgen = Gridgen(ms.modelgrid, model_ws=gridgen_ws)

# Define refinement polygons
ref_polys = [
    [[(3500, 4000), (3500, 6500), (6000, 6500), (6000, 4000), (3500, 4000)]],  # outer
    [[(4000, 4500), (4000, 6000), (5500, 6000), (5500, 4500), (4000, 4500)]],  # middle
    [[(4500, 5000), (4500, 5500), (5000, 5500), (5000, 5000), (4500, 5000)]],  # inner
]
ref_paths = []
for i, poly in enumerate(ref_polys):
    gridgen.add_refinement_features([poly], "polygon", i + 1, range(nlay))
    ref_paths.append(gridgen_ws / f"rf{i}")