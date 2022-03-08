import pygame
import os


def Loadify(img):
    return pygame.image.load(img).convert_alpha()


def TransformImage(img, x, y):
    return pygame.transform.scale(img, [x,y])


def LoadBackgroundImages():
    background_image_1 = pygame.image.load(os.path.join("Images", "Backgrounds", "Start line finished 1.png")).convert_alpha()
    background_image_2 = pygame.image.load("Images/Backgrounds/wake me up insidet.png").convert_alpha()
    background_image_1 = TransformImage(background_image_1, 1920, 1080)
    background_image_2 = TransformImage(background_image_2, 1920, 1080)
    background_list = [background_image_1, background_image_2, background_image_2]
    return background_list


def LoadUpgradeBars():
    bar_list = []
    upgrade_bar = pygame.image.load("Images/UpgradeBars/Upgrade bar unlit.png").convert_alpha()
    upgrade_bar = TransformImage(upgrade_bar, 400, 75)
    bar_list.append(upgrade_bar)
    for image in range(10):
        upgrade_bar = pygame.image.load("Images/UpgradeBars/Upgrade bar t" + str(image+1) + ".png").convert_alpha()
        upgrade_bar = TransformImage(upgrade_bar, 400, 75)
        bar_list.append(upgrade_bar)
    return bar_list


def LoadUpgradeButtons():
    button_list = []
    for image in range(9):
        button = pygame.image.load("Images/Buttons/Upgrade Button" + str((image + 1)) + ".png")
        button = TransformImage(button, 120, 60)
        button_list.append(button)
    button_list_1 = button_list[::-1]
    button_list = button_list + button_list_1
    return button_list


def LoadUpgradeLevels():
    level_list = []
    for image in range(11):
        level = Loadify("Images/UpgradeLevel/upgrade level " + str(image) + ".png")
        level = TransformImage(level, 80, 80)
        level_list.append(level)
    return level_list


def LoadVideoButtons():
    button_list = []
    for image in range(3):
        button = Loadify("Images/Buttons/video settings button " + str(image + 1) + ".png")
        button_list.append(button)
    return button_list










