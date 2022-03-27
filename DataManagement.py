import math
import copy
from numpy import linspace
from scipy.interpolate import PchipInterpolator, interp1d

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


def calc_freq_response(results, vin_PP, frequencies, cutoff_dB_val=-3):
    """Returns the frequency response from the data provided by the test_circuit function."""
    
    freq_resp = []
    freq_resp_dB = []
    retest_f = []
    print("ALL F", frequencies)
    for f in frequencies:
        gainlist = []
        for v in vin_PP:
            gainlist.append(results[f'v={v} f={f}'][1]/results[f'v={v} f={f}'][0])
        gain_avg = sum(gainlist)/len(gainlist)
        freq_resp.append(gain_avg)
        freq_resp_dB.append(20*(math.log10(gain_avg)).real)
        retest_f.append(data_verification(freq_resp_dB, f))

    print("RETEST LIST:", retest_f)
    freq_resp_verify = copy.deepcopy(freq_resp)
    freq_resp_dB_verify = copy.deepcopy(freq_resp_dB)
    frequencies_verify = copy.deepcopy(frequencies)
    unwanted_freqs = []
    for f in retest_f:
        if f != None:
            unwanted_freqs.append(frequencies.index(f))
    
    for f in sorted(unwanted_freqs, reverse = True):
        del freq_resp_verify[f]
        del freq_resp_dB_verify[f]
        del frequencies_verify[f]

    print("FREQ VERY", frequencies_verify)
    print("FREQ OG", frequencies)
    cutoff_interp_dB = interp1d(freq_resp_dB_verify, frequencies_verify, assume_sorted=False)
    cutoff_interp = interp1d(freq_resp_verify, frequencies_verify, assume_sorted=False)

    test_list=[]
    for i in retest_f:
        if i != None:
            print("I in retest_f", i)
            list_index = frequencies.index(i)
            test_list.append(["Old val:", freq_resp_dB[list_index]])
            freq_resp[list_index] = cutoff_interp(i)
            freq_resp_dB[list_index] = cutoff_interp_dB(i)
            test_list.append(["New val:", freq_resp_dB[list_index]])
    print(test_list)
    #cutoff_interp = PchipInterpolator(freq_resp_dB, frequencies) # PchipInterpolator used as it gives a more accurate result than using standard linear interpolation

    try:
        cutoff_freq = [cutoff_interp_dB(cutoff_dB_val)]
    except ValueError:
        cutoff_freq = None

    return freq_resp, freq_resp_dB, cutoff_freq


def data_verification(freq_resp_dB, f):
    """Checks the data has no clear outliers"""
    
    try:
        grad1 = freq_resp_dB[-1]-freq_resp_dB[-2]
        grad2 = freq_resp_dB[-2]-freq_resp_dB[-3]
        print("GRADS:", grad1, grad2)
        if abs(grad2)>abs(5*grad1):
            return f
    except IndexError:
        pass


    # for i in range(len(freq_resp_dB)):
    #     grad1 = freq_resp_dB[i]-freq_resp_dB[i-1]
    #     grad2 = freq_resp_dB[i+1]-freq_resp_dB[i]
    #     if abs(grad2)>abs(10*grad1):

    # return freq_resp_dB