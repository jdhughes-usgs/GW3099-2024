# Some functions for calculating the Barends analytical solution
import math

import numpy as np
from scipy.integrate import quad


def barends_eqn4(sigma, x, z, t, v, H, h_prime, D, D_prime):
    exponent = -((sigma - x * v / (4 * D * sigma)) ** 2)
    term1 = math.exp(exponent)
    term2 = x**2 * h_prime * math.sqrt(D_prime) / (8 * D * H * sigma**2)
    term3 = z / (2 * math.sqrt(D_prime))
    term4 = t - x**2 / (4 * D * sigma**2)

    # put it all together
    eqn4_val = term1 * math.erfc((term2 + term3) * (term4) ** (-0.5))

    return eqn4_val


def calc_analytical_sln(
    times, X, x_mids, z_mids, T0, T1, D, D_prime, v, H, h_prime
):
    # Remember X, Y are output from MeshGrid
    myarr = np.zeros((len(times), X.shape[0], X.shape[1]))
    integral_rslt = np.zeros_like(myarr)
    prefix_rslt = np.zeros_like(myarr)
    for t_idx, t in enumerate(times):
        for k, z in enumerate(z_mids):  # rows (which are effectively z)
            for j, x in enumerate(x_mids):  # columns (which are effectively x)
                lower_lim = x / (2 * math.sqrt(D * t))
                integral = quad(
                    barends_eqn4,
                    lower_lim,
                    np.inf,
                    args=(x, z, t, v, H, h_prime, D, D_prime),
                )
                integral_rslt[t_idx, k, j] = integral[0]

                # multiply the prefix by the solution to the integral
                prefix = (2 * (T1 - T0)) / (math.sqrt(np.pi))
                prefix_rslt[t_idx, k, j] = prefix
                result = prefix * integral[0]
                # store result for plotting
                myarr[t_idx, k, j] = result + T0

    return myarr
