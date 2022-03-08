import pygame


def SaveRes(width, height, mode):
    res_list = [width, height, mode]
    res_file = open("Data/Settings/visual", "w")
    for i in res_list:
        res_file.write(str(i))
        res_file.write("\n")
    res_file.close()


def GetRes():
    res_file = open("Data/Settings/visual", "r")
    res_list = res_file.read().splitlines()
    res_file.close()
    return res_list


def SaveAud(master_level, music_level, sound_level):
    audio_list = [master_level, music_level, sound_level]
    audio_file = open("Data/Settings/audio", "w")
    for i in audio_list:
        audio_file.write(str(i))
        audio_file.write("\n")
    audio_file.close()


def GetAud():
    audio_file = open("Data/Settings/audio", "r")
    audio_list = audio_file.read().splitlines()
    audio_file.close()
    return audio_list
