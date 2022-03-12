# Graphical User Interface

import pygame
import shelve
import InstrumentControl
from ConnectionSettings import Connection_settings
from TestSettings import Test_settings
from Tools.FontRender import RenderFont
from Tools.PictureUploads import Loadify, TransformImage
from Tools.SettingSaves import GetRes




"""Main Menu"""
def MainMenu(screen):

    #image1 = Initialise.upgrade_bars_images
    #image2 = Initialise.buttons_images
    #image3 = Initialise.upgrade_levels_text_images
    #background_image = Loadify("Images/main_background.png")
    #background_image = TransformImage(background_image, WIDTH, HEIGHT)

    BLACK = (0,0,0)
    LBLUE = (12, 181, 249)
    GREEN = (0,255,0)
    RED = (255,0,0)
    WHITE = (255,255,255)
    LGREY = (170,170,170)
    DGREY = (100,100,100)
    BACKGROUND = (254, 254, 254)
    FONTSIZE = 50
    FONTSIZE_LARGE = 75

    font_heading = RenderFont("Synardyne Lab Instrument Control", FONTSIZE_LARGE, BLACK)
    font_testcircuit = RenderFont("Test Circuit", FONTSIZE, BLACK)
    font_connections = RenderFont("Connection Settings", FONTSIZE, BLACK)
    font_calc_freqresp = RenderFont("Calculate Frequency Response", FONTSIZE, BLACK)
    font_plot_freqresp = RenderFont("Plot Frequency Response", FONTSIZE, BLACK)
    font_acqwaveform = RenderFont("Acquire Waveform", FONTSIZE, BLACK)
    font_charfilter = RenderFont("Characterise Filter", FONTSIZE, BLACK)
    
    button_list = DrawButtons()

    on_main_menu = True
    click = False
    while on_main_menu:

        screen.fill((BACKGROUND)) 

        mx, my = pygame.mouse.get_pos()
        for button in button_list:
            pygame.draw.rect(screen, LBLUE, button)
            if button.collidepoint(mx, my):
                pygame.draw.rect(screen, GREEN, button)
                if click:
                    if button_list.index(button) == 0:
                        Test_settings(screen).ShowWindow()
                    elif button_list.index(button) == 1:
                        Connection_settings(screen).ShowWindow()
                    elif button_list.index(button) == 2:
                        test_settings_file = shelve.open("Data/test_settings",writeback=True)
                        vin_PP = test_settings_file["voltages"]
                        frequencies = test_settings_file["frequencies"]
                        cutoff_dB = test_settings_file["cutoff(dB)"]
                        results = test_settings_file["results"]
                        freq_resp, freq_resp_dB, cutoff_freq = InstrumentControl.calc_freq_response(results, vin_PP, frequencies, cutoff_dB_val=cutoff_dB)
                        test_settings_file["freq_resp"] = freq_resp
                        test_settings_file["freq_resp_dB"] = freq_resp_dB
                        test_settings_file["cutoff_freq"] = cutoff_freq
                        test_settings_file.close()
                    elif button_list.index(button) == 5:
                        InstrumentControl.characterise_filter()
                    elif button_list.index(button) == 4:
                        test_settings_file = shelve.open("Data/test_settings",writeback=True)
                        frequencies = test_settings_file["frequencies"]
                        cutoff_dB = test_settings_file["cutoff(dB)"]
                        freq_resp_dB =  test_settings_file["freq_resp_dB"]
                        cutoff_freq = test_settings_file["cutoff_freq"]
                        InstrumentControl.plot_freq_resp(frequencies, freq_resp_dB, cutoff_dB, cutoff_freq)
                        test_settings_file.close()
                    elif button_list.index(button) == 3:
                        InstrumentControl.acquire_waveform(chan=1)
                    elif button_list.index(button) == 6:
                        test_settings_file = shelve.open("Data/test_settings",writeback=True)
                        voltage = test_settings_file["voltages"][0]
                        frequency = test_settings_file["frequencies"][0]
                        dc_offset = test_settings_file["dc_offset"]
                        InstrumentControl.oscope_set_siggen(voltage, frequency, dc_offset)
                    elif button_list.index(button) == 7:
                        connection_settings_file = shelve.open("Data/connection_settings",writeback=True)
                        oscilloscope1_string = connection_settings_file["oscilloscope1_string"]
                        multimeter1_string = connection_settings_file["multimeter1_string"]
                        signalgenerator1_string = connection_settings_file["signalgenerator1_string"]
                        powersupply1_string = connection_settings_file["powersupply1_string"]
                        InstrumentControl.connect_all_instruments(True, oscilloscope1_string, multimeter1_string, signalgenerator1_string, powersupply1_string)

        screen.blit(font_heading, [250, 50])
        screen.blit(font_testcircuit, [200, 250])
        screen.blit(font_connections, [900,250])
        screen.blit(font_calc_freqresp, [200, 400])
        screen.blit(font_plot_freqresp, [200, 550])
        screen.blit(font_charfilter, [900, 550])
        screen.blit(font_acqwaveform, [900, 400])

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Game quits if user presses escape on the main screen
                    pygame.quit()
                    quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        pygame.display.update()

def DrawButtons():
    button_list = []
    button_list.append(pygame.Rect(200, 250, 400, 50)) # 1. Test Circuit
    button_list.append(pygame.Rect(900, 250, 400, 50)) # 2. Connection Settings
    button_list.append(pygame.Rect(200, 400, 400, 50))
    button_list.append(pygame.Rect(900, 400, 400, 50)) 
    button_list.append(pygame.Rect(200, 550, 400, 50))
    button_list.append(pygame.Rect(900, 550, 400, 50))

    return button_list

pygame.init()
title = "Instrumentation Control"
screen_info = pygame.display.Info() # Required to set a good resolution for the game screen
first_screen = (screen_info.current_w, screen_info.current_h-50) # Take 50 pixels from the height because the menu bar, window bar and dock takes space
first_screen = (1920,1080)
screen = pygame.display.set_mode(first_screen, pygame.RESIZABLE)
pygame.display.set_caption(title)

print("1",screen_info.current_w, screen_info.current_h)
MainMenu(screen)
