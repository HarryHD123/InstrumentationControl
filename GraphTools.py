from matplotlib import pyplot as plt
import matplotlib.backends.backend_tkagg as agg
    
def EmbedGraph(data, heading = "", x_label = "", y_label = "", log_graph = False, cutoff_data = None):
    
    fig = plt.figure(figsize=(7, 5))
    plt.plot(data[0], data[1], color='b', linewidth=1.5)
    if log_graph:
        plt.semilogx()
    if cutoff_data != None:
        plt.annotate(f'{cutoff_data[0]}dB Cutoff:{cutoff_data[1]:.0f}Hz', xy=[cutoff_data[1],cutoff_data[0]], xytext=(7, 0), textcoords=('offset points'))
        plt.plot(cutoff_data[1], cutoff_data[0], color='r', marker='x', markersize='10')
    plt.rc('axes', labelsize=10) #fontsize of the x and y labels)
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
