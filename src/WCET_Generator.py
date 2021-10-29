# <OmpTG>  Copyright (C) <2021>  < Tao Jin; Jinrong Liu; >
# This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
# This is free software, and you are welcome to redistribute it
# under certain conditions; type `show c' for details.
import os


def WCET_Output(WCETList, FileNameImported):
    File = open(FileNameImported + '.wct', 'w')
    for key in WCETList:
        File.write(str(key) + ' ' + str(WCETList[key]) + '\n')
    File.close()
