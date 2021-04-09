# README - Copy Number  Parser

##  About the program

The program was created to facilitate the search of fragment information about one or more target chromosomes in a Copy Number Data file.

## Installation

The program is written in Python, and uses the following versions:

- Python 3.8.5

No additional installation is needed.

## Input file

The program is designed to parse a default Copy Number Data file, which means a tab-separated values (TSV) file.

## Running the program

The program can be run through command line.

```
python cpn_parser.py --infile copy_number.txt --chr chrN
```

#### Flag options:

- **-i** or **--infile:** single copy number data file.
- **-d** or **--dir:** directory containing more than one copy number data file.
- **-c** or **--chr:** target chromosome that will be searched. The chromosome must be informed in standard format (chrN). More than one chromosome can be searched at the same time, they must be separated by **,** . It is also possible to search for a range of chromosomes, in this case the initial and the last chromosome must be separated by **:** . 
- **-o** or **--out:** Optional output file. If not informed the result will be printed on standard output.

The required arguments are: **--infile** or **--dir** and **--chr**.  

## Results

The program only retrieve the information if the chromosome(s) selected have fragments (abnormalities). The output contains the file name, the selected chromosome, and the number of fragments found. For each fragment, the start and end positions are displayed, together with the copy number. The gap between fragments is also informed, with start and end positions and the gap length in base pairs. 

  [File name] [target chromosome] [number of fragments]
  Fragment position [start-end] [Copy number]
  Gap position [start-end]  Length
  Fragment position [start-end] [Copy number]

If more than one chromosome is selected the information is separated by a new line between chromosomes. If more than one file is selected, the information is separated by two new line between files.
