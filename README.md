# Convert_LTspice_to_Latex
Convert LTspice to Latex (TikZ)

## Setup
1. Install Python 3
2. Install LTspice
3. Latex packages: tikz, circuitikz, (amsmath)
 
## How to convert LTspice schematic to Latex TikZ picture?
All functions to convert LTspice to Latex are in the file 'LTspiceToTexConverter.py'.
The function *LtSpiceToLatex* converts one file and *ConvertForAllLTspiceFilesFormFolderToTEX* converts all files in the current folder to .tex

**LtSpiceToLatex(saveFile = '', filenameLTspice = 'Draft.asc', lt_spice_directory = r'C:\Program Files\LTC\LTspiceXVII\lib\sym', fullExample=0)**
* **saveFile: string**
	* name for the tex-file, if empty use LTSpice filename
* **filenameLTspice: string**
	* file to be converted (LTspice filename)
* **lt_spice_directory: string**
	* LTspice install directory
* **fullExample: int**
	* 0: output file contains only tikzpicture
	* 1: outputfile is a directly compilable tex-file
	
**ConvertForAllLTspiceFilesFormFolderToTEX(path='.', lt_spice_directory = r'C:\Program Files\LTC\LTspiceXVII\lib\sym', fullExample=0)**
* **path: string**
	* path to folder (default: current directory)
* **lt_spice_directory: string**
	* LTspice install directory
* **fullExample: int**
	* 0: output file contains only tikzpicture
	* 1: outputfile is a directly compilable tex-file
