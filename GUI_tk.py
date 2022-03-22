from statistics import NormalDist
from tkinter import *
import shelve
from InstrumentControl import *
from DataManagement import *
from GraphTools import EmbedGraph
import csv
from PIL import ImageTk, Image

class InstrumentationControlApp(Tk):
    def __init__(self):
        Tk.__init__(self)
        self._frame = None
        self.oscope = None
        self.siggen = None
        self.siggen_setting = None
        self.mmeter = None
        self.powers = None
        self.switch_frame(MainMenu)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack(fill = "both", expand = True)

class MainMenu(Frame):
    def __init__(self, master):

        # Allow frame to be set
        Frame.__init__(self, master)

        # Set colours and fontsize
        self.BLACK = (0,0,0)
        self.GREEN = (0,255,0)
        self.RED = (255,0,0)
        self.WHITE = (255,255,255)
        self.LGREY = (170,170,170)
        self.DGREY = (100,100,100)
        self.LBLUE = (12, 181, 249)
        self.BACKGROUND = (254, 254, 254)
        self.FONTSIZE = 25
        self.FONTSIZE_LARGE = 50

        # Create buttons and labels
        self.lbl_heading = Label (self, text='Synardyne Laboratory Instrumentation Control', height=8, width=50, font=('Helvetica', self.FONTSIZE_LARGE))
        self.btn_testmenu = Button (self, command=lambda: master.switch_frame(FreqRespMenu), text = 'Measure Frequency Response', height=2, width=25, font=('Helvetica', self.FONTSIZE))
        self.btn_connectionmenu = Button (self, command=lambda: master.switch_frame(ConnectionMenu), text = 'Connection Menu', height=2, width=25, font=('Helvetica', self.FONTSIZE))
        self.btn_oscilloscopemenu = Button (self, command=lambda: master.switch_frame(OscilloscopeMenu), text = 'Oscilloscope Screen', height=2, width=25, font=('Helvetica', self.FONTSIZE))
        self.btn_demomenu = Button (self, command=lambda: master.switch_frame(DemoMenu), text = 'Op Amp Demo', height=2, width=25, font=('Helvetica', self.FONTSIZE))

        # Place buttons and labels
        self.lbl_heading.place(relx=0.5, rely =0.2, anchor=CENTER)
        self.btn_testmenu.place(relx=0.3, rely =0.4, anchor=CENTER)
        self.btn_connectionmenu.place(relx=0.7, rely =0.4, anchor=CENTER)
        self.btn_oscilloscopemenu.place(relx=0.3, rely =0.6, anchor=CENTER)
        self.btn_demomenu.place(relx=0.7, rely =0.6, anchor=CENTER)

class FreqRespMenu(Frame):
    def __init__(self, master):

        # Allow frame to be set
        Frame.__init__(self, master)

         # Set fontsize
        self.FONTSIZE = 15
        self.FONTSIZE_LARGE = 25

        # Read inital settings
        self.Reset()
        self.ReadSettings()

        # Create text Variables
        self.tk_voltages = StringVar(self, self.voltages)
        self.tk_start_frequency = IntVar(self, self.start_frequency)
        self.tk_end_frequency = IntVar(self, self.end_frequency)
        self.tk_frequency_step = IntVar(self, self.frequency_step)
        self.tk_dc_offset = IntVar(self, self.dc_offset)
        self.tk_cutoff_dB = IntVar(self, self.cutoff_dB)
        self.tk_siggen_selected = IntVar(self, self.detect_siggen(master))
        self.tk_coupling = IntVar(self, self.detect_coupling())

        # Create buttons and labels
        self.btn_home = Button (self, command=lambda: [self.entry_update_values(), master.switch_frame(MainMenu)], text = 'Home', font=('Helvetica', self.FONTSIZE))
        self.lbl_heading = Label (self, text='Frequency Response Menu', font=('Helvetica', self.FONTSIZE_LARGE), borderwidth=1, relief="solid")
        self.lbl_voltages = Label (self, text='Pk-pk Amplitude (V)', font=('Helvetica', self.FONTSIZE))
        self.lbl_startfreq = Label (self, text='Start Frequency (Hz)', font=('Helvetica', self.FONTSIZE))
        self.lbl_endfreq = Label (self, text='End Frequency (Hz)', font=('Helvetica', self.FONTSIZE))
        self.lbl_freqsteps = Label (self, text='Frequencies per decade', font=('Helvetica', self.FONTSIZE))
        self.lbl_offset = Label (self, text='DC Offset (V)', font=('Helvetica', self.FONTSIZE))
        self.lbl_cutoff = Label (self, text='Cutoff (dB)', font=('Helvetica', self.FONTSIZE))
        self.lbl_connect_first = Label (self, text='Please connect to an oscilloscope from the connections\nmenuto measure the frequency response', fg='red', font=('Helvetica', 10))
        self.lbl_testing = Label (self, text='Testing circuit\nPlease wait', fg='red', font=('Helvetica', 10))
        self.btn_acquire_freqresp = Button (self, state=self.check_oscope_connection(master), command=lambda:[self.entry_update_values(), self.show_testing_label(), self.acquire_results(master.oscope, siggen=master.siggen_setting), self.check_freq_response_calc(self.btn_acquire_freqresp), self.update_freq_resp_plot()], text = 'Measure\nFrequency Response', height=2, width=17, font=('Helvetica', self.FONTSIZE))
        self.btn_reset = Button (self, command=lambda:[self.Reset(), master.switch_frame(FreqRespMenu)], text = 'RESET', font=('Helvetica', self.FONTSIZE), fg = 'red')
        self.btn_export = Button (self, state=self.check_export(), command=lambda:[self.export()], text = 'Export', height=2, width=5, font=('Helvetica', self.FONTSIZE))

        # Create entries and radio buttons
        vcmd = self.register(self.callback_num)
        vcmd_neg = self.register(self.callback_num_neg)
        self.entry_voltages = Entry (self, textvariable = self.tk_voltages, validate='key', validatecommand=(vcmd,'%P'), font=('Helvetica', self.FONTSIZE), width=7)
        self.entry_startfreq = Entry (self, textvariable = self.tk_start_frequency, validate='key', validatecommand=(vcmd,'%P'), font=('Helvetica', self.FONTSIZE), width=7)
        self.entry_endfreq = Entry (self, textvariable = self.tk_end_frequency, validate='key', validatecommand=(vcmd,'%P'), font=('Helvetica', self.FONTSIZE), width=7)
        self.entry_freqsteps = Entry (self, textvariable = self.tk_frequency_step, validate='key', validatecommand=(vcmd,'%P'), font=('Helvetica', self.FONTSIZE), width=7)
        self.entry_offset = Entry (self, textvariable = self.tk_dc_offset, validate='key', validatecommand=(vcmd_neg,'%P'), font=('Helvetica', self.FONTSIZE), width=7)
        self.entry_cutoff = Entry (self, textvariable = self.tk_cutoff_dB, validate='key', validatecommand=(vcmd_neg,'%P'), font=('Helvetica', self.FONTSIZE), width=7)
        self.radio_siggen_internal = Radiobutton (self, text = 'Internal signal generator', variable=self.tk_siggen_selected, value=1, command=lambda:[self.select_siggen(master)], font=('Helvetica', self.FONTSIZE))
        self.radio_siggen_external = Radiobutton (self, state=self.check_siggen_connection(master), text = 'External signal generator', variable=self.tk_siggen_selected, value=2, command=lambda:[self.select_siggen(master)], font=('Helvetica', self.FONTSIZE))
        self.radio_coupling_DC = Radiobutton (self, text = 'DC Coupling', variable=self.tk_coupling, value=1, command=lambda:[self.select_coupling()], font=('Helvetica', self.FONTSIZE))
        self.radio_coupling_AC = Radiobutton (self, text = 'AC Coupling', variable=self.tk_coupling, value=2, command=lambda:[self.select_coupling()], font=('Helvetica', self.FONTSIZE))

        # Place widgets
        self.btn_home.place(relx=0.06, rely =0.07, anchor=CENTER)
        self.lbl_heading.place(relx=0.26, rely=0.07, anchor=CENTER)

        self.lbl_voltages.place(relx=0.1, rely=0.17, anchor=CENTER)
        self.entry_voltages.place(relx=0.2, rely=0.17, anchor=CENTER)
        self.lbl_offset.place(relx=0.1, rely=0.22, anchor=CENTER)
        self.entry_offset.place(relx=0.2, rely=0.22, anchor=CENTER)
        self.lbl_cutoff.place(relx=0.1, rely=0.27, anchor=CENTER)
        self.entry_cutoff.place(relx=0.2, rely=0.27, anchor=CENTER)

        self.lbl_startfreq.place(relx=0.1, rely=0.32, anchor=CENTER)
        self.entry_startfreq.place(relx=0.2, rely=0.32, anchor=CENTER)
        self.lbl_endfreq.place(relx=0.1, rely=0.37, anchor=CENTER)
        self.entry_endfreq.place(relx=0.2, rely=0.37, anchor=CENTER)
        self.lbl_freqsteps.place(relx=0.1, rely=0.42, anchor=CENTER)
        self.entry_freqsteps.place(relx=0.2, rely=0.42, anchor=CENTER)

        self.radio_siggen_internal.place(relx=0.12, rely=0.5, anchor=CENTER)
        self.radio_siggen_external.place(relx=0.12, rely=0.54, anchor=CENTER)

        self.radio_coupling_DC.place(relx=0.12, rely=0.62, anchor=CENTER)
        self.radio_coupling_AC.place(relx=0.12, rely=0.66, anchor=CENTER)
        
        self.btn_acquire_freqresp.place(relx=0.12, rely=0.75, anchor=CENTER)
        self.btn_reset.place(relx=0.12, rely=0.85, anchor=CENTER)
        self.lbl_connect_first.place(relx=0.13, rely=0.92, anchor=CENTER)  
        self.btn_export.place(relx=0.95, rely=0.06, anchor=CENTER)

        # Draw graph
        self.freq_resp_plot = EmbedGraph((1,1), heading='Frequency Response', y_label='Gain (dB)', x_label='Frequency (Hz)', log_graph=True, size = (11,6.8))
        self.freq_resp_plot.place(relx=0.62, rely=0.55, anchor=CENTER)

    def show_testing_label(self):
        self.lbl_testing["text"] = 'Testing circuit\nPlease wait'
        self.lbl_testing.place(relx=0.12, rely=0.92, anchor=CENTER)

    def acquire_results(self, oscope, siggen=None):
        self.results = test_circuit(oscope, [self.voltages], self.frequencies, siggen=siggen)
        self.lbl_testing["text"] = ""

    def update_freq_resp_plot(self):
        self.freq_resp, self.freq_resp_dB, self.cutoff_freq = calc_freq_response(self.results, [self.voltages], self.frequencies, self.cutoff_dB)
        self.freq_resp_plot = EmbedGraph((self.frequencies,self.freq_resp_dB), heading='Frequency Response', y_label='Gain (dB)', x_label='Frequency (Hz)', log_graph=True, cutoff_data=[self.cutoff_dB, self.cutoff_freq], size = (11,6.8))
        self.freq_resp_plot.place(relx=0.62, rely=0.55, anchor=CENTER)

    def check_freq_response_calc(self, button):
        """Changes the state of the frequency response button"""
        # If the STATE is NORMAL
        if self.results != None:
            button['state'] = NORMAL
        else:
            button['state'] = DISABLED

    def check_export(self):
        """Checks there is data to be exported"""
        if self.results != None and self.freq_resp_dB != None and self.cutoff_freq != None:
            return NORMAL
        else:
            return DISABLED

    def export(self):
        """Exports data to a .csv file"""
        with open('FreqResp_raw_results.csv', 'wb') as res:
            writer = csv.writer(res)
            writer.writerows(self.results)
        with open('FreqResp_dB_data.csv', 'wb') as dB:
            writer = csv.writer(dB)
            writer.writerows(self.freq_resp_dB)
        with open('FreqResp_cutoff_freq.csv', 'wb') as cutoff:
            writer = csv.writer(cutoff)
            writer.writerows(self.cutoff_freq)

    def check_oscope_connection(self, master):
        """Checks if oscope is connected"""
        if master.oscope != None:
            self.lbl_connect_first['text']=""
            return NORMAL            
        else:
            self.lbl_connect_first['text']='Please connect to an oscilloscope from the connections\nmenuto measure the frequency response'
            return DISABLED

    def check_siggen_connection(self, master):
        """Checks if oscope is connected"""
        if master.siggen != None:
            return NORMAL            
        else:
            return DISABLED

    def detect_siggen(self, master):
        if master.siggen_setting == None:
            return 1
        else:
            return 2

    def select_siggen(self, master):
        if self.tk_siggen_selected.get() == 2:
            master.siggen_setting = master.siggen
        else:
            master.siggen_setting = None

    def detect_coupling(self):
        if self.coupling == 'DC':
            return 1
        else:
            return 2

    def select_coupling(self):
        if self.tk_coupling.get() == 2:
            self.coupling = 'AC'
        else:
            self.coupling = 'DC'

    # Call backs to check data entry
    def callback_num(self, input):
        """Only numeric input allowed"""
        if input.isnumeric() or input == '' or input.replace(".", '', 1).isnumeric():
            return True
        else:
            return False          

    def callback_num_neg(self, input):
        """Only numeric input allowed (including negative numbers)"""
        if input.isnumeric() or input == '' or input.replace(".", '', 1).isnumeric():
            return True
        elif input.startswith("-") and (input[1:].isnumeric() or input[1:]=='' or input[2:].replace(".", '').isnumeric()):
            return True
        else:
            return False  

    def convert_num(self, data):
        """Converts string to int if it can, otherwise to float"""
        try:
            val = int(data)
        except:
            val = float(data)
        return val

    ###########
    """Read and write functions"""
    ###########
    def entry_update_values(self):
        self.voltages = self.convert_num(self.entry_voltages.get())
        self.start_frequency = self.convert_num(self.entry_startfreq.get())
        self.end_frequency = self.convert_num(self.entry_endfreq.get())
        self.frequency_step = self.convert_num(self.entry_freqsteps.get())
        self.frequencies = points_list_maker(self.start_frequency, self.end_frequency, self.frequency_step)
        self.dc_offset = self.convert_num(self.entry_offset.get())
        self.cutoff_dB = self.convert_num(self.entry_cutoff.get())
        self.WriteSettings()
        
    def WriteSettings(self):
        """Writes the test settings to the save file"""
        test_settings_file = shelve.open("Data/test_settings",writeback=True)
        test_settings_file["voltages"] = self.voltages
        test_settings_file["start_freq"] = self.start_frequency
        test_settings_file["end_freq"] = self.end_frequency
        test_settings_file["freq_step"] = self.frequency_step
        self.frequencies = points_list_maker(self.start_frequency, self.end_frequency, self.frequency_step)
        test_settings_file["frequencies"] = self.frequencies
        test_settings_file["dc_offset"] = self.dc_offset
        test_settings_file["cutoff(dB)"] = self.cutoff_dB
        test_settings_file["coupling"] = self.coupling
        test_settings_file.close()

    def ReadSettings(self):
        """Reads the test settings"""
        test_settings_file = shelve.open("Data/test_settings")
        self.voltages = test_settings_file["voltages"]
        self.start_frequency = test_settings_file["start_freq"]
        self.end_frequency = test_settings_file["end_freq"]
        self.frequency_step = test_settings_file["freq_step"]
        self.frequencies = test_settings_file["frequencies"]
        self.dc_offset = test_settings_file["dc_offset"]
        self.cutoff_dB = test_settings_file["cutoff(dB)"]
        self.coupling = test_settings_file["coupling"]
        test_settings_file.close()

    def Reset(self):
        """Resets settings to default"""
        self.voltages = 1
        self.start_frequency = 1000
        self.end_frequency = 100000
        self.frequency_step = 10
        self.frequencies = points_list_maker(self.start_frequency, self.end_frequency, self.frequency_step)
        self.dc_offset = 0
        self.cutoff_dB = -3
        self.results = None
        self.freq_resp = None
        self.freq_resp_dB = None
        self.cutoff_freq = None
        self.coupling = 'DC'

class OscilloscopeMenu(Frame):
    def __init__(self, master):

        # Allow frame to be set
        Frame.__init__(self, master)

        # Set fontsize
        self.FONTSIZE = 15
        self.FONTSIZE_LARGE = 25

        # Read and set inital settings
        self.Reset()
        self.ReadSettings()
        self.wavetype_options = ['Sine', 'Square', 'DC']
        self.chan_options = [1, 2, 3, 4]

        # Create text Variables
        self.tk_voltage = StringVar(self, self.voltage)
        self.tk_frequency = IntVar(self, self.frequency)
        self.tk_dc_offset = IntVar(self, self.dc_offset)
        self.tk_siggen_selected = IntVar(self, self.detect_siggen(master))
        self.tk_coupling = IntVar(self, self.detect_coupling())
        self.tk_wavetype = StringVar(self, self.wavetype)
        self.tk_chan1 = StringVar(self, self.chan1)
        self.tk_chan2 = StringVar(self, self.chan2)

        # Create buttons and labels
        self.btn_home = Button (self, command=lambda: [self.entry_update_values(), master.switch_frame(MainMenu)], text = 'Home', font=('Helvetica', self.FONTSIZE))
        self.lbl_heading = Label (self, text='Oscilloscope Livescreen', font=('Helvetica', self.FONTSIZE_LARGE), borderwidth=1, relief="solid")
        self.lbl_voltage = Label (self, text='Pk-pk Amplitude (V)', font=('Helvetica', self.FONTSIZE))
        self.lbl_frequency = Label (self, text='Frequency (Hz)', font=('Helvetica', self.FONTSIZE))
        self.lbl_offset = Label (self, text='DC Offset (V)', font=('Helvetica', self.FONTSIZE))
        self.lbl_wavetype = Label (self, text='Wave type', font=('Helvetica', self.FONTSIZE))
        self.lbl_connect_first = Label (self, text='Please connect to an oscilloscope from\nthe connections menu to acquire waveform', fg='red', font=('Helvetica', 10))
        self.lbl_testing = Label (self, text='Loading oscilloscope screen\nPlease wait', font=('Helvetica', 10))
        self.btn_set_siggen = Button (self, state=self.check_connections(master), command=lambda:[self.entry_update_values(), self.set_siggen(master, self.voltage, self.frequency, self.dc_offset, wave_type=self.detect_wavetype())], text = 'Set Signal Generator', height=2, width=18, font=('Helvetica', self.FONTSIZE))
        self.btn_acquire_waveform = Button (self, state=self.check_oscope_connection(master), command=lambda:[self.show_testing_label(), self.update_live_graph(master.oscope, chan1=self.detect_graph(1), chan2=self.detect_graph(2))], text = 'Acquire Waveforms', height=2, width=16, font=('Helvetica', self.FONTSIZE))
        self.btn_reset = Button (self, command=lambda:[self.Reset(), master.switch_frame(OscilloscopeMenu)], text = 'RESET', font=('Helvetica', self.FONTSIZE), fg = 'red')
        self.btn_export = Button (self, state=self.check_export(), command=lambda:[self.export()], text = 'Export', height=2, width=5, font=('Helvetica', self.FONTSIZE))

        # Create entries and radio buttons
        vcmd = self.register(self.callback_num)
        vcmd_neg = self.register(self.callback_num_neg)
        self.entry_voltage = Entry (self, textvariable = self.tk_voltage, validate='key', validatecommand=(vcmd,'%P'), font=('Helvetica', self.FONTSIZE), width=7)
        self.entry_frequency = Entry (self, textvariable = self.tk_frequency, validate='key', validatecommand=(vcmd,'%P'), font=('Helvetica', self.FONTSIZE), width=7)
        self.entry_offset = Entry (self, textvariable = self.tk_dc_offset, validate='key', validatecommand=(vcmd_neg,'%P'), font=('Helvetica', self.FONTSIZE), width=7)
        self.radio_siggen_internal = Radiobutton (self, text = 'Internal signal generator', variable=self.tk_siggen_selected, value=1, command=lambda:[self.select_siggen(master)], font=('Helvetica', self.FONTSIZE))
        self.radio_siggen_external = Radiobutton (self, state=self.check_siggen_connection(master), text = 'External signal generator', variable=self.tk_siggen_selected, value=2, command=lambda:[self.select_siggen(master)], font=('Helvetica', self.FONTSIZE))
        self.radio_coupling_DC = Radiobutton (self, text = 'DC Coupling', variable=self.tk_coupling, value=1, command=lambda:[self.select_coupling()], font=('Helvetica', self.FONTSIZE))
        self.radio_coupling_AC = Radiobutton (self, text = 'AC Coupling', variable=self.tk_coupling, value=2, command=lambda:[self.select_coupling()], font=('Helvetica', self.FONTSIZE))
        self.drop_wavetype = OptionMenu (self, self.tk_wavetype, *self.wavetype_options)
        self.drop_graph1 = OptionMenu (self, self.tk_chan1, *self.chan_options)
        self.drop_graph2 = OptionMenu (self, self.tk_chan2, *self.chan_options)

        # Place widgets
        self.btn_home.place(relx=0.06, rely =0.07, anchor=CENTER)
        self.lbl_heading.place(relx=0.24, rely=0.07, anchor=CENTER)

        self.lbl_voltage.place(relx=0.1, rely=0.17, anchor=CENTER)
        self.entry_voltage.place(relx=0.2, rely=0.17, anchor=CENTER)
        self.lbl_frequency.place(relx=0.1, rely=0.22, anchor=CENTER)
        self.entry_frequency.place(relx=0.2, rely=0.22, anchor=CENTER)
        self.lbl_offset.place(relx=0.1, rely=0.27, anchor=CENTER)
        self.entry_offset.place(relx=0.2, rely=0.27, anchor=CENTER)

        self.lbl_wavetype.place(relx=0.27, rely=0.17, anchor=CENTER)
        self.drop_wavetype.place(relx=0.27, rely=0.22, anchor=CENTER)

        self.radio_siggen_internal.place(relx=0.4, rely=0.17, anchor=CENTER)
        self.radio_siggen_external.place(relx=0.4, rely=0.22, anchor=CENTER)

        self.radio_coupling_DC.place(relx=0.55, rely=0.17, anchor=CENTER)
        self.radio_coupling_AC.place(relx=0.55, rely=0.22, anchor=CENTER)

        self.drop_graph1.place(relx=0.25, rely=0.28, anchor=CENTER)
        self.drop_graph2.place(relx=0.75, rely=0.28, anchor=CENTER)
        
        self.btn_acquire_waveform.place(relx=0.67, rely=0.19, anchor=CENTER)
        self.btn_reset.place(relx=0.92, rely=0.19, anchor=CENTER)
        self.btn_set_siggen.place(relx=0.81, rely=0.19, anchor=CENTER)
        self.lbl_connect_first.place(relx=0.67, rely=0.1, anchor=CENTER)
        self.btn_export.place(relx=0.92, rely=0.06, anchor=CENTER)

        # Draw graphs
        times = [1,2,3,4,5,6,7,8,9,10]
        voltages = [0.1,0.2,0.3,0.2,0.1,0,-0.1,-0.2,-0.3,2]
        self.live_plot = EmbedGraph((times,voltages), heading='Live Oscilloscope', x_label='Voltage (V)', y_label='Time (s)', size = (7.5,5.5))
        self.live_plot.place(relx=0.25, rely=0.65, anchor=CENTER)
        times2 = [1,2,3,4,5,6,7,8,9,10]
        voltages2 = [0.1,0.2,0.3,0.2,0.1,0,-0.1,-0.2,-0.3,-5]
        self.live_plot2 = EmbedGraph((times2,voltages2), heading='Live Oscilloscope', x_label='Voltage (V)', y_label='Time (s)', size = (7.5,5.5))
        self.live_plot2.place(relx=0.75, rely=0.65, anchor=CENTER)

    def show_testing_label(self):
        self.lbl_connect_first["text"] = 'Acquiring waveforms\nPlease wait'

    def update_live_graph(self, oscope, chan1=1, chan2=2):
        times, voltages = acquire_waveform(oscope, chan1)
        self.data_g1 = [times, voltages]
        self.live_plot = EmbedGraph((times,voltages), heading='Current Waveform Channel 1', x_label='Voltage (V)', y_label='Time (s)', size = (7.5,5.5))
        self.live_plot.place(relx=0.25, rely=0.65, anchor=CENTER)
        times2, voltages2 = acquire_waveform(oscope, chan2)
        self.data_g2 = [times2, voltages2]
        self.live_plot2 = EmbedGraph((times2,voltages2), heading='Current Waveform Channel 2', x_label='Voltage (V)', y_label='Time (s)', size = (7.5,5.5))
        self.live_plot2.place(relx=0.75, rely=0.65, anchor=CENTER)
        self.lbl_connect_first["text"] = ''

    def check_export(self):
        """Checks there is data to be exported"""
        if self.data_g1 != None and self.data_g2 != None:
            return NORMAL
        else:
            return DISABLED

    def export(self):
        """Exports data to a .csv file"""
        with open('Oscilloscope_Graph1.csv', 'wb') as g1:
            writer = csv.writer(g1)
            writer.writerows(self.data_g1)
        with open('Oscilloscope_Graph1.csv', 'wb') as g2:
            writer = csv.writer(g2)
            writer.writerows(self.data_g2)

    def check_connections(self, master):
        if master.siggen_setting == None:
            state = self.check_oscope_connection(master)
        else:
            state = self.check_siggen_connection(master)
        
        return state

    def check_oscope_connection(self, master):
        """Checks if oscope is connected"""
        if master.oscope != None:
            self.lbl_connect_first['text']=""
            return NORMAL            
        else:
            self.lbl_connect_first['text']='Please connect to an oscilloscope from\nthe connections menu to acquire waveform'
            return DISABLED

    def check_siggen_connection(self, master):
        """Checks if oscope is connected"""
        if master.siggen != None:
            return NORMAL            
        else:
            return DISABLED

    def set_siggen(self, master, voltage, frequency, offset=0, wave_type='Sine'):
        if master.siggen_setting == None:
            oscope_set_siggen(master.oscope, voltage, frequency, offset=offset, wave_type=wave_type)
        elif master.siggen_setting != None:
            siggen_set_siggen(master.siggen, voltage, frequency, offset=offset, wave_type=wave_type)

    def detect_siggen(self, master):
        if master.siggen_setting == None:
            return 1
        else:
            return 2

    def select_siggen(self, master):
        if self.tk_siggen_selected.get() == 2:
            master.siggen_setting = master.siggen
        else:
            master.siggen_setting = None

    def detect_coupling(self):
        if self.coupling == 'DC':
            return 1
        else:
            return 2

    def select_coupling(self):
        if self.tk_coupling.get() == 2:
            self.coupling = 'AC'
        else:
            self.coupling = 'DC'

    def detect_wavetype(self):
        if self.tk_siggen_selected.get() == 1:
            if self.wavetype == 'Sine':
                return 'SIN'
            elif self.wavetype == 'Square':
                return 'SQU'
            elif self.wavetype == 'DC':
                return 'DC'
        else:
            if self.wavetype == 'Sine':
                return 'SINE'
            elif self.wavetype == 'Square':
                return 'SQUARE'
            elif self.wavetype == 'DC':
                return 'DC'

    def detect_graph(self, graph_no):
        if graph_no == 1:
            return self.tk_chan1.get()
        elif graph_no == 2:
            return self.tk_chan2.get()

    # Call backs to check data entry
    def callback_num(self, input):
        """Only numeric input allowed"""
        if input.isnumeric() or input == '' or input.replace(".", '', 1).isnumeric():
            return True
        else:
            return False          

    def callback_num_neg(self, input):
        """Only numeric input allowed (including negative numbers)"""
        if input.isnumeric() or input == '' or input.replace(".", '', 1).isnumeric():
            return True
        elif input.startswith("-") and (input[1:].isnumeric() or input[1:] == '' or input[1:].replace(".", '').isnumeric()):
            return True
        else:
            return False  

    def convert_num(self, data):
        """Converts string to int if it can, otherwise to float"""
        try:
            val = int(data)
        except:
            val = float(data)
        return val

    ###########
    """Read and write functions"""
    ###########
    def entry_update_values(self):
        self.voltage = self.convert_num(self.entry_voltage.get())
        self.frequency = self.convert_num(self.entry_frequency.get())
        self.dc_offset = self.convert_num(self.entry_offset.get())
        self.wavetype = self.tk_wavetype.get()
        self.chan1 = self.tk_chan1.get()
        self.chan2 = self.tk_chan2.get()
        self.WriteSettings()
        
    def WriteSettings(self):
        """Writes the test settings to the save file"""
        test_settings_file = shelve.open("Data/live_oscope_settings",writeback=True)
        test_settings_file["voltage"] = self.voltage
        test_settings_file["frequency"] = self.frequency
        test_settings_file["dc_offset"] = self.dc_offset
        test_settings_file["coupling"] = self.coupling
        test_settings_file["wavetype"] = self.wavetype
        test_settings_file["graph1"] = self.chan1
        test_settings_file["graph2"] = self.chan2
        test_settings_file.close()

    def ReadSettings(self):
        """Reads the test settings"""
        test_settings_file = shelve.open("Data/live_oscope_settings")
        self.voltage = test_settings_file["voltage"]
        self.frequency = test_settings_file["frequency"]
        self.dc_offset = test_settings_file["dc_offset"]
        self.coupling = test_settings_file["coupling"]
        self.wavetype = test_settings_file["wavetype"]
        self.chan1 = test_settings_file["graph1"]
        self.chan2 = test_settings_file["graph2"]
        test_settings_file.close()

    def Reset(self):
        """Resets settings to default"""
        self.voltage = 1
        self.frequency = 1000
        self.dc_offset = 0
        self.coupling = 'DC'
        self.wavetype = 'Sine'
        self.chan1 = 1
        self.chan2 = 2
        self.data_g1 = None
        self.data_g2 = None

class ConnectionMenu(Frame):
    def __init__(self, master):

        # Allow frame to be set
        Frame.__init__(self, master)

        # Set fontsize
        self.FONTSIZE = 20
        self.FONTSIZE_LARGE = 25

        # Read Initial Settings
        self.ReadSettings_Connect()

        # Create text variables
        self.tk_oscope = StringVar(self, self.oscilloscope1_string)
        self.tk_siggen = StringVar(self, self.signalgenerator1_string)
        self.tk_multim = StringVar(self, self.multimeter1_string)
        self.tk_powers = StringVar(self, self.powersupply1_string)

        # Create buttons and labels
        self.btn_home = Button (self, command=lambda: [self.entry_update_connections(), master.switch_frame(MainMenu)], text = 'Home', font=('Helvetica', 15))
        self.lbl_heading = Label (self, text='Connections Menu', font=('Helvetica', self.FONTSIZE_LARGE), borderwidth=1, relief="solid")
        self.lbl_oscope = Label (self, text='Oscilloscope:', font=('Helvetica', self.FONTSIZE))
        self.lbl_siggen = Label (self, text='Signal Generator:', font=('Helvetica', self.FONTSIZE))
        self.lbl_multim = Label (self, text='Multimeter:', font=('Helvetica', self.FONTSIZE))
        self.lbl_powers = Label (self, text='Power Supply:', font=('Helvetica', self.FONTSIZE))
        self.lbl_oscope_connect = Label (self, text='Disconnected', fg = 'red', font=('Helvetica', self.FONTSIZE))
        self.lbl_siggen_connect = Label (self, text='Disconnected', fg = 'red', font=('Helvetica', self.FONTSIZE))
        self.lbl_multim_connect = Label (self, text='Disconnected', fg = 'red', font=('Helvetica', self.FONTSIZE))
        self.lbl_powers_connect = Label (self, text='Disconnected', fg = 'red', font=('Helvetica', self.FONTSIZE))

        self.btn_connect_all = Button (self, command=lambda:[self.connect_all(master)], text = 'Connect to all', height=2, width=15, font=('Helvetica', self.FONTSIZE))
        self.btn_reset = Button (self, command=lambda:[self.Reset(), master.switch_frame(ConnectionMenu)], text = 'RESET', font=('Helvetica', self.FONTSIZE), fg = 'red')

        # Create entries
        self.entry_oscope = Entry (self, textvariable = self.tk_oscope, font=('Helvetica', self.FONTSIZE))
        self.entry_siggen = Entry (self, textvariable = self.tk_siggen, font=('Helvetica', self.FONTSIZE))
        self.entry_multim = Entry (self, textvariable = self.tk_multim, font=('Helvetica', self.FONTSIZE))
        self.entry_powers = Entry (self, textvariable = self.tk_powers, font=('Helvetica', self.FONTSIZE))

        # Place buttons, labels and entries
        self.btn_home.place(relx=0.06, rely =0.07, anchor=CENTER)
        self.lbl_heading.place(relx=0.24, rely=0.07, anchor=CENTER)

        self.lbl_oscope.place(relx=0.1, rely=0.2, anchor=CENTER)
        self.entry_oscope.place(relx=0.3, rely=0.2, anchor=CENTER)
        self.lbl_siggen.place(relx=0.1, rely=0.3, anchor=CENTER)
        self.entry_siggen.place(relx=0.3, rely=0.3, anchor=CENTER)
        self.lbl_multim.place(relx=0.1, rely=0.4, anchor=CENTER)
        self.entry_multim.place(relx=0.3, rely=0.4, anchor=CENTER)
        self.lbl_powers.place(relx=0.1, rely=0.5, anchor=CENTER)
        self.entry_powers.place(relx=0.3, rely=0.5, anchor=CENTER)

        self.lbl_oscope_connect.place(relx=0.5, rely=0.2, anchor=CENTER)
        self.lbl_siggen_connect.place(relx=0.5, rely=0.3, anchor=CENTER)
        self.lbl_multim_connect.place(relx=0.5, rely=0.4, anchor=CENTER)
        self.lbl_powers_connect.place(relx=0.5, rely=0.5, anchor=CENTER)

        self.btn_connect_all.place(relx=0.5, rely=0.7, anchor=CENTER)
        self.btn_reset.place(relx=0.1, rely=0.7, anchor=CENTER)

        self.connect_all(master)

    def connect_all(self, master):
        master.oscope = connect_instrument(self.oscilloscope1_string)
        master.siggen = connect_instrument(self.signalgenerator1_string)
        master.mmeter = connect_instrument(self.multimeter1_string)
        master.powers = connect_instrument(self.powersupply1_string)

        instr = [master.oscope, master.siggen, master.mmeter, master.powers]
        instr_lbl = [self.lbl_oscope_connect, self.lbl_siggen_connect, self.lbl_multim_connect, self.lbl_powers_connect]
        for i in range(4):
            if instr[i] != None:
                self.change_connect_state(instr_lbl[i], 'On')
            else:
                self.change_connect_state(instr_lbl[i], 'Off')


    def change_connect_state(self, button, state):
        """Changes the connection state"""
        
        if state == 'On':
            button['fg'] = 'green'
            button['text'] = 'Connected'
        else:
            button['fg'] = 'red'
            button['text'] = 'Not connected'

    ###########
    """Read and write functions"""
    ###########
    def entry_update_connections(self):
        self.oscilloscope1_string = self.entry_oscope.get()
        self.multimeter1_string = self.entry_multim.get()
        self.signalgenerator1_string = self.entry_siggen.get()
        self.powersupply1_string = self.entry_powers.get()
        self.WriteSettings_Connect()

    def WriteSettings_Connect(self):
        """Writes the test settings to the save file"""
        connection_settings_file = shelve.open("Data/test_settings",writeback=True)
        connection_settings_file["oscilloscope1_string"] = self.oscilloscope1_string
        connection_settings_file["multimeter1_string"] = self.multimeter1_string
        connection_settings_file["signalgenerator1_string"] = self.signalgenerator1_string
        connection_settings_file["powersupply1_string"] = self.powersupply1_string
        connection_settings_file.close()

    def ReadSettings_Connect(self):
        """Reads the test settings"""
        connection_settings_file = shelve.open("Data/test_settings") 
        self.oscilloscope1_string = connection_settings_file["oscilloscope1_string"]
        self.multimeter1_string = connection_settings_file["multimeter1_string"]
        self.signalgenerator1_string = connection_settings_file["signalgenerator1_string"]
        self.powersupply1_string = connection_settings_file["powersupply1_string"]
        connection_settings_file.close()

    def Reset(self):
        """Resets settings to default"""
        # Set initial settings
        self.oscilloscope1_string = 'TCPIP0::192.168.1.2::inst0::INSTR'
        self.multimeter1_string = 'TCPIP0::192.168.1.5::5025::SOCKET'
        self.signalgenerator1_string = 'TCPIP0::192.168.1.3::inst0::INSTR'
        self.powersupply1_string = 'TCPIP0::192.168.1.4::inst0::INSTR'
        self.WriteSettings_Connect()

class DemoMenu(Frame):
    def __init__(self, master):

        # Allow frame to be set
        Frame.__init__(self, master)

        # Set fontsize
        self.FONTSIZE = 15
        self.FONTSIZE_LARGE = 25

        # Read and set inital settings
        self.siggen_v = 0.5
        self.frequency = 1000
        self.powers_pos = 7
        self.powers_neg = 7
        self.powers_v = 7
        self.demo_stage = 1
        self.demo_parts = [7,12,17]

        # Create text Variables
        self.tk_siggen_selected = IntVar(self, self.detect_siggen(master))

        # Create buttons and labels
        self.btn_home = Button (self, command=lambda: [master.switch_frame(MainMenu)], text = 'Home', font=('Helvetica', self.FONTSIZE))
        self.lbl_heading = Label (self, text='Op-Amp Demo', font=('Helvetica', self.FONTSIZE_LARGE), borderwidth=1, relief="solid")

        self.lbl_siggen_v = Label (self, text= 'Signal Generator Pk-pk (V):', font=('Helvetica', self.FONTSIZE))
        self.lbl_frequency = Label (self, text='Frequency (Hz):', font=('Helvetica', self.FONTSIZE))
        self.lbl_powers_pos = Label (self, text='Power supply + (V):', font=('Helvetica', self.FONTSIZE))
        self.lbl_powers_neg = Label (self, text='Power supply - (V):', font=('Helvetica', self.FONTSIZE))

        self.lbl_siggen_v_val = Label (self, text=f"{self.siggen_v}", font=('Helvetica', self.FONTSIZE))
        self.lbl_frequency_val = Label (self, text=f"{self.frequency}", font=('Helvetica', self.FONTSIZE))
        self.lbl_powers_pos_val = Label (self, text=f"{self.powers_v}", font=('Helvetica', self.FONTSIZE))
        self.lbl_powers_neg_val = Label (self, text=f"-{self.powers_v}", font=('Helvetica', self.FONTSIZE))

        self.lbl_connect_first = Label (self, text='Please connect to an oscilloscope, power supply and multimeter\nfrom the connections menu to run the op-amp demo', fg='red', font=('Helvetica', 10))
        self.btn_reset = Button (self, command=lambda:[self.Reset(), master.switch_frame(DemoMenu)], text = 'Restart demo',  height=2, font=('Helvetica', self.FONTSIZE), fg = 'red')
        self.btn_next = Button (self, command=lambda:[self.demo_stage_change(master, 'next'), self.demo_show_info(), self.demo_run(master)], text = '→', font=('Helvetica', self.FONTSIZE+10))
        self.btn_back = Button (self, command=lambda:[self.demo_stage_change(master, 'back'), self.demo_show_info(), self.demo_run(master)], text = '←', font=('Helvetica', self.FONTSIZE+10))
        self.btn_next_big = Button (self, command=lambda:[self.demo_stage_change(master, 'next'), self.demo_show_info(), self.demo_run(master)], text = 'Next', height=2, width=7, font=('Helvetica', self.FONTSIZE), fg = 'green')

        self.radio_siggen_internal = Radiobutton (self, text = 'Internal signal generator', variable=self.tk_siggen_selected, value=1, command=lambda:[self.select_siggen(master)], font=('Helvetica', self.FONTSIZE))
        self.radio_siggen_external = Radiobutton (self, state=self.check_siggen_connection(master), text = 'External signal generator', variable=self.tk_siggen_selected, value=2, command=lambda:[self.select_siggen(master)], font=('Helvetica', self.FONTSIZE))

        self.lbl_stage_num = Label (self, text=f'{self.demo_stage}/21', font=('Helvetica', self.FONTSIZE))

        self.lbl_info_1 = Label (self, text="", font=('Helvetica', self.FONTSIZE))
        self.lbl_info_2 = Label (self, text="", font=('Helvetica', self.FONTSIZE))
        self.lbl_info_3 = Label (self, text="", font=('Helvetica', self.FONTSIZE))
        self.lbl_info_4 = Label (self, text="", font=('Helvetica', self.FONTSIZE))
        self.lbl_info_5 = Label (self, text="", font=('Helvetica', self.FONTSIZE))
        self.img = self.load_image("Images\op_amp_circ2.png", new_size = (750, 400))
        self.lbl_img = Label(self, image = self.img)

        # Place widgets
        self.btn_home.place(relx=0.06, rely =0.07, anchor=CENTER)
        self.lbl_heading.place(relx=0.18, rely=0.07, anchor=CENTER)

        self.lbl_siggen_v.place(relx=0.33, rely=0.17, anchor=CENTER)
        self.lbl_siggen_v_val.place(relx=0.43, rely=0.17, anchor=CENTER)
        self.lbl_frequency.place(relx=0.33, rely=0.22, anchor=CENTER)
        self.lbl_frequency_val.place(relx=0.43, rely=0.22, anchor=CENTER)
        self.lbl_powers_pos.place(relx=0.6, rely=0.17, anchor=CENTER)
        self.lbl_powers_pos_val.place(relx=0.7, rely=0.17, anchor=CENTER)
        self.lbl_powers_neg.place(relx=0.6, rely=0.22, anchor=CENTER)
        self.lbl_powers_neg_val.place(relx=0.7, rely=0.22, anchor=CENTER)
        
        self.btn_back.place(relx=0.35, rely=0.07, anchor=CENTER)
        self.lbl_stage_num.place(relx=0.40, rely=0.07, anchor=CENTER)
        self.btn_next.place(relx=0.45, rely=0.07, anchor=CENTER)
        self.btn_reset.place(relx=0.65, rely=0.07, anchor=CENTER)
        self.btn_next_big.place(relx=0.9, rely=0.87, anchor=CENTER)
        self.lbl_connect_first.place(relx=0.85, rely=0.07, anchor=CENTER)        

        self.radio_siggen_internal.place(relx=0.12, rely=0.17, anchor=CENTER)
        self.radio_siggen_external.place(relx=0.12, rely=0.22, anchor=CENTER)

        self.demo_show_info()

    def demo_stage_change(self, master, direction):
        """Changes the demo stage"""
        if direction == "back" and self.demo_stage != 1:
            self.demo_stage -= 1
        elif direction == "next" and self.demo_stage < 21:
            self.demo_stage += 1
        self.lbl_stage_num["text"] = f'{self.demo_stage}/21'

        if self.demo_stage > self.demo_parts[0]-2:
            self.btn_next['state']=self.check_connections(master)
            self.btn_next_big['state']=self.check_connections(master)
        else:
            self.btn_next['state']=NORMAL
            self.btn_next_big['state']=NORMAL
        if self.demo_stage > self.demo_parts[0]:
            self.btn_back['state']=self.check_connections(master)
        else:
            self.btn_back['state']=NORMAL

        self.demo_changesettings()

    def reset_labels(self):
        self.lbl_info_1["text"] = ''
        self.lbl_info_2["text"] = ''
        self.lbl_info_3["text"] = ''
        self.lbl_info_4["text"] = ''
        self.lbl_info_5["text"] = ''
        self.lbl_img["image"] = ''
        self.lbl_info_1.place(relx=1, rely=1, anchor=CENTER)
        self.lbl_info_2.place(relx=1, rely=1, anchor=CENTER)
        self.lbl_info_3.place(relx=1, rely=1, anchor=CENTER)
        self.lbl_info_4.place(relx=1, rely=1, anchor=CENTER)
        self.lbl_info_5.place(relx=1, rely=1, anchor=CENTER)
        self.lbl_img.place(relx=1, rely=1, anchor=CENTER)

    def demo_show_info(self):
        self.reset_labels()
        if self.demo_stage == 1:
            self.lbl_info_1["text"] = "This demonstration is designed to teach you about saturation."
            self.lbl_info_2["text"] = "The circuit below shows the inverting op-amp circuit which will be used to carry out the following demonstration."
            self.lbl_img["image"] = self.load_image("Images\op_amp_circ2.png", new_size = (750, 400))
            self.lbl_info_1.place(relx=0.5, rely=0.30, anchor=CENTER)
            self.lbl_info_2.place(relx=0.5, rely=0.35, anchor=CENTER)
            self.lbl_img.place(relx=0.5, rely=0.65, anchor=CENTER)
        elif self.demo_stage == 2:
            self.lbl_info_1["text"] = "Connect the power supply as shown."
            self.lbl_info_2["text"] = "Connect the positive side of channel 1 to Vcc and the negative side of channel 2 to -Vcc."
            self.lbl_img["image"] = self.load_image("Images\op_amp_circ.png", new_size = (750, 400))
            self.lbl_info_1.place(relx=0.5, rely=0.30, anchor=CENTER)
            self.lbl_info_2.place(relx=0.5, rely=0.87, anchor=CENTER)
            self.lbl_img.place(relx=0.5, rely=0.59, anchor=CENTER)
        elif self.demo_stage == 3:
            self.lbl_info_1["text"] = "Connect the multimeter as shown."
            self.lbl_info_2["text"] = "The multimeter will be used to check the voltage of the power supply."
            self.lbl_img["image"] = self.load_image("Images\op_amp_circ.png", new_size = (750, 400))
            self.lbl_info_1.place(relx=0.5, rely=0.30, anchor=CENTER)
            self.lbl_info_2.place(relx=0.5, rely=0.87, anchor=CENTER)
            self.lbl_img.place(relx=0.5, rely=0.59, anchor=CENTER)
        elif self.demo_stage == 4:
            self.lbl_info_1["text"] = "The gain can be predicted using the formula:"
            self.lbl_img["image"] = self.load_image("Images\eq_inv_gain_r.png", new_size = (700, 300))
            self.lbl_info_1.place(relx=0.5, rely=0.35, anchor=CENTER)
            self.lbl_img.place(relx=0.5, rely=0.59, anchor=CENTER)
        elif self.demo_stage == 5:
            self.lbl_info_1["text"] = "Connect the signal generator as shown."
            self.lbl_img["image"] = self.load_image("Images\op_amp_circ.png", new_size = (750, 400))
            self.lbl_info_1.place(relx=0.5, rely=0.30, anchor=CENTER)
            self.lbl_img.place(relx=0.5, rely=0.59, anchor=CENTER)
        elif self.demo_stage == 6:
            self.lbl_info_1["text"] = "The gain can be measured by measuring the input and output voltage and using the formula:"
            self.lbl_img["image"] = self.load_image("Images\eq_inv_gain_v.png", new_size = (500, 300))
            self.lbl_info_1.place(relx=0.5, rely=0.35, anchor=CENTER)
            self.lbl_img.place(relx=0.5, rely=0.59, anchor=CENTER)
        elif self.demo_stage == 7:
            self.lbl_info_1["text"] = f"1. The power supply is set to output + and - {self.powers_v}V."
            self.lbl_info_1.place(relx=0.5, rely=0.30, anchor=CENTER)
        elif self.demo_stage == 8:
            self.lbl_info_1["text"] = "2. Check the power supply output with the mulitmeter."
            self.lbl_info_1.place(relx=0.5, rely=0.30, anchor=CENTER)
        elif self.demo_stage == 9:
            self.lbl_info_1["text"] = "3. Calculate the predicted gain."
            self.lbl_info_1.place(relx=0.5, rely=0.30, anchor=CENTER)
        elif self.demo_stage == 10:
            self.lbl_info_1["text"] = f"4. The signal generator is set to output {self.siggen_v}V."
            self.lbl_info_1.place(relx=0.5, rely=0.30, anchor=CENTER)
        elif self.demo_stage == 11:
            self.lbl_info_1["text"] = "5. Measure the actual gain and compare with the predicted value."
            self.lbl_info_1.place(relx=0.5, rely=0.30, anchor=CENTER)
        elif self.demo_stage == 12:
            self.lbl_info_1["text"] = f"1. The power supply is set to output + and - {self.powers_v}V."
            self.lbl_info_1.place(relx=0.5, rely=0.30, anchor=CENTER)
        elif self.demo_stage == 13:
            self.lbl_info_1["text"] = "2. Check the power supply output with the mulitmeter."
            self.lbl_info_1.place(relx=0.5, rely=0.30, anchor=CENTER)
        elif self.demo_stage == 14:
            self.lbl_info_1["text"] = "3. Calculate the predicted gain."
            self.lbl_info_1.place(relx=0.5, rely=0.30, anchor=CENTER)
        elif self.demo_stage == 15:
            self.lbl_info_1["text"] = f"4. The signal generator is set to output {self.siggen_v}V."
            self.lbl_info_1.place(relx=0.5, rely=0.30, anchor=CENTER)
        elif self.demo_stage == 16:
            self.lbl_info_1["text"] = "5. Measure the actual gain and compare with the predicted value."
            self.lbl_info_1.place(relx=0.5, rely=0.30, anchor=CENTER)
        elif self.demo_stage == 17:
            self.lbl_info_1["text"] = f"1. The power supply is set to output + and - {self.powers_v}V."
            self.lbl_info_1.place(relx=0.5, rely=0.30, anchor=CENTER)
        elif self.demo_stage == 18:
            self.lbl_info_1["text"] = "2. Check the power supply output with the mulitmeter."
            self.lbl_info_1.place(relx=0.5, rely=0.30, anchor=CENTER)
        elif self.demo_stage == 19:
            self.lbl_info_1["text"] = "3. Calculate the predicted gain."
            self.lbl_info_1.place(relx=0.5, rely=0.30, anchor=CENTER)
        elif self.demo_stage == 20:
            self.lbl_info_1["text"] = f"4. The signal generator is set to output {self.siggen_v}V."
            self.lbl_info_1.place(relx=0.5, rely=0.30, anchor=CENTER)
        elif self.demo_stage == 21:
            self.lbl_info_1["text"] = "5. Measure the actual gain and compare with the predicted value."
            self.lbl_info_1.place(relx=0.5, rely=0.30, anchor=CENTER)

    def demo_run(self, master):
        if self.demo_stage in self.demo_parts: # Set powers supply
            print("1")
            #powers_set_powers(master.powers, self.powers_v, 3, 1) # Connect to positive terminal of chan1
            #powers_set_powers(master.powers, -self.powers_v, 3, 2) # # Connect to negative terminal of chan1
            # Connect the unused ports for chan1 and chan2 of power supply together to form ground
        elif self.demo_stage-1 in self.demo_parts: # Check power supply with multimeter
            print("2")
            #mmeter_v = mmeter_get_voltage(master.mmeter) # Check power supply with multi meter
            #print("Power supply V", self.powers_v)
            #print("Power supply V", self.siggen_v)
            #print("Multimeter V", mmeter_v)
        elif self.demo_stage-2 in self.demo_parts: # Calculate the predicted gain
            print("3")
            # Set gain to be 10
            #gain_predicted = self.calc_gain(1,10)
            #print("Predicted gain", gain_predicted)
        elif self.demo_stage-3 in self.demo_parts: # Set the signal generator
            print("4")
            #self.set_siggen(master, self.siggen_v, self.frequency)
            #Vin = full_measure(master.oscope, 1, 'PEAK', 1) # Vin
            #Vout = full_measure(master.oscope, 2, 'PEAK', 2) # Vout
        elif self.demo_stage-4 in self.demo_parts: # Measure the actual gain - comment on what this means
            print("5")
            #gain_measured = self.calc_gain(Vout/Vin)
            #print("Measured gain", gain_measured)
            # Gain should 10 as predicted, however, this is limited by the voltage of the power supply
        else:
            pass

    def demo_changesettings(self):
        if self.demo_stage == self.demo_parts[0] or self.demo_stage == self.demo_parts[1]-1:
            self.siggen_v = 0.5
            self.powers_v = 7
            self.powers_pos = 7
            self.powers_neg = -7
            self.lbl_siggen_v_val['text'] = f"{self.siggen_v}"
            self.lbl_frequency_val['text'] = f"{self.frequency}"
            self.lbl_powers_pos_val['text'] = f"{self.powers_v}"
            self.lbl_powers_neg_val['text'] = f"-{self.powers_v}"
        elif self.demo_stage == self.demo_parts[1] or self.demo_stage == self.demo_parts[2]-1:
            self.siggen_v = 1
            self.powers_v = 7
            self.powers_pos = 7
            self.powers_neg = -7
            self.lbl_siggen_v_val['text'] = f"{self.siggen_v}"
            self.lbl_frequency_val['text'] = f"{self.frequency}"
            self.lbl_powers_pos_val['text'] = f"{self.powers_v}"
            self.lbl_powers_neg_val['text'] = f"-{self.powers_v}"
        elif self.demo_stage == self.demo_parts[2]:
            self.siggen_v = 1
            self.powers_v = 15
            self.powers_pos = 15
            self.powers_neg = -15
            self.lbl_siggen_v_val['text'] = f"{self.siggen_v}"
            self.lbl_frequency_val['text'] = f"{self.frequency}"
            self.lbl_powers_pos_val['text'] = f"{self.powers_v}"
            self.lbl_powers_neg_val['text'] = f"-{self.powers_v}"

    def calc_gain(self, input, output):
        gain = output/input
        return gain

    def set_siggen(self, master, voltage, frequency, offset=0, wave_type='Sine'):
        if master.siggen_setting == None:
            oscope_set_siggen(master.oscope, voltage, frequency, offset=offset, wave_type=wave_type)
        elif master.siggen_setting != None:
            siggen_set_siggen(master.siggen, voltage, frequency, offset=offset, wave_type=wave_type)

    def check_connections(self, master):
        if master.siggen_setting == None:
            state = self.check_oscope_connection(master) and self.check_powers_connection(master) and self.check_mmeter_connection(master)
        else:
            state = self.check_siggen_connection(master) and self.check_oscope_connection(master) and self.check_powers_connection(master) and self.check_mmeter_connection(master)

        return state

    def check_oscope_connection(self, master):
        """Checks if oscope is connected"""
        if master.oscope != None:
            return NORMAL            
        else:
            return DISABLED

    def check_siggen_connection(self, master):
        """Checks if oscope is connected"""
        if master.siggen != None:
            return NORMAL            
        else:
            return DISABLED

    def check_powers_connection(self, master):
        """Checks if oscope is connected"""
        if master.powers != None:
            return NORMAL            
        else:
            return DISABLED
    
    def check_mmeter_connection(self, master):
        """Checks if oscope is connected"""
        if master.mmeter != None:
            return NORMAL            
        else:
            return DISABLED

    def detect_siggen(self, master):
        if master.siggen_setting == None:
            return 1
        else:
            return 2

    def select_siggen(self, master):
        if self.tk_siggen_selected.get() == 2:
            master.siggen_setting = master.siggen
        else:
            master.siggen_setting = None

    def convert_num(self, data):
        """Converts string to int if it can, otherwise to float"""
        try:
            val = int(data)
        except:
            val = float(data)
        return val
    
    def load_image(self, image, new_size):
        self.img = ImageTk.PhotoImage(Image.open(image).resize(new_size, Image.ANTIALIAS))
        return self.img
    
    def Reset(self):
        """Resets demo to first stage"""
        self.demo_stage = 1


if __name__ == "__main__":
    app = InstrumentationControlApp()
    width= app.winfo_screenwidth()               
    height= app.winfo_screenheight()               
    app.geometry(f"{width}x{height}")
    app.title('Instrumentation Control')
    app.state('zoomed')
    app.mainloop()
