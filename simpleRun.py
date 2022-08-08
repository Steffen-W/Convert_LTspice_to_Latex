import os

from LTspiceToTexConverter import *

if os.name == 'nt':
    print("OS: is Windows")
    path_ltspice = r'C:\Program Files\LTC\LTspiceXVII\lib\sym'
else:
    print("OS: is NOT Windows")
    path_ltspice = '~/.wine/drive_c/Program Files/LTC/LTspiceXVII/lib/sym'

fileName_input = 'Draft.asc'
print("input:  ", fileName_input)

out = LtSpiceToLatex(filenameLTspice=fileName_input,
                     lt_spice_directory=os.path.expanduser(path_ltspice),
                     fullExample=1)

# print(out)
