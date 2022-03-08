import pygame
from Tools.PictureUploads import Loadify, TransformImage
from Menu.SettingSaves import GetRes

pygame.init()
width = int(GetRes()[0])
height = int(GetRes()[1])
mode = (GetRes()[2])
if mode == "fullscreen":
    screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
else:
    screen = pygame.display.set_mode([width, height])
""" Run Game intro """


""" Load initialise screen """


"""Load every image used within game and save them to variable to be called"""

# # Tier 1 User Car Loaded
# tier_1_user_car_images = []
# for num in range(4):
#     tier_1_user_car_images.append(Loadify("Images/CarSprites/Tier1/greencarfr" + str(num+1) + ".png"))

# # Tier 1 Blue Car Loaded
# tier_1_blue_car_images = []
# for num in range(4):
#     tier_1_blue_car_images.append(Loadify("Images/CarSprites/Tier1/bluecarfr" + str(num+1) + ".png"))

# # Tier 1 Purple Car Loaded
# tier_1_purple_car_images = []
# for num in range(4):
#     tier_1_purple_car_images.append(Loadify("Images/CarSprites/Tier1/purplecarfr" + str(num+1) + ".png"))

# # Tier 1 Grey Car Loaded
# tier_1_grey_car_images = []
# for num in range(4):
#     tier_1_grey_car_images.append(Loadify("Images/CarSprites/Tier1/greycarfr" + str(num+1) + ".png"))

# # Tier 1 Boss Car Loaded
# tier_1_boss_car_images = []
# for num in range(4):
#     tier_1_boss_car_images.append(Loadify("Images/CarSprites/Tier1/boss1carfr" + str(num+1) + ".png"))


# # Buttons Loaded
# buttons_images = []
# for image in range(9):
#     button = Loadify("Images/Buttons/Upgrade Button" + str((image + 1)) + ".png")
#     button = TransformImage(button, 120, 60)
#     buttons_images.append(button)
# button_list_1 = buttons_images[::-1]
# buttons_images = buttons_images + button_list_1


# # Upgrade Bars Loaded
# upgrade_bars_images = []
# upgrade_bar = Loadify("Images/UpgradeBars/Upgrade bar unlit.png")
# upgrade_bar = TransformImage(upgrade_bar, 400, 75)
# upgrade_bars_images.append(upgrade_bar)
# for image in range(10):
#     upgrade_bar = Loadify("Images/UpgradeBars/Upgrade bar t" + str(image+1) + ".png")
#     upgrade_bar = TransformImage(upgrade_bar, 400, 75)
#     upgrade_bars_images.append(upgrade_bar)


# # Upgrade Levels Text Loaded
# upgrade_levels_text_images = []
# for image in range(11):
#     level = Loadify("Images/UpgradeLevel/upgrade level " + str(image) + ".png")
#     level = TransformImage(level, 80, 80)
#     upgrade_levels_text_images.append(level)


# # Numbers for Money
# numbers_money_images = []
# for num in range(10):
#     numbers_money_images.append("Images/Numbers/number " + str(num) + "png")
# numbers_money_images.append("Images/Numbers/money symbol.png")
# numbers_money_images.append("Images/Numbers/comma for numbers.png")

# # Backgrounds


""" Click to enter main menu """

