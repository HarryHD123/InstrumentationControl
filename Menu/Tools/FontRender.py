import pygame
from Tools.PictureUploads import Loadify, TransformImage


def RenderFont(text, size, colour):
    """Easy function that allows you to render a font quickly"""
    return pygame.font.Font("Data/Fonts/PixelFJVerdana12pt.ttf", size).render(text, True, colour)


class CreateNumber(object):
    def __init__(self, text, width, height, screen, sign):
        self.width = width
        self.height = height
        self.money_symbol = Loadify("Images/Numbers/money symbol.png")
        self.money_symbol = TransformImage(self.money_symbol, self.width, self.height)
        self.screen = screen
        self.comma = Loadify("Images/Numbers/comma for numbers.png")
        self.comma = TransformImage(self.comma, self.width, self.height)
        self.text = int(text)
        self.text = str(format(self.text, ',d'))
        if sign:
            self.text_list = [self.money_symbol]
            self.is_comma = [0]
        else:
            self.text_list = []
            self.is_comma = []
        for numbers in self.text:
            if numbers.isnumeric():
                numbers = Loadify("Images/Numbers/number " + str(numbers) + ".png")
                numbers = TransformImage(numbers, self.width, self.height)
                self.is_comma.append(0)
            else:
                numbers = self.comma
                self.is_comma.append(1)
            self.text_list.append(numbers)

    def ShowNumber(self, x_position, y_position):
        counter = 0
        for numbers in self.text_list:
            if self.is_comma[counter] == 0:
                self.screen.blit(numbers, [x_position + (self.width * counter)/2, y_position])
            elif self.is_comma[counter] == 1:
                self.screen.blit(numbers, [x_position + (self.width * counter)/2, y_position + 5/32 * self.width])
            counter += 1



