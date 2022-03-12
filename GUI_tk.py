from cgitb import text
from operator import neg
from tkinter import *
import shelve
from turtle import color
import InstrumentControl
from DataManagement import *
from GraphTools import EmbedGraph

oscope = None

class InstrumentationControlApp(Tk):
    def __init__(self):
        Tk.__init__(self)
        self._frame = None
        global oscope 
        self.oscope = oscope
        self.switch_frame(MainMenu)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        global oscope
        oscope = self.oscope
        self._frame.pack(fill = "both", expand = TRUE)

class MainMenu(Frame):
    def __init__(self, master):

        # Allow frame to be set
        Frame.__init__(self, master)

         # Set colours
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
        self.btn_testmenu = Button (self, command=lambda: master.switch_frame(TestMenu), text = 'Test Circuit', height=2, width=15, font=('Helvetica', self.FONTSIZE))
        self.btn_connectionmenu = Button (self, command=lambda: master.switch_frame(ConnectionMenu), text = 'Connection Menu', height=2, width=15, font=('Helvetica', self.FONTSIZE))

        # Place buttons and labels
        self.lbl_heading.place(relx=0.5, rely =0.2, anchor=CENTER)
        self.btn_testmenu.place(relx=0.4, rely =0.4, anchor=CENTER)
        self.btn_connectionmenu.place(relx=0.6, rely =0.4, anchor=CENTER)

class TestMenu(Frame):
    def __init__(self, master):

        # Allow frame to be set
        Frame.__init__(self, master)

         # Set colours
        self.LBLUE = (12, 181, 249)
        self.FONTSIZE = 20
        self.FONTSIZE_LARGE = 40

        # Read inital settings
        self.ReadSettings()

        # Create text Variables
        self.tk_voltages = StringVar(self, self.voltages)
        self.tk_start_frequency = IntVar(self, self.start_frequency)
        self.tk_end_frequency = IntVar(self, self.end_frequency)
        self.tk_frequency_step = IntVar(self, self.frequency_step)
        self.tk_dc_offset = IntVar(self, self.dc_offset)
        self.tk_meas_type = StringVar(self, self.meas_type)
        self.tk_cutoff_dB = IntVar(self, self.cutoff_dB)

        # Create buttons and labels
        self.btn_home = Button (self, command=lambda: [self.entry_update_values(), master.switch_frame(MainMenu)], text = 'Home', font=('Helvetica', self.FONTSIZE))
        self.lbl_heading = Label (self, text='Circuit Testing Menu', font=('Helvetica', self.FONTSIZE_LARGE))
        self.lbl_voltages = Label (self, text='Voltages (V)', font=('Helvetica', self.FONTSIZE))
        self.lbl_startfreq = Label (self, text='Start Frequency (Hz)', font=('Helvetica', self.FONTSIZE))
        self.lbl_endfreq = Label (self, text='End Frequency (Hz)', font=('Helvetica', self.FONTSIZE))
        self.lbl_freqsteps = Label (self, text='Frequencies per decade', font=('Helvetica', self.FONTSIZE))
        self.lbl_offset = Label (self, text='DC Offset (V)', font=('Helvetica', self.FONTSIZE))
        self.lbl_meastype = Label (self, text='Measuring Type', font=('Helvetica', self.FONTSIZE))
        self.lbl_cutoff = Label (self, text='Cutoff (dB)', font=('Helvetica', self.FONTSIZE))
        self.lbl_connect_first = Label (self, text='Please connect to an oscillscope first\nfrom the connections menu', fg='red', font=('Helvetica', 10))
        self.btn_testcircuit = Button (self, state=self.check_oscope_connection(master), command=lambda:[self.update_live_graph(), self.change_state(self.btn_acquire_freqresp)], text = 'Test Circuit', height=2, width=15, font=('Helvetica', self.FONTSIZE))
        self.btn_acquire_freqresp = Button (self, state=DISABLED, command=lambda:[self.update_freq_resp_plot()], text = 'Acquire\nFrequency Response', height=2, width=17, font=('Helvetica', self.FONTSIZE))
        self.btn_reset = Button (self, command=lambda:[self.Reset(), master.switch_frame(TestMenu)], text = 'RESET', font=('Helvetica', self.FONTSIZE), fg = 'red')

        # Create entries
        vcmd = self.register(self.callback_num)
        vcmd_neg = self.register(self.callback_num_neg)
        self.entry_voltages = Entry (self, textvariable = self.tk_voltages, validate='key', validatecommand=(vcmd,'%P'), font=('Helvetica', self.FONTSIZE))
        self.entry_startfreq = Entry (self, textvariable = self.tk_start_frequency, validate='key', validatecommand=(vcmd,'%P'), font=('Helvetica', self.FONTSIZE))
        self.entry_endfreq = Entry (self, textvariable = self.tk_end_frequency, validate='key', validatecommand=(vcmd,'%P'), font=('Helvetica', self.FONTSIZE))
        self.entry_freqsteps = Entry (self, textvariable = self.tk_frequency_step, validate='key', validatecommand=(vcmd,'%P'), font=('Helvetica', self.FONTSIZE))
        self.entry_offset = Entry (self, textvariable = self.tk_dc_offset, validate='key', validatecommand=(vcmd,'%P'), font=('Helvetica', self.FONTSIZE))
        self.entry_meastype = Entry (self, textvariable = self.tk_meas_type, validate='key', validatecommand=(vcmd,'%P'), font=('Helvetica', self.FONTSIZE))
        self.entry_cutoff = Entry (self, textvariable = self.tk_cutoff_dB, validate='key', validatecommand=(vcmd_neg,'%P'), font=('Helvetica', self.FONTSIZE))

        # Place buttons, labels and entries
        self.btn_home.place(relx=0.1, rely =0.1, anchor=CENTER)

        self.lbl_voltages.place(relx=0.1, rely=0.2, anchor=CENTER)
        self.entry_voltages.place(relx=0.3, rely=0.2, anchor=CENTER)
        self.lbl_startfreq.place(relx=0.1, rely=0.25, anchor=CENTER)
        self.entry_startfreq.place(relx=0.3, rely=0.25, anchor=CENTER)
        self.lbl_endfreq.place(relx=0.1, rely=0.3, anchor=CENTER)
        self.entry_endfreq.place(relx=0.3, rely=0.3, anchor=CENTER)
        self.lbl_freqsteps.place(relx=0.1, rely=0.35, anchor=CENTER)
        self.entry_freqsteps.place(relx=0.3, rely=0.35, anchor=CENTER)
        self.lbl_offset.place(relx=0.1, rely=0.4, anchor=CENTER)
        self.entry_offset.place(relx=0.3, rely=0.4, anchor=CENTER)
        self.lbl_meastype.place(relx=0.1, rely=0.45, anchor=CENTER)
        self.entry_meastype.place(relx=0.3, rely=0.45, anchor=CENTER)
        self.lbl_cutoff.place(relx=0.1, rely=0.55, anchor=CENTER)
        self.entry_cutoff.place(relx=0.3, rely=0.55, anchor=CENTER)

        self.lbl_heading.place(relx=0.35, rely=0.1, anchor=CENTER)
        self.btn_testcircuit.place(relx=0.5, rely=0.3, anchor=CENTER)
        self.btn_acquire_freqresp.place(relx=0.5, rely=0.7, anchor=CENTER)
        self.btn_reset.place(relx=0.1, rely=0.7, anchor=CENTER)
        self.lbl_connect_first.place(relx=0.43, rely=0.2)

        # Draw graphs
        freq_resp_plot = EmbedGraph((1,1), heading='Frequency Response', y_label='Gain (dB)', x_label='Frequency (Hz)', log_graph=True)
        times = [1,2,3,4,5,6,7,8,9,10]
        voltages = [0.1,0.2,0.3,0.2,0.1,0,-0.1,-0.2,-0.3,2]
        live_plot = EmbedGraph((times,voltages), heading='Live Oscilloscope', x_label='Voltage (V)', y_label='Time (s)')
        freq_resp_plot.place(relx=0.8, rely=0.75, anchor=CENTER)
        live_plot.place(relx=0.8, rely=0.25, anchor=CENTER)

    def update_live_graph(self):
        times = [1,2,3,4,5,6,7,8,9,10]
        voltages = [0.1,0.2,0.3,0.2,0.1,0,-0.1,-0.2,-0.3,-0.2]
        #times, voltages = acquire_waveform(1)
        live_plot = EmbedGraph((times,voltages), heading='Live Oscilloscope', x_label='Voltage (V)', y_label='Time (s)')
        live_plot.place(relx=0.8, rely=0.24, anchor=CENTER)

    def update_freq_resp_plot(self):
        self.freq_resp, self.freq_resp_dB, self.cutoff_freq = calc_freq_response(self.results, self.voltages, self.frequencies, self.cutoff_dB)
        freq_resp_plot = EmbedGraph((self.frequencies,self.freq_resp_dB), heading='Frequency Response', y_label='Gain (dB)', x_label='Frequency (Hz)', log_graph=True, cutoff_data=[self.cutoff_dB, self.cutoff_freq])
        freq_resp_plot.place(relx=0.8, rely=0.68, anchor=CENTER)

    def change_state(self, button):
        """Changes the state of a button"""
        # If the STATE is NORMAL
        if (button['state'] == NORMAL):
    
            # Change the state to DISABLED
            button['state'] = DISABLED
        else:
            
            # Otherwise, change the state to NORMAL
            button['state'] = NORMAL

    def check_oscope_connection(self, master):
        """Checks if oscope is connected"""
        if master.oscope != None:
            self.lbl_connect_first['text']=""
            return NORMAL            
        else:
            self.lbl_connect_first['text']='Please connect to an oscillscope first\nfrom the connections menu'
            return DISABLED

    # Call backs to check data entry
    def callback_num(self, input):
        """Only numeric input allowed"""
        if input.isnumeric() or input == '' or input.replace(".", '', 1).isnumeric():
            return True
        else:
            return False          

    def callback_num_neg(self, input, neg=True):
        """Only numeric input allowed (including negative numbers)"""
        if input.isnumeric() or input == '' or input.replace(".", '', 1).isnumeric():
            return True
        if neg:
            if input.startswith("-") and (input[1:].isnumeric() or input[1:]=='' or input[1:].replace(".", '').isnumeric()):
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
        self.freq_steps = self.convert_num(self.entry_freqsteps.get())
        self.dc_offset = self.convert_num(self.entry_offset.get())
        self.meas_type = self.entry_meastype.get()
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
        test_settings_file["meas_type"] = self.meas_type
        test_settings_file["cutoff(dB)"] = self.cutoff_dB
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
        self.meas_type = test_settings_file["meas_type"]
        self.cutoff_dB = test_settings_file["cutoff(dB)"]
        test_settings_file.close()

    def Reset(self):
        """Resets settings to default"""
        self.voltages = 1
        self.start_frequency = 1000
        self.end_frequency = 100000
        self.frequency_step = 10
        self.frequencies = points_list_maker(self.start_frequency, self.end_frequency, self.frequency_step)
        self.dc_offset = 0
        self.meas_type = 'PEAK'
        self.cutoff_dB = -3
        self.results = None
        self.freq_resp = None
        self.freq_resp_dB = None
        self.cutoff_freq = None
        self.WriteSettings()

class ConnectionMenu(Frame):
    def __init__(self, master):

        # Allow frame to be set
        Frame.__init__(self, master)

        self.BLACK = (0,0,0)
        self.RED = (255,0,0)
        self.GREEN = (0,255,0)
        self.LBLUE = (12, 181, 249)
        self.BACKGROUND = (254, 254, 254)
        self.FONTSIZE = 20
        self.FONTSIZE_LARGE = 40

        # Read Initial Settings
        self.ReadSettings_Connect()

        # Create text variables
        self.tk_oscope = StringVar(self, self.oscilloscope1_string)
        self.tk_siggen = StringVar(self, self.signalgenerator1_string)
        self.tk_multim = StringVar(self, self.multimeter1_string)
        self.tk_powers = StringVar(self, self.powersupply1_string)

        # Create buttons and labels
        self.btn_home = Button (self, command=lambda: [self.entry_update_connections(), master.switch_frame(MainMenu)], text = 'Home', font=('Helvetica', self.FONTSIZE))
        self.lbl_heading = Label (self, text='Connections Menu', font=('Helvetica', self.FONTSIZE_LARGE))
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
        self.btn_home.place(relx=0.1, rely =0.1, anchor=CENTER)

        self.lbl_oscope.place(relx=0.1, rely=0.2, anchor=CENTER)
        self.entry_oscope.place(relx=0.3, rely=0.2, anchor=CENTER)
        self.lbl_siggen.place(relx=0.1, rely=0.3, anchor=CENTER)
        self.entry_siggen.place(relx=0.3, rely=0.3, anchor=CENTER)
        self.lbl_multim.place(relx=0.1, rely=0.4, anchor=CENTER)
        self.entry_multim.place(relx=0.3, rely=0.4, anchor=CENTER)
        self.lbl_powers.place(relx=0.1, rely=0.5, anchor=CENTER)
        self.entry_powers.place(relx=0.3, rely=0.5, anchor=CENTER)

        self.lbl_oscope_connect.place(relx=0.6, rely=0.2, anchor=CENTER)
        self.lbl_siggen_connect.place(relx=0.6, rely=0.3, anchor=CENTER)
        self.lbl_multim_connect.place(relx=0.6, rely=0.4, anchor=CENTER)
        self.lbl_powers_connect.place(relx=0.6, rely=0.5, anchor=CENTER)

        self.lbl_heading.place(relx=0.35, rely=0.1, anchor=CENTER)
        self.btn_connect_all.place(relx=0.5, rely=0.7, anchor=CENTER)
        self.btn_reset.place(relx=0.1, rely=0.7, anchor=CENTER)

    def connect_all(self, master):
        master.oscope = InstrumentControl.connect_instrument(self.oscilloscope1_string)
        master.siggen = InstrumentControl.connect_instrument(self.signalgenerator1_string)
        master.multim = InstrumentControl.connect_instrument(self.multimeter1_string)
        master.powers = InstrumentControl.connect_instrument(self.powersupply1_string)
        master.oscope = "HELLO THERE"
        instr = [master.oscope, master.siggen, master.multim, master.powers]
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
        

if __name__ == "__main__":
    app = InstrumentationControlApp()
    width= app.winfo_screenwidth()               
    height= app.winfo_screenheight()               
    app.geometry(f"{width}x{height}")
    app.title('Instrumentation Control')
    app.state('zoomed')
    app.mainloop()
