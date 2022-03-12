import math
from numpy import linspace
from scipy.interpolate import PchipInterpolator

def calc_freq_response(results, vin_PP, frequencies, cutoff_dB_val=-3):
    """Returns the frequency response from the data provided by the test_circuit function."""
    
    freq_resp=[]
    freq_resp_dB=[]
    for f in frequencies:
        gainlist=[]
        for v in vin_PP:
            gainlist.append(results[f'v={v} f={f}'][1]/results[f'v={v} f={f}'][0])
        gain_avg = sum(gainlist)/len(gainlist)
        freq_resp.append(gain_avg)
        freq_resp_dB.append(10*(math.log10(gain_avg)).real)
    
    cutoff_interp = PchipInterpolator(freq_resp_dB, frequencies) # PchipInterpolator used as it gives a more accurate result than using standard linear interpolation
    cutoff_freq = cutoff_interp(cutoff_dB_val)

    return freq_resp, freq_resp_dB, cutoff_freq


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
        if i*10**int(first_dec) > start_freq:
            temp_freqs.append(int(i*10**int(first_dec)))
        if i*10**int(last_dec) < end_freq:
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
            all_freqs.append(j)

    all_freqs = list(dict.fromkeys(all_freqs))
    all_freqs.sort()

    return all_freqs
    