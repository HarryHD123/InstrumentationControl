from cmath import log
import pygame
from Tools.FontRender import RenderFont
from Tools.GraphTools import EmbedGraph
import shelve
from InstrumentControl import test_circuit, calc_freq_response, plot_freq_resp, acquire_waveform
from DataManagement import points_list_maker
#import Initialise


class Test_settings(object):
    def __init__(self, screen):
        
        # Set colours
        self.BLACK = (0,0,0)
        self.GREEN = (0,255,0)
        self.RED = (255,0,0)
        self.WHITE = (255,255,255)
        self.LGREY = (170,170,170)
        self.DGREY = (100,100,100)
        self.LBLUE = (12, 181, 249)
        self.BACKGROUND = (254, 254, 254)
        self.FONTSIZE = 30
        self.FONTSIZE_LARGE = 75

        # Set initial variables
        self.on_test_settings = True
        self.rerender = True
        self.screen = screen
        self.width, self.height = pygame.display.get_surface().get_size()
        print("HERE", self.width, self.height)
        self.scale = self.width/1920

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

        # Render initial text
        self.voltages_textfont = RenderFont(f"Voltages (V):", self.FONTSIZE, self.BLACK)
        self.start_frequency_textfont = RenderFont(f"Start Frequency (Hz):", self.FONTSIZE, self.BLACK)
        self.end_frequency_textfont = RenderFont(f"End Frequency (Hz):", self.FONTSIZE, self.BLACK)
        self.frequency_step_textfont = RenderFont(f"Frequency Steps:", self.FONTSIZE, self.BLACK)
        self.dc_offset_textfont = RenderFont(f"DC Offset (V):", self.FONTSIZE, self.BLACK)
        self.meas_type_textfont = RenderFont(f"Measuring Type:", self.FONTSIZE, self.BLACK)
        self.cutoff_dB_textfont = RenderFont(f"Cut off (dB):", self.FONTSIZE, self.BLACK)
        
        self.voltages_valfont_str = ""
        for v in self.voltages:
            self.voltages_valfont_str = self.voltages_valfont_str + str(v) + " " 

        self.voltages_valfont = RenderFont(f"{self.voltages_valfont_str}", self.FONTSIZE, self.BLACK)
        self.start_frequency_valfont = RenderFont(f"{self.start_frequency}", self.FONTSIZE, self.BLACK)
        self.end_frequency_valfont = RenderFont(f"{self.end_frequency}", self.FONTSIZE, self.BLACK)
        self.frequency_step_valfont = RenderFont(f"{self.frequency_step}", self.FONTSIZE, self.BLACK)
        self.dc_offset_valfont = RenderFont(f"{self.dc_offset}", self.FONTSIZE, self.BLACK)
        self.meas_type_valfont = RenderFont(f"{self.meas_type}", self.FONTSIZE, self.BLACK)
        self.cutoff_dB_valfont = RenderFont(f"{self.cutoff_dB}", self.FONTSIZE, self.BLACK)
        
        self.heading_textfont = RenderFont("Circuit Testing Menu", self.FONTSIZE_LARGE, self.LBLUE)
        self.test_circ_textfont = RenderFont("Test Circuit", self.FONTSIZE, self.BLACK)
        self.acq_freq_textfont = RenderFont(f"Acquire Frequency Response", self.FONTSIZE, self.BLACK)
        self.testing_textfont = RenderFont("Testing...", self.FONTSIZE, self.GREEN)

        # Create buttons
        self.button_list = self.DrawButtons()  # sets the button locations on the screen


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

    ##########
    """Window Update Functions"""
    ##########

    def ShowWindow(self):
        """Shows the window for test settings"""

        click = False
        typing = False
        text = ''
        Input_fault = False
        live_graph = False
        freq_resp_graph = False
        freq_resp_plot = EmbedGraph((1,1), heading='Frequency Response', y_label='Gain (dB)', x_label='Frequency (Hz)', log_graph=True)
        times = [1,2,3,4,5,6,7,8,9,10]
        voltages = [0.1,0.2,0.3,0.2,0.1,0,-0.1,-0.2,-0.3,-0.2]
        live_plot = EmbedGraph((times,voltages), heading='Live Oscilloscope', x_label='Voltage (V)', y_label='Time (s)')
        self.ReadSettings()
        while self.on_test_settings:

            self.screen.fill((self.BACKGROUND)) 

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.on_test_settings = False
                    if typing:
                        if event.key == pygame.K_RETURN:
                            # Data entry checking
                            if self.button_list.index(button_pressed) in (0,1,2,4):
                                try:
                                    for i in text.split(","):
                                        float(i)
                                except ValueError:
                                    Input_fault = True

                                if self.button_list.index(button_pressed) == 0:
                                    self.voltages = text.split(",")
                                    self.voltages = [float(i) for i in self.voltages]
                                if self.button_list.index(button_pressed) == 1:
                                    self.start_frequency = float(text)
                                if self.button_list.index(button_pressed) == 2:
                                    self.end_frequency = float(text)
                                if self.button_list.index(button_pressed) == 3:
                                    self.frequency_step = float(text)
                                if self.button_list.index(button_pressed) == 4:
                                    self.dc_offset = float(text)
                                if self.button_list.index(button_pressed) == 5:
                                    self.cutoff_dB = float(text)

                            if self.button_list.index(button_pressed) == 6:
                                if text != 'PEAK':
                                    Input_fault = True
                                else:
                                    self.meas_type = text

                            text = ''
                            typing = False
                            self.rerender = True

                        elif event.key == pygame.K_BACKSPACE:
                            text = text[:-1]
                        else:
                            text += event.unicode                                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        click = True
            
            mx, my = pygame.mouse.get_pos()
            for buttons in self.button_list:
                colour = self.LBLUE
                pygame.draw.rect(self.screen, colour, buttons)
                if buttons.collidepoint(mx, my):
                    colour = self.GREEN
                    pygame.draw.rect(self.screen, colour, buttons)
                    """If user clicks on any of the buttons"""
                    if click:
                        Input_fault = False
                        if self.button_list.index(buttons) == 0:
                            button_pressed = self.button_list[0]
                            typing = True
                        elif self.button_list.index(buttons) == 1:
                            button_pressed = self.button_list[1]
                            typing = True
                        elif self.button_list.index(buttons) == 2:
                            button_pressed = self.button_list[2]
                            typing = True
                        elif self.button_list.index(buttons) == 3:
                            button_pressed = self.button_list[3]
                            typing = True
                        elif self.button_list.index(buttons) == 4:
                            button_pressed = self.button_list[4]
                            typing = True
                        elif self.button_list.index(buttons) == 5:
                            button_pressed = self.button_list[5]
                            typing = True
                        elif self.button_list.index(buttons) == 6:
                            button_pressed = self.button_list[6]
                            typing = True
                        elif self.button_list.index(buttons) == 7:
                            button_pressed = self.button_list[7]
                            typing = True
                        elif self.button_list.index(buttons) == 8:
                            button_pressed = self.button_list[8]
                            self.ReadSettings()
                            test_data_file = shelve.open("Data/test_data")
                            self.screen.blit(self.testing_textfont, [800, 150])
                            pygame.display.update()
                            self.results = test_circuit(self.voltages, self.frequencies)
                            test_data_file["results"] = self.results
                            test_data_file.close()
                            typing = True
                        elif self.button_list.index(buttons) == 9:
                            button_pressed = self.button_list[9]
                            if self.results != None:
                                test_data_file = shelve.open("Data/test_freqresp_data")
                                self.freq_resp, self.freq_resp_dB, self.cutoff_freq = calc_freq_response(self.results, self.voltages, self.frequencies, self.cutoff_dB)
                                test_data_file["freq_resp"] = self.freq_resp
                                test_data_file["freq_resp_dB"] = self.freq_resp_dB
                                test_data_file["cutoff_freq"] = self.cutoff_freq
                                test_data_file.close()
                                freq_resp_graph = True

                            typing = True
                        click = False

            if typing:
                input_box = pygame.Rect(button_pressed)
                text_font = RenderFont(f"{text}", self.FONTSIZE, self.BLACK)
                pygame.draw.rect(self.screen, self.GREEN, input_box)
                self.screen.blit(text_font, [button_pressed[0], button_pressed[1]])
                    
            if Input_fault:
                fault_font = RenderFont(f"Invalid setting entered", 25, self.RED)
                self.screen.blit(fault_font, [button_pressed[0]+250, button_pressed[1]])

            if self.results == None:
                results_needed_font = RenderFont(f"Circuit must be tested first to acquire a frequency response", 25, self.RED)
                self.screen.blit(results_needed_font, [100 * self.scale, 600 * self.scale])

            if self.rerender:
                self.voltages_valfont_str = ""
                for v in self.voltages:
                    if v == int(v):
                        v = int(v)
                    self.voltages_valfont_str = self.voltages_valfont_str + str(v) + ", " 
                self.voltages_valfont = RenderFont(f"{self.voltages_valfont_str[:-2]}", self.FONTSIZE, self.BLACK)
                self.start_frequency_valfont = RenderFont(f"{self.start_frequency}", self.FONTSIZE, self.BLACK)
                self.end_frequency_valfont = RenderFont(f"{self.end_frequency}", self.FONTSIZE, self.BLACK)
                self.frequency_step_valfont = RenderFont(f"{self.frequency_step}", self.FONTSIZE, self.BLACK)
                self.dc_offset_valfont = RenderFont(f"{self.dc_offset}", self.FONTSIZE, self.BLACK)
                self.meas_type_valfont = RenderFont(f"{self.meas_type}", self.FONTSIZE, self.BLACK)
                self.cutoff_dB_valfont = RenderFont(f"{self.cutoff_dB}", self.FONTSIZE, self.BLACK)
                self.WriteSettings()
                self.rerender = False

            self.screen.blit(self.voltages_textfont, [100 * self.scale, 150 * self.scale])
            self.screen.blit(self.start_frequency_textfont, [100 * self.scale, 200 * self.scale])
            self.screen.blit(self.end_frequency_textfont, [100 * self.scale, 250 * self.scale])
            self.screen.blit(self.frequency_step_textfont, [100 * self.scale, 300 * self.scale])
            self.screen.blit(self.dc_offset_textfont, [100 * self.scale, 350 * self.scale])
            self.screen.blit(self.meas_type_textfont, [100 * self.scale, 400 * self.scale])
            self.screen.blit(self.cutoff_dB_textfont, [100 * self.scale, 650 * self.scale])
            self.screen.blit(self.test_circ_textfont, [700 * self.scale, 150 * self.scale])
            self.screen.blit(self.acq_freq_textfont, [700 * self.scale, 650 * self.scale])
            self.screen.blit(self.heading_textfont, [100 * self.scale, 50 * self.scale])

            self.screen.blit(self.voltages_valfont, [420 * self.scale, 150 * self.scale])
            self.screen.blit(self.start_frequency_valfont, [420 * self.scale, 200 * self.scale])
            self.screen.blit(self.end_frequency_valfont, [420 * self.scale, 250 * self.scale])
            self.screen.blit(self.frequency_step_valfont, [420 * self.scale, 300 * self.scale])
            self.screen.blit(self.dc_offset_valfont, [420 * self.scale, 350 * self.scale])
            self.screen.blit(self.meas_type_valfont, [420 * self.scale, 400 * self.scale])
            self.screen.blit(self.cutoff_dB_valfont, [420 * self.scale, 650 * self.scale])

            if live_graph:
                times, voltages = acquire_waveform(1)
                live_plot = EmbedGraph((times,voltages), heading='Live Oscilloscope', x_label='Voltage (V)', y_label='Time (s)')

            if freq_resp_graph:
                freq_resp_plot = EmbedGraph((self.frequencies,self.freq_resp_dB), heading='Frequency Response', y_label='Gain (dB)', x_label='Frequency (Hz)', log_graph=True)
                freq_resp_graph = False

            self.screen.blit(live_plot, (1000,0))
            self.screen.blit(freq_resp_plot, (1000,500))

            pygame.display.update()


    def DrawButtons(self):
        """Draw the buttons for the upgrades menu"""
        button_list = []
        button_list.append(pygame.Rect(420 * self.scale, 150 * self.scale, 150, 30)) # 1. Voltage Button
        button_list.append(pygame.Rect(420 * self.scale, 200 * self.scale, 150, 30)) # 2. Start Frequency Button
        button_list.append(pygame.Rect(420 * self.scale, 250 * self.scale, 150, 30)) # 3. End Frequency Button
        button_list.append(pygame.Rect(420 * self.scale, 300 * self.scale, 150, 30)) # 4. Frequency Step Button
        button_list.append(pygame.Rect(420 * self.scale, 350 * self.scale, 150, 30)) # 5. DC Offset Button
        button_list.append(pygame.Rect(420 * self.scale, 400 * self.scale, 150, 30)) # 6. Meas Type Button
        button_list.append(pygame.Rect(420 * self.scale, 650 * self.scale, 150, 30)) # 7. Cutoff dB Button
        button_list.append(pygame.Rect(700 * self.scale, 150 * self.scale, 150, 30)) # 8. Test Circuit Button
        button_list.append(pygame.Rect(700 * self.scale, 650 * self.scale, 360, 30)) # 9. Acquire Frequency Response Button
        return button_list