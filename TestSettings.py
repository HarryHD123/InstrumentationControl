from turtle import width
import pygame
from Tools.FontRender import RenderFont
from Tools.PictureUploads import Loadify, TransformImage
import shelve
from InstrumentControl import test_circuit
from DataManagement import points_list_maker
#import Initialise


class Test_settings(object):
    def __init__(self, screen):
        
        # Set colours
        self.BLACK = (0,0,0)
        self.GREEN = (0,155,0)
        self.RED = (255,0,0)
        self.WHITE = (255,255,255)
        self.LGREY = (170,170,170)
        self.DGREY = (100,100,100)
        self.LBLUE = (0, 204, 204)
        self.BACKGROUND = (254, 254, 254)
        self.FONTSIZE = 25

        # Set initial variables
        self.on_test_settings = True
        self.rerender = True
        self.screen = screen
        self.width, self.height = pygame.display.get_surface().get_size()
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
        
        self.test_circ_textfont = RenderFont("Test Circuit", self.FONTSIZE, self.BLACK)
        self.testing_textfont = RenderFont("Testing...", self.FONTSIZE, self.GREEN)

        # Create buttons and set background
        self.button_list = self.DrawButtons()  # sets the button locations on the screen
        #self.background = Loadify("Images/settings_background.jpg")
        #self.background = TransformImage(self.background, self.width, self.height)

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
        testing = False
        text = ''
        Input_fault = False
        self.ReadSettings()
        while self.on_test_settings:

            self.screen.fill((self.BACKGROUND)) 
            #self.screen.blit(self.background, [0, 0])

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.on_test_settings = False
                    if typing:
                        if event.key == pygame.K_RETURN:
                            # Data entry checking
                            if button_index in (0,1,2,4):
                                try:
                                    for i in text.split(","):
                                        float(i)
                                except ValueError:
                                    Input_fault = True

                                if button_index == 0:
                                    self.voltages = text.split(",")
                                    self.voltages = [float(i) for i in self.voltages]
                                if button_index == 1:
                                    self.frequencies = text.split(",")
                                    self.frequencies = [float(i) for i in self.frequencies]
                                if button_index == 2:
                                    self.dc_offset = float(text)
                                if button_index == 4:
                                    self.cutoff_dB = float(text)

                            if button_index == 3:
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
                colour = self.DGREY
                pygame.draw.rect(self.screen, colour, buttons)
                if buttons.collidepoint(mx, my):
                    colour = self.LGREY
                    pygame.draw.rect(self.screen, colour, buttons)
                    """If user clicks on any of the buttons"""
                    if click:
                        Input_fault = False
                        if self.button_list.index(buttons) == 0:
                            button_index = 0
                            typing = True
                        elif self.button_list.index(buttons) == 1:
                            button_index = 1
                            typing = True
                        elif self.button_list.index(buttons) == 2:
                            button_index = 2
                            typing = True
                        elif self.button_list.index(buttons) == 3:
                            button_index = 3
                            typing = True
                        elif self.button_list.index(buttons) == 4:
                            button_index = 4
                            typing = True
                        elif self.button_list.index(buttons) == 5:
                            self.ReadSettings()
                            test_data_file = shelve.open("Data/test_data")
                            self.screen.blit(self.testing_font, [600, 150])
                            results = test_circuit(self.voltages, self.frequencies)
                            test_data_file["results"] = results
                            test_data_file.close()
                            button_index = 5
                        elif self.button_list.index(buttons) == 6:
                            button_index = 6
                            typing = True
                        elif self.button_list.index(buttons) == 7:
                            button_index = 7
                            typing = True
                        elif self.button_list.index(buttons) == 8:
                            button_index = 8
                            typing = True
                        elif self.button_list.index(buttons) == 9:
                            button_index = 9
                            typing = True
                        click = False

            if typing:
                input_box = pygame.Rect(900 * self.scale, (button_index * 150 + 150) * self.scale, 500, 50)
                text_font = RenderFont(f"{text}", 50, self.BLACK)
                pygame.draw.rect(self.screen, self.WHITE, input_box)
                self.screen.blit(text_font, [900 * self.scale, (button_index * 150 + 150) * self.scale])
                    
            if Input_fault:
                fault_font = RenderFont(f"Invalid setting entered", 50, self.RED)
                self.screen.blit(fault_font, [1200 * self.scale, (button_index * 150 + 150) * self.scale])

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

            self.screen.blit(self.voltages_textfont, [100 * self.scale, 50 * self.scale])
            self.screen.blit(self.start_frequency_textfont, [100 * self.scale, 150 * self.scale])
            self.screen.blit(self.end_frequency_textfont, [500 * self.scale, 150 * self.scale])
            self.screen.blit(self.frequency_step_textfont, [900 * self.scale, 150 * self.scale])
            self.screen.blit(self.dc_offset_textfont, [100 * self.scale, 250 * self.scale])
            self.screen.blit(self.meas_type_textfont, [100 * self.scale, 350 * self.scale])
            self.screen.blit(self.cutoff_dB_textfont, [100 * self.scale, 450 * self.scale])
            self.screen.blit(self.test_circ_textfont, [self.width/2, 500 * self.scale])

            
            self.screen.blit(self.voltages_valfont, [380 * self.scale, 50 * self.scale])
            self.screen.blit(self.start_frequency_valfont, [380 * self.scale, 150 * self.scale])
            self.screen.blit(self.end_frequency_valfont, [780 * self.scale, 150 * self.scale])
            self.screen.blit(self.frequency_step_valfont, [1180 * self.scale, 150 * self.scale])
            self.screen.blit(self.dc_offset_valfont, [380 * self.scale, 250 * self.scale])
            self.screen.blit(self.meas_type_valfont, [380 * self.scale, 350 * self.scale])
            self.screen.blit(self.cutoff_dB_valfont, [380 * self.scale, 450 * self.scale])

            pygame.display.update()

    def DrawButtons(self):
        """Draw the buttons for the upgrades menu"""
        button_list = []
        button_list.append(pygame.Rect(100 * self.scale, 50 * self.scale, 220, 50)) # Voltage Button
        button_list.append(pygame.Rect(100 * self.scale, 150 * self.scale, 220, 50)) # Start Frequency Button
        button_list.append(pygame.Rect(500 * self.scale, 150 * self.scale, 220, 50)) # End Frequency Button
        button_list.append(pygame.Rect(900 * self.scale, 150 * self.scale, 220, 50)) # Frequency Step Button
        button_list.append(pygame.Rect(100 * self.scale, 250 * self.scale, 220, 50)) # DC Offset Button
        button_list.append(pygame.Rect(100 * self.scale, 350 * self.scale, 220, 50)) # Meas Type Button
        button_list.append(pygame.Rect(100 * self.scale, 450 * self.scale, 220, 50)) # Cutoff dB Button
        button_list.append(pygame.Rect(self.width/2, 500 * self.scale, 220, 50)) # Test Circuit Button
        return button_list
