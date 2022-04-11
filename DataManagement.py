import math
import copy
from matplotlib import pyplot as plt
from numpy import linspace, sign
from scipy.interpolate import interp1d

def points_list_maker(start_freq, end_freq, points_per_dec):
    """Creates a list of frequencies with a specified number of points per decade."""

    first_dec=math.log10(start_freq)
    last_dec=math.log10(end_freq)

    point_maker=linspace(1,10,points_per_dec)
    freqs=[]

    for i in range(int(first_dec+1),int(last_dec)):
        temp_freqs = [int(j*10**i) for j in point_maker]
        freqs.append(temp_freqs)

    temp_freqs = []
    for i in point_maker:
        if i*10**int(first_dec) > start_freq and i*10**int(first_dec) < end_freq:
            temp_freqs.append(int(i*10**int(first_dec)))
        if i*10**int(last_dec) < end_freq and i*10**int(last_dec) > start_freq:
            temp_freqs.append(int(i*10**int(last_dec)))
    if start_freq not in temp_freqs:
        temp_freqs.append(start_freq)
    if end_freq not in temp_freqs:
        temp_freqs.append(end_freq)
        freqs.append(temp_freqs)
    freqs.append(temp_freqs)

    all_freqs=[]
    for i in freqs:
        for j in i:
            if j > start_freq or j < end_freq or j == start_freq or j == end_freq:
                all_freqs.append(j)

    all_freqs = list(dict.fromkeys(all_freqs))
    all_freqs.sort()

    return all_freqs

def calc_freq_response(results, vin_PP, frequencies, res_freq_det=2):
    """Returns the frequency response from the data provided by the test_circuit function."""
    
    freq_resp = []
    freq_resp_dB = []
    interpolate_f = []
    resonant_freq = []
    for f in frequencies:
        gainlist = []
        for v in vin_PP:
            gainlist.append(results[f'v={v} f={f}'][1]/results[f'v={v} f={f}'][0])
        gain_avg = sum(gainlist)/len(gainlist)
        freq_resp.append(gain_avg)
        freq_resp_dB.append(20*(math.log10(gain_avg)).real)
        interpolate_f.append(data_verification(freq_resp_dB, 20*(math.log10(gain_avg)).real, f)) # check points for clear outliers
        resonant_freq.append(resonant_freq_identify(freq_resp_dB, 20*(math.log10(gain_avg)).real, f))

    # The a copy of the data is made and the invalid data is removed
    freq_resp_verify = copy.deepcopy(freq_resp)
    freq_resp_dB_verify = copy.deepcopy(freq_resp_dB)
    frequencies_verify = copy.deepcopy(frequencies)
    unwanted_freqs = []
    for f in interpolate_f:
        if f != None:
            unwanted_freqs.append(frequencies.index(f))
    
    for f in sorted(unwanted_freqs, reverse = True):
        del freq_resp_verify[f]
        del freq_resp_dB_verify[f]
        del frequencies_verify[f]

    # Interpolation of invalid points is found using verified data only
    inter_interp_dB = interp1d(frequencies_verify, freq_resp_dB_verify, assume_sorted=False, fill_value='extrapolate')
    inter_interp = interp1d(frequencies_verify, freq_resp_verify, assume_sorted=False, fill_value='extrapolate')

    # Calculate resonant frequency points
    frequencies_inc_res = copy.deepcopy(frequencies)
    resonant_freq = list(filter(None, resonant_freq))
    if resonant_freq:
        res_freqs = [resonant_freq[0]]
        step = resonant_freq[0] * 1/20
        for f in resonant_freq:
            for i in range(1,res_freq_det+1):
                res_freqs.append(resonant_freq[0]+step*i)
                res_freqs.append(resonant_freq[0]-step*i)
        res_freqs.sort(reverse=True)
        res_index = frequencies.index(resonant_freq[0])
        frequencies_inc_res.pop(res_index)
        for i in res_freqs:
            frequencies_inc_res.insert(res_index, i)
  
    # Graphs showing difference in data sets
    plt.figure(1)
    plt.plot(frequencies, freq_resp_dB)
    plt.figure(2)
    plt.plot(frequencies_verify, freq_resp_dB_verify)
    plt.figure(3)
    interpolated_dB = []
    for i in frequencies_inc_res:
        interpolated_dB.append(inter_interp_dB(i))
        
    plt.plot(frequencies_inc_res, interpolated_dB)

    plt.show(block=False)
    plt.show()

    return freq_resp, freq_resp_dB, res_freqs, frequencies_inc_res

def calc_freq_resp_resfreq(results, vin_PP, frequencies):
    """Returns the frequency response for resonant frequency points from the data provided by the test_circuit function."""

    freq_resp = []
    freq_resp_dB = []
    interpolate_f = []
    for f in frequencies:
        gainlist = []
        for v in vin_PP:
            gainlist.append(results[f'v={v} f={f}'][1]/results[f'v={v} f={f}'][0])
        gain_avg = sum(gainlist)/len(gainlist)
        freq_resp.append(gain_avg)
        freq_resp_dB.append(20*(math.log10(gain_avg)).real)
        interpolate_f.append(data_verification(freq_resp_dB, 20*(math.log10(gain_avg)).real, f)) # check points for clear outliers

    # The a copy of the data is made and the invalid data is removed
    freq_resp_verify = copy.deepcopy(freq_resp)
    freq_resp_dB_verify = copy.deepcopy(freq_resp_dB)
    frequencies_verify = copy.deepcopy(frequencies)
    unwanted_freqs = []
    for f in interpolate_f:
        if f != None:
            unwanted_freqs.append(frequencies.index(f))
    
    for f in sorted(unwanted_freqs, reverse = True):
        del freq_resp_verify[f]
        del freq_resp_dB_verify[f]
        del frequencies_verify[f]

    # Interpolation of invalid points is found using verified data only
    inter_interp_dB = interp1d(frequencies_verify, freq_resp_dB_verify, assume_sorted=False, fill_value='extrapolate')
    inter_interp = interp1d(frequencies_verify, freq_resp_verify, assume_sorted=False, fill_value='extrapolate')

    return freq_resp, freq_resp_dB

def combine_res_data(results_main, results_res, freq_resp_main, freq_resp_dB_main, freq_resp_res, freq_resp_dB_res, res_freqs, freqs_inc_res):
    """Combines results from the inital test and those from the resonant frequency points."""

    results = {**results_main, **results_res}
    count = 0
    for f in res_freqs:
        pos = freqs_inc_res.index(f)
        freq_resp_main.insert(pos, freq_resp_res[count])
        freq_resp_dB_main.insert(pos, freq_resp_dB_res[count])
        count+=1

    return results, freq_resp_main, freq_resp_dB_main

def calc_cutoff_freq(freq_resp_dB, frequencies, cutoff_dB_val=-3):
    """Calculates the cutoff frequency using interpolation"""

    cutoff_interp_dB = interp1d(freq_resp_dB, frequencies, assume_sorted=False)
    try:
        cutoff_freq = cutoff_interp_dB(cutoff_dB_val)
    except ValueError:
        cutoff_freq = None

    return cutoff_freq

def data_verification(freq_resp_dB, current_freq_resp_dB, f):
    """Checks the data has no clear outliers"""
    
    if abs(current_freq_resp_dB)>100:
        return f
    try:
        grad1 = freq_resp_dB[-1]-freq_resp_dB[-2]
        grad2 = freq_resp_dB[-2]-freq_resp_dB[-3]
        if abs(grad2)>abs(50*grad1):
            return f
    except IndexError:
        pass

def resonant_freq_identify(freq_resp_dB, current_freq_resp_dB, f):
    """Checks the data has no clear outliers"""
    try:
        grad1 = freq_resp_dB[-1]-freq_resp_dB[-2]
        grad2 = freq_resp_dB[-2]-freq_resp_dB[-3]
        if abs(grad2)>abs(50*grad1) or abs(current_freq_resp_dB)>100:
            pass
        elif sign(grad1)!= sign(grad2):
            return f
    except IndexError:
        pass