from matplotlib import pyplot as plt
import matplotlib.backends.backend_tkagg as agg
    
def EmbedGraph(data, heading = "", x_label = "", y_label = "", log_graph = False, cutoff_data = None, size=(7,5), colour = 'b'):
    """Plots a graph embedded into a Tkinter frame"""

    fig = plt.figure(figsize=size)
    plt.plot(data[0], data[1], color=colour, linewidth=1.5)
    plt.ticklabel_format(axis='x', style='sci', scilimits=(-2,2))
    if log_graph:
        plt.semilogx()
    if cutoff_data != None:
        if cutoff_data[1] != None:
            print("CUTOFF DATA", cutoff_data)
            print("CUTOFF DATA [1]", cutoff_data[1])
            #for p in cutoff_data[1]:
            #    print("P in data[1]", p)
            plt.annotate(f'{cutoff_data[0]}dB Cutoff:{cutoff_data[1]:.0f}Hz', xy=[cutoff_data[1],cutoff_data[0]], xytext=(7, 0), textcoords=('offset points'))
            plt.plot(cutoff_data[1], cutoff_data[0], color='r', marker='x', markersize='10')
                
    plt.rc('axes', labelsize=10)
    plt.ylabel(f'{y_label}')
    plt.xlabel(f'{x_label}')
    plt.title(f'{heading}')
    plt.grid(which='both')
    plt.autoscale()
    plt.tight_layout()
    canvas = agg.FigureCanvasTkAgg(fig)
    canvas.draw()
    plt.close('all')
    get_widz=canvas.get_tk_widget()
    get_widz.pack()

    return get_widz


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

#test data
#data = [1,-30.5821,1.04713,-30.1809,1.09648,-29.7796,1.14815,-29.3782,1.20226,-28.9766,1.25893,-28.5749,1.31826,-28.173,1.38038,-27.7709,1.44544,-27.3687,1.51356,-26.9662,1.58489,-26.5635,1.65959,-26.1605,1.7378,-25.7572,1.8197,-25.3536,1.90546,-24.9496,1.99526,-24.5453,2.0893,-24.1406,2.18776,-23.7354,2.29087,-23.3297,2.39883,-22.9234,2.51189,-22.5166,2.63027,-22.109,2.75423,-21.7008,2.88403,-21.2917,3.01995,-20.8818,3.16228,-20.4709,3.31131,-20.059,3.46737,-19.6459,3.63078,-19.2315,3.80189,-18.8157,3.98107,-18.3984,4.16869,-17.9795,4.36516,-17.5587,4.57088,-17.1358,4.7863,-16.7108,5,-16.2833,5.24807,-15.8531,5.49541,-15.4201,5.7544,-14.9838,6.0256,-14.5439,6.30957,-14.1002,6.60693,-13.6523,6.91831,-13.1997,7.24436,-12.7419,7.58578,-12.2786,7.94328,-11.8091,8.31764,-11.333,8.70964,-10.8495,9.12011,-10.358,9.54993,-9.85781,10,-9.34818,10.4713,-8.82835,10.9648,-8.29756,11.4815,-7.75509,12.0226,-7.20031,12.5893,-6.63274,13.1826,-6.05222,13.8038,-5.45903,14.4544,-4.85421,15.1356,-4.2399,15.8489,-3.61987,16.5959,-3.00024,17.378,-2.39035,18.197,-1.80376,19.0546,-1.25901,19.9526,-0.779817,20.893,-0.393675,21.8776,-0.128387,22.9087,-0.00652244,23.9883,-0.0395087,25.1189,-0.224183,26.3027,-0.543777,27.5423,-0.972753,28.8403,-1.48286,30.1995,-2.0479,31.6228,-2.64631,33.1131,-3.26171,34.6737,-3.88244,36.3078,-4.50064,38.0189,-5.11129,39.8107,-5.71138,41.6869,-6.29928,43.6516,-6.87433,45.7088,-7.43645,47.863,-7.98596,50.1187,-8.52341,52.4807,-9.04947,54.9541,-9.56489,57.544,-10.0704,60.256,-10.5669,63.0957,-11.0549,66.0693,-11.5352,69.1831,-12.0085,72.4436,-12.4753,75.8578,-12.9361,79.4328,-13.3917,83.1764,-13.8422,87.0964,-14.2884,91.2011,-14.7304,95.4993,-15.1687,100,-15.6036]
#frequencies = data[70::2]
#frequencies = [i*1000 for i in frequencies]
#freq_resp_dB = data[71::2]
