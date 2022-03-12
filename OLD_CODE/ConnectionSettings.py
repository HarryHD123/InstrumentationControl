import pygame
from sympy import Si
from Tools.FontRender import RenderFont
import shelve
from InstrumentControl import connect_instrument

class Connection_settings(object):
    def __init__(self, screen):

        self.BLACK = (0,0,0)
        self.RED = (255,0,0)
        self.GREEN = (0,255,0)
        self.LBLUE = (12, 181, 249)
        self.BACKGROUND = (254, 254, 254)
        self.FONTSIZE = 40
        self.FONTSIZE_LARGE = 75

        # Set initial variables
        self.on_connection_settings = True
        self.rerender = True
        self.screen = screen
        self.width, self.height = pygame.display.get_surface().get_size()
        self.scale = self.width/1920

        # Set initial settings
        self.oscilloscope1_string = 'TCPIP0::192.168.1.2::inst0::INSTR'
        self.multimeter1_string = 'TCPIP0::192.168.1.5::5025::SOCKET'
        self.signalgenerator1_string = 'TCPIP0::192.168.1.3::inst0::INSTR'
        self.powersupply1_string = 'TCPIP0::192.168.1.4::inst0::INSTR'

        # Render Initial Text

        self.oscope_textfont = RenderFont("Oscilloscope:", self.FONTSIZE, self.BLACK)
        self.mutlim_textfont = RenderFont("Mulitmeter:", self.FONTSIZE, self.BLACK)
        self.siggen_textfont = RenderFont("Signal Generator:", self.FONTSIZE, self.BLACK)
        self.powers_textfont = RenderFont("Power Supply:", self.FONTSIZE, self.BLACK)

        self.oscope_valfont = RenderFont(f"{self.oscilloscope1_string}", self.FONTSIZE, self.BLACK)
        self.multim_valfont = RenderFont(f"{self.multimeter1_string}", self.FONTSIZE, self.BLACK)
        self.siggen_valfont = RenderFont(f"{self.signalgenerator1_string}", self.FONTSIZE, self.BLACK)
        self.powers_valfont = RenderFont(f"{self.powersupply1_string}", self.FONTSIZE, self.BLACK)

        self.heading_textfont = RenderFont("Connection Menu", self.FONTSIZE_LARGE, self.LBLUE)
        self.reset_textfont = RenderFont("RESET", self.FONTSIZE, self.RED)
        self.connectall_textfont = RenderFont("Connect to all", self.FONTSIZE, self.BLACK)
        self.connected_textfont = RenderFont("Connected", 25, self.GREEN)
        self.not_connected_textfont = RenderFont("Not connected", 25, self.RED)

        # Create buttons
        self.button_list = self.DrawButtons()  # sets the button locations on the screen

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

    def ShowWindow(self):
        """Shows the window for test settings"""
        
        click = False
        typing = False
        self.WriteSettings_Connect()
        text = ''
        self.ReadSettings_Connect()
        oscope_con = False
        multim_con = None
        siggen_con = None
        powers_con = None
        while self.on_connection_settings:

            self.screen.fill((self.BACKGROUND)) 

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.on_connection_settings = False
                    if typing:
                        if event.key == pygame.K_RETURN:
  
                            if self.button_list.index(button_pressed) == 0:
                                self.oscilloscope1_string = text
                            if self.button_list.index(button_pressed) == 1:
                                self.multimeter1_string = text
                            if self.button_list.index(button_pressed) == 2:
                                self.signalgenerator1_string = text
                            if self.button_list.index(button_pressed) == 3:
                                self.powersupply1_string = text

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
                        if self.button_list.index(buttons) == 0:
                            button_pressed = self.button_list[0]
                            self.oscope_valfont = RenderFont("", self.FONTSIZE, self.BLACK)
                            typing = True
                        elif self.button_list.index(buttons) == 1:
                            button_pressed = self.button_list[1]
                            self.multim_valfont = RenderFont("", self.FONTSIZE, self.BLACK)
                            typing = True
                        elif self.button_list.index(buttons) == 2:
                            button_pressed = self.button_list[2]
                            self.siggen_valfont = RenderFont("", self.FONTSIZE, self.BLACK)
                            typing = True
                        elif self.button_list.index(buttons) == 3:
                            button_pressed = self.button_list[3]
                            self.powers_valfont = RenderFont("", self.FONTSIZE, self.BLACK)
                            typing = True
                        elif self.button_list.index(buttons) == 4: # Reset
                            button_pressed = self.button_list[4]
                            self.oscilloscope1_string = 'TCPIP0::192.168.1.2::inst0::INSTR'
                            self.multimeter1_string = 'TCPIP0::192.168.1.5::5025::SOCKET'
                            self.signalgenerator1_string = 'TCPIP0::192.168.1.3::inst0::INSTR'
                            self.powersupply1_string = 'TCPIP0::192.168.1.4::inst0::INSTR'
                            self.rerender = True
                        elif self.button_list.index(buttons) == 5:
                            button_pressed = self.button_list[5]
                            oscope_con = connect_instrument(self.oscilloscope1_string)
                            multim_con = connect_instrument(self.multimeter1_string)
                            siggen_con = connect_instrument(self.signalgenerator1_string)
                            powers_con = connect_instrument(self.powersupply1_string)
                        elif self.button_list.index(buttons) == 6:
                            button_pressed = self.button_list[6]
                            oscope_con = connect_instrument(self.oscilloscope1_string)
                        elif self.button_list.index(buttons) == 7:
                            button_pressed = self.button_list[7]
                            multim_con = connect_instrument(self.multimeter1_string)
                        elif self.button_list.index(buttons) == 8:
                            button_pressed = self.button_list[8]
                            siggen_con = connect_instrument(self.signalgenerator1_string)
                        elif self.button_list.index(buttons) == 9:
                            button_pressed = self.button_list[9]
                            powers_con = connect_instrument(self.powersupply1_string)


                        click = False

            if typing:
                input_box = pygame.Rect(button_pressed)
                text_font = RenderFont(f"{text}", self.FONTSIZE, self.BLACK)
                pygame.draw.rect(self.screen, self.GREEN, input_box)
                self.screen.blit(text_font, [button_pressed[0], button_pressed[1]])

            if self.rerender:
                self.oscope_valfont = RenderFont(f"{self.oscilloscope1_string}", self.FONTSIZE, self.BLACK)
                self.multim_valfont = RenderFont(f"{self.multimeter1_string}", self.FONTSIZE, self.BLACK)
                self.siggen_valfont = RenderFont(f"{self.signalgenerator1_string}", self.FONTSIZE, self.BLACK)
                self.powers_valfont = RenderFont(f"{self.powersupply1_string}", self.FONTSIZE, self.BLACK)
                self.WriteSettings_Connect()
                self.rerender = False

            connected_instr = [oscope_con, multim_con, siggen_con, powers_con]
            connected_instr_count = 0
            for i in connected_instr:
                if i != None:
                    self.screen.blit(self.connected_textfont, [100 * self.scale, (215 + 100 * connected_instr_count) * self.scale])
                else:
                    self.screen.blit(self.not_connected_textfont, [50 * self.scale, (215 + 100 * connected_instr_count) * self.scale])
                connected_instr_count += 1


            self.screen.blit(self.oscope_textfont, [250 * self.scale, 200 * self.scale])
            self.screen.blit(self.mutlim_textfont, [250 * self.scale, 300 * self.scale])
            self.screen.blit(self.siggen_textfont, [250 * self.scale, 400 * self.scale])
            self.screen.blit(self.powers_textfont, [250 * self.scale, 500 * self.scale])

            self.screen.blit(self.reset_textfont, [250 * self.scale, 800 * self.scale])
            self.screen.blit(self.connectall_textfont, [250 * self.scale, 700 * self.scale])
            self.screen.blit(self.heading_textfont, [100 * self.scale, 50 * self.scale])

            self.screen.blit(self.oscope_valfont, [650 * self.scale, 200 * self.scale])
            self.screen.blit(self.multim_valfont, [650 * self.scale, 300 * self.scale])
            self.screen.blit(self.siggen_valfont, [650 * self.scale, 400 * self.scale])
            self.screen.blit(self.powers_valfont, [650 * self.scale, 500 * self.scale])

            pygame.display.update()


    def DrawButtons(self):
        """Draw the buttons for the connections menu"""
        button_list = []
        button_list.append(pygame.Rect(650 * self.scale, 200 * self.scale, 650, 40)) # 1. Oscope Button
        button_list.append(pygame.Rect(650 * self.scale, 300 * self.scale, 650, 40)) # 2. Mulitm Frequency Button
        button_list.append(pygame.Rect(650 * self.scale, 400 * self.scale, 650, 40)) # 3. Siggen Button
        button_list.append(pygame.Rect(650 * self.scale, 500 * self.scale, 650, 40)) # 4. Powers Button
        button_list.append(pygame.Rect(250 * self.scale, 800 * self.scale, 300, 40)) # 5. Reset Button
        button_list.append(pygame.Rect(250 * self.scale, 700 * self.scale, 300, 40)) # 6. Connect all Button
        button_list.append(pygame.Rect(250 * self.scale, 200 * self.scale, 300, 40)) # 7. Connect Oscope Button
        button_list.append(pygame.Rect(250 * self.scale, 300 * self.scale, 300, 40)) # 8. Connect Mulitm Frequency Button
        button_list.append(pygame.Rect(250 * self.scale, 400 * self.scale, 300, 40)) # 9. Connect Siggen Button
        button_list.append(pygame.Rect(250 * self.scale, 500 * self.scale, 300, 40)) # 10. Connect Powers Button

        return button_list