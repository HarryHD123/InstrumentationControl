# Create additional data from the results

import math
from numpy import linspace

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
    print("Cutoff", cutoff_freq)

    return freq_resp, freq_resp_dB, cutoff_freq


#DOESNT WORK IF START FREQ ISNT A POWER OF 10 (FIX)
def points_list_maker(start_freq, end_freq, points_per_dec):
    """Creates a list of frequencies with a specified number of points per decade."""

    first_dec=math.log10(start_freq)
    last_dec=math.log10(end_freq)

    point_maker=linspace(1,10,points_per_dec)
    freqs=[]

    for i in range(int(first_dec),int(last_dec)):
        temp_freqs = [int(j*10**i) for j in point_maker]
        freqs.append(temp_freqs)

    temp_freqs = []
    if not int(last_dec)==last_dec:
        for i in point_maker:
            if i*10**int(last_dec) < end_freq:
                temp_freqs.append(int(i*10**int(last_dec)))
        if end_freq not in temp_freqs:
            temp_freqs.append(end_freq)   
        freqs.append(temp_freqs)

    all_freqs=[]
    for i in freqs:
        for j in i:
            all_freqs.append(j)

    return all_freqs
    
print(points_list_maker(15,5000,4))

# Save data
