# Graphical User Interface

#from InstrumentControl import test_circuit, characterise_filter, acquire_waveform
#from Plot import plot_freq_resp
import pygame
import Initialise
import shelve
#import InstrumentControl
from TestSettings import Test_settings
from Tools.FontRender import RenderFont
from Tools.PictureUploads import Loadify, TransformImage

"""Main Menu"""
def MainMenu(screen):
    #image1 = Initialise.upgrade_bars_images
    #image2 = Initialise.buttons_images
    #image3 = Initialise.upgrade_levels_text_images
    background_image = Loadify("Images/main_background.png")
    background_image = TransformImage(background_image, Initialise.width, Initialise.height)

    LBLUE = (0, 204, 204)
    BLACK = (0,0,0)
    GREEN = (0,255,0)
    RED = (255,0,0)

    font_testcircuit = RenderFont("Test Circuit", 50, BLACK)
    font_testcircuit_settings = RenderFont("Test Circuit Settings", 50, BLACK)
    font_calc_freqresp = RenderFont("Calculate Frequency Response", 50, BLACK)
    font_plot_freqresp = RenderFont("Plot Frequency Response", 50, BLACK)
    font_acqwaveform = RenderFont("Acquire Waveform", 50, BLACK)
    font_charfilter = RenderFont("Characterise Filter", 50, BLACK)
    font_testing = RenderFont("Testing...", 50, GREEN)

    button_list = []
    for num in range(3):
        button_list.append(pygame.Rect(200, 150 * num + 150, 400, 50))
        button_list.append(pygame.Rect(1000, 150 * num + 150, 400, 50))


    on_main_menu = True
    click = False
    testing = False
    while on_main_menu:

        screen.blit(background_image, [0, 0])

        mx, my = pygame.mouse.get_pos()
        for button in button_list:
            pygame.draw.rect(screen, RED, button)
            if button.collidepoint(mx, my):
                pygame.draw.rect(screen, GREEN, button)
                if click:
                    if button_list.index(button) == 0:
                        testing = True
                        test_settings_file = shelve.open("Data/test_settings",writeback=True)
                        vin_PP = test_settings_file["voltages"]
                        frequencies = test_settings_file["frequencies"]
                        dc_offset = test_settings_file["dc_offset"]
                        meas_type = test_settings_file["meas_type"]
                        cutoff_dB = test_settings_file["cutoff(dB)"]
                        #InstrumentControl.test_circuit(vin_PP, frequencies)
                    elif button_list.index(button) == 1:
                        Test_settings(screen).ShowWindow()
                    #elif button_list.index(button) == 2:
                    #    InstrumentControl.calc_freq_resp()
                    #elif button_list.index(button) == 3:
                    #    InstrumentControl.characterise_filter()
                    #elif button_list.index(button) == 4:
                    #    InstrumentControl.plot_freq_resp()
                    #elif button_list.index(button) == 5:
                    #    InstrumentControl.acquire_waveform()

        screen.blit(font_testcircuit, [200, 150])
        screen.blit(font_calc_freqresp, [200, 300])
        screen.blit(font_plot_freqresp, [200, 450])
        screen.blit(font_charfilter, [1000, 450])
        screen.blit(font_acqwaveform, [1000, 300])
        screen.blit(font_testcircuit_settings, [1000, 150])

        if testing:
            screen.blit(font_testing, [600, 150])

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


MainMenu(Initialise.screen)
