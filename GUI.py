# Graphical User Interface

import pygame
import shelve
import InstrumentControl
from Tools.FontRender import RenderFont
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
    GREEN = (0,255,0)
    RED = (255,0,0)
    WHITE = (255,255,255)
    LGREY = (170,170,170)
    DGREY = (100,100,100)
    BACKGROUND = (254, 254, 254)

    font_testcircuit = RenderFont("Test Circuit", 50, BLACK)
    font_calc_freqresp = RenderFont("Calculate Frequency Response", 50, BLACK)
    font_plot_freqresp = RenderFont("Plot Frequency Response", 50, BLACK)
    font_acqwaveform = RenderFont("Acquire Waveform", 50, BLACK)
    font_charfilter = RenderFont("Characterise Filter", 50, BLACK)
    

    button_list = []
    for num in range(3):
        button_list.append(pygame.Rect(200, 150 * num + 150, 400, 50))
        button_list.append(pygame.Rect(1000, 150 * num + 150, 400, 50))


    on_main_menu = True
    click = False
    while on_main_menu:

        screen.fill((BACKGROUND)) 
        #screen.blit(background_image, [0, 0])

        mx, my = pygame.mouse.get_pos()
        for button in button_list:
            pygame.draw.rect(screen, DGREY, button)
            if button.collidepoint(mx, my):
                pygame.draw.rect(screen, LGREY, button)
                if click:
                    if button_list.index(button) == 0:
                        Test_settings(screen).ShowWindow()
                        #test_settings_file = shelve.open("Data/test_settings",writeback=True)
                        #vin_PP = test_settings_file["voltages"]
                        #frequencies = test_settings_file["frequencies"]
                        #dc_offset = test_settings_file["dc_offset"]
                        #meas_type = test_settings_file["meas_type"]
                        #cutoff_dB = test_settings_file["cutoff(dB)"]
                        #test_settings_file["results"] = results
                        #test_settings_file.close()
                    elif button_list.index(button) == 1:
                        Test_settings(screen).ShowWindow()
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
                        #connection_settings_file["oscilloscope1_string"] = 'TCPIP0::192.168.1.2::inst0::INSTR'
                        #connection_settings_file["multimeter1_string"] = 'TCPIP0::192.168.1.5::5025::SOCKET'
                        #connection_settings_file["signalgenerator1_string"] = 'TCPIP0::192.168.1.3::inst0::INSTR'
                        #connection_settings_file["powersupply1_string"] = 'TCPIP0::192.168.1.4::inst0::INSTR'
                        oscilloscope1_string = connection_settings_file["oscilloscope1_string"]
                        multimeter1_string = connection_settings_file["multimeter1_string"]
                        signalgenerator1_string = connection_settings_file["signalgenerator1_string"]
                        powersupply1_string = connection_settings_file["powersupply1_string"]
                        InstrumentControl.connect_all_instruments(True, oscilloscope1_string, multimeter1_string, signalgenerator1_string, powersupply1_string)


        screen.blit(font_testcircuit, [200, 150])
        screen.blit(font_calc_freqresp, [200, 300])
        screen.blit(font_plot_freqresp, [200, 450])
        screen.blit(font_charfilter, [1000, 450])
        screen.blit(font_acqwaveform, [1000, 300])

        click = False
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Game quits if user presses escape on the main screen
                    pygame.quit()
                    quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        pygame.display.update()


pygame.init()
WIDTH = int(GetRes()[0])
HEIGHT = int(GetRes()[1])
mode = (GetRes()[2])
if mode == "fullscreen":
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
else:
    screen = pygame.display.set_mode([WIDTH, HEIGHT])

MainMenu(screen)
