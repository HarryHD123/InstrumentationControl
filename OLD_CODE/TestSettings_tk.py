from tkinter import *
from DataManagement import points_list_maker
import shelve

class TestMenu():
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
        self.FONTSIZE = 20
        self.FONTSIZE_LARGE = 40

        # Set initial settings
        self.settings = [["voltages", [1]], ["frequencies", [1000, 10000]], ["dc_offset", 0], ["meas_type", "Peak"], ["cutoff_dB", -3]]
        self.settings_names = [settings for settings, values in self.settings]
        self.voltages = [1, 3]
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

        # Create buttons and labels
        self.lbl_heading = Label (master, text='Circuit Test Menu', height=8, width=50, font=('Helvetica', self.FONTSIZE_LARGE))
        self.btn_testcircuit = Button (master, text = 'Test Circuit', height=2, width=15, font=('Helvetica', self.FONTSIZE))
        self.btn_acquire_freqresp = Button (master, text = 'Acquire Frequency Response', height=2, width=15, font=('Helvetica', self.FONTSIZE))

        # Place buttons and labels
        self.lbl_heading.place(relx=0.2, rely =0.2, anchor=CENTER)
        self.btn_testcircuit.place(relx=0.1, rely =0.3, anchor=CENTER)
        self.btn_acquire_freqresp.place(relx=0.1, rely =0.7, anchor=CENTER)

    ###########
    """Read and write functions"""
    ###########
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