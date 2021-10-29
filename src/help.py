# <OmpTG>  Copyright (C) <2021>  < Tao Jin; Jinrong Liu; >
# This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
# This is free software, and you are welcome to redistribute it
# under certain conditions; type `show c' for details.

Options = \
    {'i': 'Input Files.',
     'w': 'Generate WCET for the file imported.',
     't': 'Generate ALF for every OpenMP task that fit SWEET.',
     'h': 'Show Help.'
     }


def ShowOptions():
    if __name__ == '__main__':
        print('Please run in main module.')
    else:
        for key in Options:
            print('-' + key + ' ' + Options[key])
