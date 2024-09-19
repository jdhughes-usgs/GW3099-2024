# A few functions to get data ready for setting up DISU model grid
import flopy.discretization as fgrid
import numpy as np


def dis_mult(thk, nlay, dis_mult):
    lay_elv = thk * ((dis_mult - 1) / (dis_mult**nlay - 1))
    return lay_elv


def flatten(xss):
    return [x for xs in xss for x in xs]


def set_connectiondata(
    n, lay, top, left, right, bottom, top_overburden, botm, ncol, delr, delc
):
    # Instatiate empty lists
    jas = [n]
    ihc = [lay]
    cl12 = [n]
    hwva = [n]
    angldeg = [360.0]

    # Calculate half-cell thickness up front for vertical connections
    if lay == 0:
        cl12_val = (top_overburden - botm[lay]) / 2
    else:
        cl12_val = (botm[lay - 1] - botm[lay]) / 2

    if top:
        jas.append(n - ncol)
        ihc.append(0)  # ihc = 0 for vertical connection
        cl12.append(
            cl12_val
        )  # half the cell thickness or a vertical connection
        hwva.append(
            delr * delc
        )  # for vertical connection, area is delr * delc
        angldeg.append(0.0)  # placeholder only for vertical connections

    if left:
        jas.append(n - 1)  # left
        ihc.append(delc)  # ihc = 1 for horizontal connection
        cl12.append(
            delr / 2
        )  # half the cell width along a horizontal connection
        hwva.append(
            delc
        )  # for horizontal connection, value of hwva is width along a row
        angldeg.append(
            180.0
        )  # for horizontal connection, value is 180.0 along negative x-axis

    if right:
        jas.append(n + 1)  # right
        ihc.append(delc)  # ihc = 1 for horizontal connection
        cl12.append(
            delr / 2
        )  # half the cell width along a horizontal connection
        hwva.append(
            delc
        )  # for horizontal connection, value of hwva is width along a row
        angldeg.append(
            0.0
        )  # for horizontal connection, value is 0.0 along positive x-axis

    if bottom:
        jas.append(n + ncol)  # below
        ihc.append(0)  # ihc = 0 for vertical connection
        cl12.append(
            cl12_val
        )  # half the cell thickness or a vertical connection
        hwva.append(
            delr * delc
        )  # for vertical connection, value of hwva is area
        angldeg.append(0.0)  # placeholder only for vertical connections

    return jas, ihc, cl12, hwva, angldeg


def get_conndat(n, lay, col, nlay, top_overburden, botm, ncol, delr, delc):
    top = False
    left = False
    right = False
    bottom = False

    # iac is the number of connections (plus 1) for each cell
    iac = 1  # start with the "plus 1"

    if lay == 0:
        # For upper-most layer, only connection cell underneath it
        iac += 1
        # Bottom
        bottom = True

    elif lay <= 99:
        # For layers 2-100, connections fixed at 2 (above and below)
        iac += 2
        # Above
        top = True
        # Bottom
        bottom = True

    elif lay > 99:
        # Layer 100 is the upper most layer in the gw reservoir and where
        # horizontal connections start
        iac += 2
        if col == 0:
            # In addition to vertical connections, include 1 horizontal connecion
            # (horizontal connection will be to the right only in this case)
            iac += 1
            # Above
            top = True
            # Right
            right = True
            # Bottom
            bottom = True

        elif col == ncol - 1:
            # Horizontal connection will be to the left only
            iac += 1
            # Above
            top = True
            # Left
            left = True
            # Below
            bottom = True

        else:
            # If interior column, there will be two horizontal connections
            iac += 2
            # Above
            top = True
            # Left
            left = True
            # Right
            right = True
            # Below
            bottom = True

    jas_vals, ihc_vals, cl12_vals, hwva_vals, angldeg_vals = (
        set_connectiondata(
            n,
            lay,
            top,
            left,
            right,
            bottom,
            top_overburden,
            botm,
            ncol,
            delr,
            delc,
        )
    )

    # If bottom most layer, need to .pop() the last values out of the respective lists
    # This should be done because the bottom connections will always be represented by the final
    # values in the list (at this point in the development anyway)
    if lay == nlay - 1:
        iac -= 1
        jas_vals.pop(-1)
        ihc_vals.pop(-1)
        cl12_vals.pop(-1)
        hwva_vals.pop(-1)
        angldeg_vals.pop(-1)

    return iac, jas_vals, ihc_vals, cl12_vals, hwva_vals, angldeg_vals


def filter_nodes(xvc, yvc, iv, xv, yv):
    # Check if iv is empty
    if iv:
        vert_id = max(iv)

        # Add nodes represented by xvc and yvc if not already contained in xv, yv
        for new_pair in zip(xvc, yvc):
            found = False
            for old_pair in zip(xv, yv):
                if old_pair[0] == new_pair[0] and old_pair[1] == new_pair[1]:
                    found = True
                    break

            if not found:
                # if not already present, add the vertex
                iv.append(vert_id + 1)
                vert_id += 1
                xv.append(new_pair[0])
                yv.append(new_pair[1])

    else:
        iv.extend(list(range(0, 4)))
        xv.extend(xvc)
        yv.extend(yvc)

    return iv, xv, yv


def populate_linked_IDs(xvc, yvc, xv, yv):
    # Ensure 4 items contained in the passed list of nodes to get positional IDs for
    assert len(xvc) == 4, "Number of processed vertices is off"

    vertices = []
    for pair in zip(xvc, yvc):  # xvc should have 4 items
        for i, existing_pair in enumerate(zip(xv, yv)):
            if existing_pair[0] == pair[0] and existing_pair[1] == pair[1]:
                vertices.append(i)
                break

    assert len(vertices) == 4, "Number of vertices should be 4"
    return vertices


def buildout_vertex_locations(nlay, ncol, delr):
    n = -1
    cell_vert_lkup = {}
    # Only need 1 layer's worth of vertices since they can be repeated
    iv = []
    xv = []
    yv = []

    ly = 0
    for j in np.arange(ncol):
        # There are two X locations (leverages the fact that delr = 1.0)
        vert_left = float(j * delr)
        vert_right = vert_left + delr
        # There are two Y locations (only 1 row with unit width)
        vert_front = 0.0
        vert_back = 1.0

        # First define each vertex for the cell in the current column
        if ly == 0:
            # left, back
            xvc = [vert_left]
            yvc = [vert_back]
            # right, back
            xvc.append(vert_right)
            yvc.append(vert_back)
            # right, front
            xvc.append(vert_right)
            yvc.append(vert_front)
            # left, front
            xvc.append(vert_left)
            yvc.append(vert_front)

        # Second, only keep vertices that don't already appear in the respective lists
        iv, xv, yv = filter_nodes(xvc, yvc, iv, xv, yv)

        # Store dictionary entry linking cell ID with its vertices
        vertices = populate_linked_IDs(xvc, yvc, xv, yv)
        n += 1
        cell_vert_lkup[n] = vertices

    # Now loop for the remaining layers
    for j in np.arange(ncol):
        # Only need to find the top layer's vertices once
        verts_to_use = cell_vert_lkup[j]
        for ly in np.arange(1, nlay):
            n = (ly * ncol) + j
            cell_vert_lkup[n] = verts_to_use

    return iv, xv, yv, cell_vert_lkup


def append_cell2d(n, xv_lst, yv_lst, cell_vert_lkup, ncol, delr, delc):
    # Get the vertex IDs for the current cell

    # Start with calculating the x location of the cell
    col_id = n % ncol
    cell_x = delr / 2 + col_id * delr
    # The y location of the cell is fixed at delc/2
    cell_y = delc / 2

    # Get associated vertices
    vertices = cell_vert_lkup[n]

    # Every cell will have 4 vertices
    new_cell2d = [[n, cell_x, cell_y, 4], vertices]

    # Flatten
    new_cell2d = flatten(new_cell2d)

    return new_cell2d


def gen_faux_grid(nrow, ncol, delr, delc, top_overburden, botm):
    # Mimicking DISU grid with a DIS grid. DISU plotting is much
    # too slow for whatever reason.
    delc_local = delc * np.ones(nrow)
    delr_local = delr * np.ones(ncol)
    top_overburden_local = top_overburden * np.ones((nrow, ncol))
    botm_local = []
    for bot in botm:
        bot_arr = bot * np.ones((nrow, ncol))
        botm_local.append(bot_arr)

    botm_local = np.array(botm_local)

    sgr = fgrid.StructuredGrid(
        delc_local,
        delr_local,
        top=top_overburden_local,
        botm=botm_local,
        xoff=0.0,
        yoff=0.0,
        angrot=0.0,
    )

    return sgr
