import pygame
import pylab as plt
import matplotlib.backends.backend_agg as agg
    
def EmbedGraph(data, heading = "", x_label = "", y_label = "", log_graph = False):
        
    fig = plt.figure()
    plt.plot(data[0], data[1], color='b', linewidth=1.5)
    if log_graph:
        plt.semilogx()
    plt.ylabel(f'{y_label}')
    plt.xlabel(f'{x_label}')
    plt.title(f'{heading}')
    plt.autoscale()
    plt.grid(which='both')
    canvas = agg.FigureCanvasAgg(fig)
    plt.close('all')
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()
    size = canvas.get_width_height()
    surf = pygame.image.fromstring(raw_data, size, "RGB")

    return surf

