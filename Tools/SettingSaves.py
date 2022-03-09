
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

