import numpy as np

__all__ = ["reduced_chi_squared"]

def reduced_chi_squared(data, uncertainties, model, bin_edges):

    params_fixed_free = model.fixed

    params_free = {k: v for k, v in params_fixed_free.items() if v is False}

    dof = len(data) - len(params_free)

    model_eval = model(bin_edges)

    chi = np.sum((data - model_eval)**2 / (uncertainties**2))
    chi_red = np.round(chi / dof,1).value

    return chi_red