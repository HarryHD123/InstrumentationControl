# Plot data

from matplotlib import pyplot as plt

# Test for plots
# c = 16789.476
# print(f'{c:.0f}')

#a = [1,2,3,4,5,6,7,20,100]
#b= [2,5,6,3,4,7,8,9,10]

#fig = plt.figure()
#plt.plot(a,b)
# plt.semilogx()
# plt.hlines(y=9, xmin=0, xmax=20, color='b', linestyle='--')
# plt.axvline(x=20, color='r', linestyle='--', linewidth=2)
# plt.plot(20,9, color='r', linewidth='5')
# #plt.annotate('Test55Hz', [20,9], xycoords='data',xytext=(1*(20/100), 0), textcoords="axes fraction")
# plt.annotate('Test55Hz', xy=[20,9], xytext=(20, 1.01), textcoords=('data', 'axes fraction'))#textcoords='offset points')
# plt.grid(which='both')
#plt.show()

def plot_freq_resp(frequencies, freq_resp_dB, cutoff_dB_val, cutoff_freq):
    """Plots a frequency response graph."""

    # Plotting
    plt.figure(3)
    plt.plot(frequencies, freq_resp_dB, color='b', linewidth=1.5)
    plt.semilogx()
    
    # Cutoff frequency calculated through interpolation and marked
    plt.annotate(f'{cutoff_dB_val}dB Cutoff:{cutoff_freq:.0f}Hz', xy=[cutoff_freq,cutoff_dB_val], xytext=(7, 0), textcoords=('offset points'))
    plt.plot(cutoff_freq, cutoff_dB_val, color='r', marker='x', markersize='10')

    # Plotting
    plt.ylabel('Gain (dB)')
    plt.xlabel('Frequency (Hz)')
    plt.title('Frequency Response')
    plt.autoscale()
    plt.grid(which='both')
    plt.show(block=False)
    plt.show()
