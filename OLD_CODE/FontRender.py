import pygame


def RenderFont_import(text, size, colour):
    """Easy function that allows you to render a font quickly"""
    return pygame.font.Font("Data/Fonts/PixelFJVerdana12pt.ttf", size).render(text, True, colour)

def RenderFont(text, size, colour, font = 'Corbel'):
    """Renders pygame fonts"""
    pg_font = pygame.font.SysFont(font, size)
    return pg_font.render(text, True, colour)



