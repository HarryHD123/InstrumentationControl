import pygame
from Tools.FontRender import RenderFont
from Tools.PictureUploads import Loadify, TransformImage
import shelve
import Initialise


class Test_settings(object):
    def __init__(self, screen):
        self.BLACK = (0, 0, 0)
        self.LBLUE = (0, 204, 204)
        self.on_test_settings = True
        self.rerender = True
        self.screen = screen
        self.width, self.height = pygame.display.get_surface().get_size()
        self.scale = self.width/1920
        self.settings = [["voltages", [1]], ["frequencies", [1000]], ["dc_offset", 0], ["meas_type", "Peak"], ["cutoff_dB", -3]]
        self.settings_names = [settings for settings, values in self.settings]

        self.voltages = [1]
        self.frequencies = [1000]
        self.dc_offset = 0
        self.meas_type = 'PEAK'
        self.cutoff_dB = -3

        self.voltages_font = RenderFont(f"Voltages Measured:        {self.voltages}", 50, self.BLACK)
        self.frequencies_font = RenderFont(f"Frequencies Measured:    {self.frequencies}", 50, self.BLACK)
        self.dc_offset_font = RenderFont(f"DC Offset:                    {self.dc_offset}", 50, self.BLACK)
        self.meas_type_font = RenderFont(f"Measuring Type:             {self.meas_type}", 50, self.BLACK)
        self.cutoff_dB_font = RenderFont(f"Cut off (dB):                  {self.cutoff_dB}", 50, self.BLACK)

        self.settings_names_fonts = [self.voltages_font, self.frequencies_font, self.dc_offset_font, self.meas_type_font, self.cutoff_dB_font]

        self.button_list = self.DrawButtons()  # sets the button locations on the screen
        self.background = Loadify("Images/settings_background.jpg")
        self.background = TransformImage(self.background, self.width, self.height)

        self.RED = (255,0,0)
        self.GREEN = (0,250,0)
        self.WHITE = (255,255,255)

    ###########
    """Read and write functions"""
    ###########
    def WriteSettings(self):
        """Writes the test settings to the save file"""
        test_settings_file = shelve.open("Data/test_settings",writeback=True)
        test_settings_file["voltages"] = self.voltages
        test_settings_file["frequencies"] = self.frequencies
        test_settings_file["dc_offset"] = self.dc_offset
        test_settings_file["meas_type"] = self.meas_type
        test_settings_file["cutoff(dB)"] = self.cutoff_dB
        test_settings_file.close()

    def ReadSettings(self):
        """Reads the test settings"""
        test_settings_file = shelve.open("Data/test_settings")
        self.voltages = test_settings_file["voltages"]
        self.frequencies = test_settings_file["frequencies"]
        self.dc_offset = test_settings_file["dc_offset"]
        self.meas_type = test_settings_file["meas_type"]
        self.cutoff_dB = test_settings_file["cutoff(dB)"]
        test_settings_file.close()

    #def ReadFile(self):
    #    """Reads the original file"""
    #    self.WriteSettings()
    #    keys = [names for names, value in self.settings]
    #    value_file = shelve.open("Data/test_settings")
    #    for key in keys:
    #        values = value_file[f"{key}"]
    #    value_file.close()
    #    self.settings = []
    #    for n in range(10):
    #        self.settings.append([keys[n], values[n]])
    ##########
    """Window Update Functions"""
    ##########

    def DrawButtons(self):
        """Draw the buttons for the upgrades menu"""
        button_list = []
        for num in range(5):
            button_list.append(pygame.Rect(250 * self.scale, (150 * num + 150) * self.scale, 500, 50))
        return button_list


    def ShowWindow(self):
        """Shows the window for test settings"""
        
        click = False
        typing = False
        text = ''
        Input_fault = False
        self.ReadSettings()
        while self.on_test_settings:

            self.screen.blit(self.background, [0, 0])

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.on_test_settings = False
                    if typing:
                        if event.key == pygame.K_RETURN:

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
                colour = self.RED
                pygame.draw.rect(self.screen, colour, buttons)
                if buttons.collidepoint(mx, my):
                    colour = self.GREEN
                    pygame.draw.rect(self.screen, colour, buttons)
                    """If user clicks on any of the buttons"""
                    if click:
                        Input_fault = False
                        if self.button_list.index(buttons) == 0:
                            button_index = 0
                            typing = True
                            self.voltages_font = RenderFont(f"Voltages Measured:", 50, self.BLACK)
                        elif self.button_list.index(buttons) == 1:
                            button_index = 1
                            typing = True
                            self.frequencies_font = RenderFont(f"Frequencies Measured:", 50, self.BLACK)
                        elif self.button_list.index(buttons) == 2:
                            button_index = 2
                            typing = True
                            self.dc_offset_font = RenderFont(f"DC Offset:", 50, self.BLACK)
                        elif self.button_list.index(buttons) == 3:
                            button_index = 3
                            typing = True
                            self.meas_type_font = RenderFont(f"Measuring Type:", 50, self.BLACK)
                        elif self.button_list.index(buttons) == 4:
                            button_index = 4
                            typing = True
                            self.cutoff_dB_font = RenderFont(f"Cut off (dB):", 50, self.BLACK)
                        elif self.button_list.index(buttons) == 5:
                            button_index = 5
                            typing = True
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
                text_font = RenderFont(f"{text}", 50, self.WHITE)
                pygame.draw.rect(self.screen, self.BLACK, input_box)
                self.screen.blit(text_font, [900 * self.scale, (button_index * 150 + 150) * self.scale])
                    
            if Input_fault:
                fault_font = RenderFont(f"Invalid setting entered", 50, self.RED)
                self.screen.blit(fault_font, [1200 * self.scale, (button_index * 150 + 150) * self.scale])

            if self.rerender:
                self.voltages_font = RenderFont(f"Voltages Measured:        {self.voltages}", 50, self.BLACK)
                self.frequencies_font = RenderFont(f"Frequencies Measured:    {self.frequencies}", 50, self.BLACK)
                self.dc_offset_font = RenderFont(f"DC Offset:                    {self.dc_offset}", 50, self.BLACK)
                self.meas_type_font = RenderFont(f"Measuring Type:             {self.meas_type}", 50, self.BLACK)
                self.cutoff_dB_font = RenderFont(f"Cut off (dB):                  {self.cutoff_dB}", 50, self.BLACK)
                self.WriteSettings()
                self.rerender = False

            setting_counter = 0
            self.settings_names_fonts = [self.voltages_font, self.frequencies_font, self.dc_offset_font, self.meas_type_font, self.cutoff_dB_font] 
            for value in self.settings_names_fonts:
                self.screen.blit(value, [250 * self.scale, (setting_counter * 150 + 150) * self.scale])
                setting_counter += 1

            pygame.display.update()


