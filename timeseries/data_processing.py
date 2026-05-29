import numpy as np
from stixpy.product import Product 
from astropy.time import Time 
from astropy.time import TimeDelta 
from user_functions import csv_writer
from astropy.io import fits
from pathlib import Path
import pandas as pd


def time_finder_sci(counts, time,
                    window_size_start, window_size_end,
                    thresh_start, thresh_end,
                    dt_start_offset=0.0, dt_end_offset=0.0):
    """
    Find start and end times of 'activity' based on the running mean of the gradient.

    Parameters
    ----------
    counts : array-like
        Signal values.
    time : array-like
        Time array (same length as counts). Can be plain floats or astropy Time.
    window_size_start : int
        Window size for running mean used to detect the start.
    window_size_end : int
        Window size for running mean used to detect the end.
    thresh_start : float
        Threshold for the smoothed gradient to define the start.
    thresh_end : float
        Threshold for the smoothed gradient to define the end.
    dt_start_offset : float, optional
        Time offset *in seconds* to move before the detected start.
    dt_end_offset : float, optional
        Time offset *in seconds* to move after the detected end.

    Returns
    -------
    t_start, t_end : same type as elements of `time` (e.g. astropy Time) or None
        Estimated start and end times. Returns None if not found.
    """

    counts = np.asarray(counts).reshape(-1)
    time   = np.asarray(time).reshape(-1)

    # --- Basic cadence (assume nearly uniform sampling) ---
    if len(time) > 1:
        dt_raw = np.median(np.diff(time))
        # If this is an astropy TimeDelta or Quantity, convert to seconds
        try:
            dt = float(dt_raw.to_value('s'))
        except AttributeError:
            # Plain numeric times, no units attached
            dt = float(dt_raw)
    else:
        dt = 1.0  # fallback in seconds (or "1 step" equivalent)

    # Gradient of the signal
    grad = np.gradient(counts)

    # Running-mean of gradient (start and end windows)
    kernel_start = np.ones(window_size_start) / window_size_start
    kernel_end   = np.ones(window_size_end)   / window_size_end

    start_win = np.convolve(grad, kernel_start, mode='valid')
    end_win   = np.convolve(grad, kernel_end,   mode='valid')
    print(start_win)

    # --- Find start: first index where running mean > thresh_start ---
    start_idx_sm = np.where(start_win > thresh_start)[0]
    if start_idx_sm.size > 0:
        k = start_idx_sm[0]
        # Center of the window ~ k + (window_size_start - 1)/2
        idx_start = int(k + (window_size_start - 1) // 2)

        # Apply time offset backwards (dt_start_offset in seconds)
        offset_n_start = int(round(dt_start_offset / dt)) if dt > 0 else 0
        idx_start = max(idx_start - 10 * offset_n_start, 0)

        t_start = time[idx_start]
    else:
        t_start = None
        print('No start time found!')

    # --- Find end: last index where running mean > thresh_end ---
    end_idx_sm = np.where(end_win > thresh_end)[0]
    if end_idx_sm.size > 0:
        k = end_idx_sm[-1]
        idx_end = int(k + (window_size_end - 1) // 2)

        # Apply time offset forwards (dt_end_offset in seconds)
        offset_n_end = int(round(dt_end_offset / dt)) if dt > 0 else 0
        idx_end = min(idx_end + offset_n_end, len(time) - 1)

        t_end = time[idx_end]
    else:
        t_end = None
        print('No end time found')

    return t_start, t_end

def cal_data(sci_data, bkg_data,
             e_min=None, e_max=None,
             t_sci=None, t_bkg=None,
             save_csv=False):

    # ---- Open science file and get data ----
    sci = Product(sci_data)
    counts_fullfile_sci, errors_fullfile_sci, times_fullfile_sci, deltatimes_fullfile_sci, energies_fullfile_sci = sci.get_data()
    for k in range(len(energies_fullfile_sci)):
        if energies_fullfile_sci['e_low'][k].value == e_min:
            e_min_idx = k
        if e_max is not None:
            if energies_fullfile_sci['e_high'][k].value == e_max:
                e_max_idx = k
        else:
            e_max_idx = len(energies_fullfile_sci) - 2
        
    # ---- Select right energy range ----
    energy_range = energies_fullfile_sci['e_low'][e_max_idx] - energies_fullfile_sci['e_low'][e_min_idx]
    counts_fullfile_sci, errors_fullfile_sci, times_fullfile_sci, deltatimes_fullfile_sci, energies_fullfile_sci = sci.get_data(
        energy_indices=[[e_min_idx, e_max_idx]])
    
    counts_fullfile_sci = np.nansum(counts_fullfile_sci, axis=(1)).squeeze()
    deltatimes = deltatimes_fullfile_sci[..., 0].squeeze()
    counts_time_search = counts_fullfile_sci.squeeze().value

    # ---- Select time range ----
    if t_sci is not None: 
        t_low, t_high = t_sci
        time_indices = [j for j, t in enumerate(times_fullfile_sci)
                        if times_fullfile_sci[j] >= t_low and times_fullfile_sci[j] <= t_high]
    else:
        time_indices = [j for j, t in enumerate(times_fullfile_sci)]
           
    counts_sci, errors_sci, times_sci, deltatimes, energies_sci = sci.get_data(
        energy_indices=[[e_min_idx, e_max_idx]],
        time_indices=time_indices)

    counts_time_search = counts_time_search[time_indices]
    counts_sci = np.nansum(counts_sci, axis=(1, 2)).squeeze().value * 100 * energy_range.value   
    errors_sci = np.sqrt(np.nansum(errors_sci**2, axis=(1, 2)).squeeze().value) * 100 * energy_range.value
    deltatimes = deltatimes[..., 0].squeeze()


    # ---- Background subtraction ONLY if time interval is given ----
    bkg_mean = 0  # set 0 so that no background time returns unsubtracted counts
    bkg_error_mean = 0
    bkg = Product(bkg_data)
    counts_fullfile_bkg, errors_fullfile_bkg, times_fullfile_bkg, deltatimes_fullfile_bkg, energies_fullfile_bkg = bkg.get_data()
    for k in range(len(energies_fullfile_bkg)):
        if energies_fullfile_bkg['e_low'][k].value == e_min:
            e_min_idx_bkg = k
        if e_max is not None:
            if energies_fullfile_bkg['e_high'][k].value == e_max:
                e_max_idx_bkg = k
        else:
            e_max_idx_bkg = len(energies_fullfile_bkg) - 2
    
    counts_bkg, errors_bkg, times_bkg, deltatimes_bkg, energies_bkg = bkg.get_data(
        energy_indices=[[e_min_idx_bkg, e_max_idx_bkg]])
    
    if t_bkg is not None:  # only subtract background if time is given
        time_indices_bkg = [j for j, t in enumerate(times_fullfile_bkg)
                            if times_fullfile_bkg[j] >= t_bkg[0] and times_fullfile_bkg[j] <= t_bkg[1]]
        counts_bkg, errors_bkg, times_bkg, deltatimes_bkg, energies_bkg = bkg.get_data(
            energy_indices=[[e_min_idx_bkg, e_max_idx_bkg]],
            time_indices=time_indices_bkg)
        counts_bkg = np.nansum(counts_bkg, axis=(1, 2)).squeeze().value * 100 * energy_range.value
        bkg_mean = np.mean(counts_bkg)
        bkg_error_mean = np.std(counts_bkg)

    # ---- Data returned by function ----
    counts = (counts_sci - bkg_mean)
    error = np.sqrt(errors_sci**2 + bkg_error_mean**2)
    time = (np.cumsum(deltatimes) - deltatimes[0]).squeeze().to_value('s')
    time_dt = times_sci.to_datetime()

    # ---- Save data ----
    filename = Path(sci_data).name

    id_part = filename.split("V02_")[1].split("-")[0]   
    subfolder = 'input_data'
    rows = list(range(len(counts) - 1))
    if save_csv is True:
        start = time_dt[0]
        csv_writer(id_part, start, rows, time, counts, time_dt, error, subfolder=subfolder)

    return time, counts, time_dt, error
