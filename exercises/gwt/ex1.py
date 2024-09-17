import flopy
import numpy as np


def block_wave_constant(x, t, v):
    x_wave_start = 0
    x_wave_end = x_wave_start + v * t
    return np.where((x < x_wave_start) | (x > x_wave_end), 0, 1)


def get_ex1_sim(workspace, dx=10.0, dt=20.0, advscheme="upstream"):
    # validate
    advscheme = advscheme.lower()
    if advscheme not in ["upstream", "central", "tvd"]:
        raise ValueError("advscheme must be 'upstream', 'central', or 'tvd'")

    # Model units
    length_units = "meters"
    time_units = "days"

    # spatial dimensions
    delr = dx  # Column width ($m$)
    Lx = 1000.0  # Length of domain
    ncol = int(Lx / delr)  # Number of columns
    nlay = 1  # Number of layers
    nrow = 1  # Number of rows
    delc = 1.0  # Row width ($m$)
    top = 0.0  # Top of the model ($m$)
    botm = -1.0  # Layer bottom elevations ($m$)

    # Time discretization
    perlen = 2000.0  # Simulation time ($days$)
    nstp = int(perlen / dt)  # Number of time steps
    tdis_rc = [(perlen, nstp, 1.0)]
    nper = len(tdis_rc)  # number of periods

    # Model parameters
    porosity = 0.25  # Porosity
    k11 = 1.0  # Horizontal hydraulic conductivity ($m/d$)

    # Set velocity so that front reaches Lx/2 at time=perlen
    v = Lx / 2.0 / perlen

    # Calculate the required flow rate for this velocity
    Q = v * (delc * (top - botm)) * porosity

    # Set some static model parameter values
    strt = np.zeros((nlay, nrow, ncol), dtype=float)  # Starting head ($m$)
    icelltype = 1  # Cell conversion type

    # Set starting concentration
    sconc = np.zeros((nlay, nrow, ncol), dtype=float)

    # Set solver parameter values (and related)
    nouter, ninner = 100, 300
    hclose, rclose, relax = 1e-6, 1e-6, 1.0

    # Well on left, constant head on right
    chdspd = [[(0, 0, ncol - 1), 0.0]]
    welspd = [[(0, 0, 0), Q, 1.0]]

    # Constant concentration on left side of model
    cncspd = [[(0, 0, 0), 1.0]]

    # MODFLOW 6
    name = "ex1"
    gwfname = "gwf-" + name
    sim_ws = workspace
    sim = flopy.mf6.MFSimulation(sim_name=name, sim_ws=sim_ws, exe_name="mf6")

    # Time discretization
    flopy.mf6.ModflowTdis(
        sim, nper=nper, perioddata=tdis_rc, time_units=time_units
    )

    # Groundwater flow model
    gwf = flopy.mf6.ModflowGwf(
        sim,
        modelname=gwfname,
        save_flows=True,
    )

    # Solver for flow model
    imsgwf = flopy.mf6.ModflowIms(
        sim,
        print_option="SUMMARY",
        outer_dvclose=hclose,
        outer_maximum=nouter,
        under_relaxation="NONE",
        inner_maximum=ninner,
        inner_dvclose=hclose,
        rcloserecord=rclose,
        linear_acceleration="CG",
        scaling_method="NONE",
        reordering_method="NONE",
        relaxation_factor=relax,
        filename=f"{gwfname}.ims",
    )
    sim.register_ims_package(imsgwf, [gwf.name])

    # Discretization package
    flopy.mf6.ModflowGwfdis(
        gwf,
        length_units=length_units,
        nlay=nlay,
        nrow=nrow,
        ncol=ncol,
        delr=delr,
        delc=delc,
        top=top,
        botm=botm,
        idomain=np.ones((nlay, nrow, ncol), dtype=int),
    )

    # Node-property flow package
    flopy.mf6.ModflowGwfnpf(
        gwf,
        save_flows=False,
        icelltype=icelltype,
        k=k11,
        save_specific_discharge=True,
    )

    # Initial conditions package for flow model
    flopy.mf6.ModflowGwfic(gwf, strt=strt)

    # Constant head package
    flopy.mf6.ModflowGwfchd(
        gwf,
        maxbound=len(chdspd),
        stress_period_data=chdspd,
        save_flows=False,
        pname="CHD-1",
    )

    # Well package
    flopy.mf6.ModflowGwfwel(
        gwf,
        maxbound=len(welspd),
        stress_period_data=welspd,
        save_flows=False,
        auxiliary=["concentration"],
        pname="WEL-1",
    )

    # Output control package for flow model
    flopy.mf6.ModflowGwfoc(
        gwf,
        head_filerecord=f"{gwfname}.hds",
        budget_filerecord=f"{gwfname}.cbc",
        headprintrecord=[("COLUMNS", 10, "WIDTH", 15, "DIGITS", 6, "GENERAL")],
        saverecord=[("HEAD", "LAST"), ("BUDGET", "LAST")],
        printrecord=[("HEAD", "LAST"), ("BUDGET", "LAST")],
    )

    # Groundwater transport package
    gwtname = "gwt-" + name
    gwt = flopy.mf6.MFModel(
        sim,
        model_type="gwt6",
        modelname=gwtname,
    )
    gwt.name_file.save_flows = True
    imsgwt = flopy.mf6.ModflowIms(
        sim,
        print_option="SUMMARY",
        outer_dvclose=hclose,
        outer_maximum=nouter,
        under_relaxation="NONE",
        inner_maximum=ninner,
        inner_dvclose=hclose,
        rcloserecord=rclose,
        linear_acceleration="BICGSTAB",
        scaling_method="NONE",
        reordering_method="NONE",
        relaxation_factor=relax,
        filename=f"{gwtname}.ims",
    )
    sim.register_ims_package(imsgwt, [gwt.name])

    # Transport discretization package
    flopy.mf6.ModflowGwtdis(
        gwt,
        nlay=nlay,
        nrow=nrow,
        ncol=ncol,
        delr=delr,
        delc=delc,
        top=top,
        botm=botm,
        idomain=1,
    )

    # Transport initial concentrations
    flopy.mf6.ModflowGwtic(gwt, strt=sconc)

    # Transport advection package
    flopy.mf6.ModflowGwtadv(gwt, scheme=advscheme)

    # Transport mass storage package
    flopy.mf6.ModflowGwtmst(
        gwt,
        porosity=porosity,
    )

    # Transport source-sink mixing package
    sourcerecarray = [("WEL-1", "AUX", "CONCENTRATION")]
    ssm = flopy.mf6.ModflowGwtssm(
        gwt,
        print_flows=True,
        sources=sourcerecarray,
    )

    # Transport output control package
    flopy.mf6.ModflowGwtoc(
        gwt,
        budget_filerecord=f"{gwtname}.cbc",
        concentration_filerecord=f"{gwtname}.ucn",
        concentrationprintrecord=[
            ("COLUMNS", 10, "WIDTH", 15, "DIGITS", 6, "GENERAL")
        ],
        saverecord=[("CONCENTRATION", "ALL"), ("BUDGET", "LAST")],
        printrecord=[("CONCENTRATION", "LAST"), ("BUDGET", "LAST")],
    )

    # Flow-transport exchange
    flopy.mf6.ModflowGwfgwt(
        sim,
        exgtype="GWF6-GWT6",
        exgmnamea=gwfname,
        exgmnameb=gwtname,
        filename=f"{name}.gwfgwt",
    )

    return sim
