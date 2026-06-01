import matplotlib 
from matplotlib import pyplot as plt
import numpy as np


__all__ = ["plot_fit_results"]

def plot_fit_results(count_edges,photon_edges,observed_counts,observed_counts_err,model,save_name,fit_times):

    count_centers = count_edges[:-1] + 0.5*np.diff(count_edges)

    compound_model_evaluation = model(photon_edges)
    
    count_bin_widths = 0.5*np.diff(count_edges)

    model_names = list(model.submodel_names)

    x_unit = count_edges.unit
    y_unit = observed_counts.unit

    left, bottom, width, height = 0,0,1,1
    spacing = 0.005

    w,h=11,10

    plt.rcParams.update({
        'xtick.labelsize': 14,
        'ytick.labelsize': 14,
        'axes.labelsize': 16 # This sets both x and y axis label sizes
    })

    tfs = 14

    colour_tot = 'k'
    colour_thermal = 'C0'
    colour_nonthermal = 'C1'
    colour_albedo = 'grey'

    fig = plt.figure(figsize=(w,h))

    rect_dat = [left,bottom+(1/4)*height+1*spacing,width,(3/4)*height]
    rect_rat = [left,bottom,width,(1/4)*height]

    ax_dat = plt.axes(rect_dat)
    ax_rat = plt.axes(rect_rat,sharex=ax_dat)

    ax_dat.errorbar(count_centers,observed_counts,label='Observed Data',marker='None',ms=5,linestyle='None',yerr=observed_counts_err,xerr=count_bin_widths, color='grey',elinewidth=2)
    ax_dat.stairs(compound_model_evaluation.value,count_edges.value,baseline=None, label='Total', linewidth=2,alpha=0.75,zorder=10000,color='k')

    dict = {}


    if 'ThermalEmission' in model_names and 'ThickTarget' in model_names:

        eval_noalbedo = ((((model['ThermalEmission'] + model['ThickTarget']) * model['InverseSquareFluxScaling'] ) ) | model['SRM'])(photon_edges)
        eval_albedo = ((((model['ThermalEmission'] + model['ThickTarget']) * model['InverseSquareFluxScaling'] ) | model['Albedo'] ) | model['SRM'])(photon_edges)
        eval_thermal = (((model['ThermalEmission'] * model['InverseSquareFluxScaling'] ) ) | model['SRM'])(photon_edges)
        eval_nonthermal = (((model['ThickTarget'] * model['InverseSquareFluxScaling'] )  ) | model['SRM'] )(photon_edges)

        albedo = eval_albedo - eval_noalbedo

        ax_dat.stairs(eval_thermal.value,count_edges.value,label='ThermalEmission',baseline=None,linewidth=2,alpha=0.9,zorder=10000, color = colour_thermal)
        ax_dat.stairs(eval_nonthermal.value,count_edges.value,label='ThickTarget',baseline=None, linewidth=2,alpha=0.9,zorder=10000, color = colour_nonthermal)
        ax_dat.stairs(albedo.value,count_edges.value,label='Albedo',baseline=None, linewidth=2,alpha=0.9,zorder=10000,color=colour_albedo)

        ax_dat.text(0.77,0.7,f'Temp = {np.round(model.temperature_0.value,1)} {model.temperature_0.unit}',transform=ax_dat.transAxes,fontsize=tfs,color=colour_thermal)
        ax_dat.text(0.77,0.65,f'EM = {np.round(model.emission_measure_0.value,3)} {r'$\mathrm{\times \: 10^{49} \: cm^{-3}}$'}',transform=ax_dat.transAxes,fontsize=tfs,color=colour_thermal)
        ax_dat.text(0.77,0.6,f'Index = {np.round(model.p_1.value,1)}',transform=ax_dat.transAxes,fontsize=tfs,color=colour_nonthermal)
        ax_dat.text(0.77,0.55,f'E_c = {np.round(model.low_e_cutoff_1.value,1)} {model.low_e_cutoff_1.unit}',transform=ax_dat.transAxes,fontsize=tfs,color=colour_nonthermal)
        ax_dat.text(0.77,0.5,f'e Flux = {np.round(model.total_eflux_1.value,1)} {r'$\mathrm{\times \: 10^{35} \: e \: s^{-1}}$'}',transform=ax_dat.transAxes,fontsize=tfs,color=colour_nonthermal)


    if 'ThermalEmission' in model_names and 'ThickTarget' not in model_names:

        eval_noalbedo = (((model['ThermalEmission'] * model['InverseSquareFluxScaling'] ) ) | model['SRM'])(photon_edges)
        eval_albedo = (((model['ThermalEmission'] * model['InverseSquareFluxScaling'] ) | model['Albedo'] ) | model['SRM'])(photon_edges)
        eval_thermal = (((model['ThermalEmission'] * model['InverseSquareFluxScaling'] ) ) | model['SRM'])(photon_edges)

        albedo = eval_albedo - eval_noalbedo

        ax_dat.stairs(eval_thermal.value,count_edges.value,label='ThermalEmission',baseline=None, linewidth=2,alpha=0.9,zorder=10000, color=colour_thermal)
        ax_dat.stairs(albedo.value,count_edges.value,label='Albedo',baseline=None, linewidth=2,alpha=0.9,zorder=10000, color=colour_albedo)
        

        ax_dat.text(0.77,0.7,f'Temp = {np.round(model.temperature_0.value,1)} {model.temperature_0.unit}',transform=ax_dat.transAxes,fontsize=tfs,color=colour_thermal)
        ax_dat.text(0.77,0.65,f'EM = {np.round(model.emission_measure_0.value,3)} {r'$\mathrm{\times \: 10^{49} \: cm^{-3}}$'}',transform=ax_dat.transAxes,fontsize=tfs,color=colour_thermal)

   
    ax_dat.set_ylim(0.8*np.min(observed_counts.value),2*np.max(observed_counts.value))
    ax_dat.legend(frameon=False,fontsize=14)
    ax_dat.loglog()

    params_fixed_free = model.fixed

    params_free = {k: v for k, v in params_fixed_free.items() if v is False}


    dof = len(observed_counts) - len(params_free)

    delchi = (observed_counts - compound_model_evaluation) / observed_counts_err
    chi = np.sum((observed_counts - compound_model_evaluation)**2 / (observed_counts_err**2))
    chi_red = np.round(chi / dof,1).value

    ax_rat.stairs(delchi.value, count_edges.value,baseline=None, linewidth=2,color='k')
    ax_rat.axhline(0,linestyle='--',linewidth=2, color='k')

    ax_dat.set_ylabel(f'Counts Spectrum ({y_unit})')
    ax_rat.set_xlabel(f'Energy ({x_unit})')

    ax_rat.set_ylabel(r'$\mathrm{(D - M) / \sigma}$')
    ax_rat.text(0.8,0.06,r'$\mathrm{\chi^{2}_{red} = }$'+str(chi_red),transform=ax_rat.transAxes,fontsize=14)

    for ax in fig.axes:
        ax.tick_params(axis='both', which='both',top=True, bottom=True, left=True, right=True,  direction='in', length=6)
        ax.tick_params(axis='both', which='minor',top=True, bottom=True, left=True, right=True,  length=3)
        ax.minorticks_on()

    fig.suptitle(fit_times,fontsize=16,x=0.5,y=1.035)

    fig.savefig(str(save_name),bbox_inches='tight',dpi=300)

    plt.show()