#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title: Copy Number Parser

Created on: Wed Oct 28, 2020
Author: Arthur Boffelli Castro

"""

import os
import argparse
import platform

###############################################################################
# Argparse section

usage = '''Retrieve information of target chromosome(s) fragments in 
one or several Copy Number Data files.'''
parser = argparse.ArgumentParser(description=usage)

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument(
        '-d', '--dir', type=str, metavar='FOLDER', dest='fold_path',
        help='Path to directory containing the files.'    
        )

group.add_argument(
        '-i', '--infile', dest='infile', metavar='INFILE',
        type=str,
        help='Single file to be read.'
        )


parser.add_argument(
        '-c', '--chr', dest='tg_chr', metavar='chrN',
        type=str, help='''Target chromosome in standard format (chr1, chr2 ...
        chrX, chrY).
        If more than one chromosome, they must be separated by ','.
        If range of chromosomes, the initial and the last chromosomes must be 
        separated by ':'. '''
        )


parser.add_argument(
        '-o', '--out', dest='outfile', metavar='OUTFILE',
        type=str, help='''Optional output file. If not informed, the result 
        will be printed on the screen.'''
        )


args = parser.parse_args()

###############################################################################
# Functions section


def check_file(file):
    """
    Function to check if the file is a Copy Number Data and has all the columns
        needed for the program.
    
    :param file: file path (str)

    :return: True if the file has the necessary conditions. If not, print a warning 
        message and return False.
    """
    with open(file, 'r') as infile:
        # reads the first line and transform it into a list.
        header = infile.readline().split() 
        # words that must be present in the file
        check_words = ['Chromosome', 'Start', 'End', 'Cn']
        for word in check_words:
            # if the word is found in the list continue to the other words
            if word in header: continue
            else:
                # if the word is not present, print message and break the loop
                print('Warning: The file "{}" is not in the right format.'\
                      .format(file.split('/')[-1]))
                break
        # Else statement only executed if the loop did not break (all words are
        #   present).
        else: 
            return True


def chr_set(string):
    """
    Function to create a set with all target chromosomes.
    
    :param string: target chromosome (str)

    :return: set containing the target chromosomes.
    """
    # create an empty set
    chr_set = set()
    # split the string in the ',' separator.
    string_list = string.split(',')
    for line in string_list:
        # if ':' is present, it is a range of chromosomes.
        if ':' in line:
            # split in the ':'
            chromosome_list = line.split(':')
            # transform chromosome X and Y in numbers.
            if 'chrX' in chromosome_list:
                chromosome_list[chromosome_list.index('chrX')] = 'chr23'
            if 'chrY' in chromosome_list:
                chromosome_list[chromosome_list.index('chrY')] = 'chr24'    
            # start a loop with initial value as the first chromosome number
            #   and end in the second chromosome number +1.
            for i in range(int(chromosome_list[0][3:]),
                        int(chromosome_list[1][3:])+1):
                # add all the chromosomes of the range to the set.
                chr_set.add('chr'+str(i))
        # add single chromosome to the set
        else:
            chr_set.add(line)

    return chr_set


def find_fragments(file):
    """
    Function that will look for the target chromosome(s) and write the 
        information to the output.
        
    :param file: file path (str)

    :return: print the information in the output. 
    """
    # remove the whole path of the file name.
    file_name = file.replace('\\', '/').split('/')[-1]
    # call the function to create the set of target chromosomes.
    target = chr_set(args.tg_chr)
    # creates an empty dictionary and a fragment flag.
    frag_dict = {}
    frag = False
    with open(file, 'r') as file:
        for line in file:
            # creates a list with the line.
            line_list = line.strip().split('\t')
            # check if the chromosome of the line is in the target set.
            if line_list[0] in target:
                # checks if the chromosome was already added to the dictionary,
                #   avoiding overwriting keys.
                if line_list[0] not in frag_dict:
                    # create a new key with the chr and a list containing a 
                    #   sublist [start, end, copy number] as value.
                    frag_dict[line_list[0]] = [[int(line_list[1]),
                                  int(line_list[2]), int(line_list[-3])]]
                else:
                    # if the key alredy exists (fragment), add a new sublist 
                    #   to the value list.
                    frag_dict[line_list[0]].append([int(line_list[1]),
                                  int(line_list[2]), int(line_list[-3])])
    # After all the lines were read, start a loop through all the keys in the
    #   dict.
    for key in frag_dict:
        # if the length of the value list is bigger than 1, it means that the
        #   chromosome has fragments (print the information).
        if len(frag_dict[key]) > 1:
            # The fragment flag becomes True.
            frag = True
            # create a new list with the gap length between segments.
            frag_list = gap_length(frag_dict[key])
            # write in the output 'file name, chromosome, number of fragments'
            outfile.write('{} {}\t{} fragments\n'.format(file_name, key,
                          len(frag_dict[key])))
            # loop through all the objects in the new list.
            for frag in frag_list:
                # If not an int (fragment position).
                if type(frag) is not int:
                    # write the information in the output.
                    outfile.write('Fragment position\t{}-{}\tCn {}\n'.format(
                            frag[0], frag[1], frag[2]))
                else: # if is an int (gap length)
                    # retrive the start and the end of the gap.
                    gap_start = frag_list[frag_list.index(frag) - 1][1]
                    gap_end = frag_list[frag_list.index(frag) + 1][0]
                    # write the information in the output.
                    outfile.write('Gap position\t{}-{}\tLength {}\n'.format(
                        gap_start, gap_end, frag))
            # print a black line between chromosomes 
            # (1 blank line between chromosomes in the same file).
            outfile.write('\n')

    if frag:
        # print a blank line between files (2 blank lines between files) 
        # (only if the file had fragments), avoid stacking blank lines.
        outfile.write('\n')
        frag = False


def gap_length(fragment_list):
    """
    Function that calculates the fragment length and add the value between the
        two segments.
    
   :param fragment_list: list containing sublists with information about 
        the fragments of one chromosome. (list)

    :return: list containing the fragment information and the gap information 
        (length and position) between each fragment.
    """
    # create a copy of the list given as an argument (avoids error in the loop)
    gaps_list = fragment_list.copy()
    # loop in a range of the size of the list. 1 is subtracted to avoid errors
    # in the index position.
    for i in range(len(fragment_list)-1):
        # calculate the gap length by subtracting the start position of a 
        # fragment and the end position of the fragment before.
        gap = fragment_list[i+1][0] - fragment_list[i][1]
        # calculate the position of the gap in the list by the index postion
        # of the first segment plus 1.
        position = gaps_list.index(fragment_list[i]) + 1
        # insert the gap in the copy list between the both fragments.
        gaps_list.insert(position, gap)

    return gaps_list


###############################################################################
# Running Code

infile = args.infile

# If the output file is not informed
if not args.outfile:
    # check which operating system the user is using.
    if platform.system() == 'Linux':
        # if Linux the stdout path for Linux becomes the outfile
        outfile = '/dev/stdout'
    elif platform.system() == 'Windows':
        # if Windows the stdout path for Windows becomes the outfile
        outfile = '\CON'
    # I could not find the path of stdout for Mac. If Mac the program will not
    # print in the screen.
else: # if the outfile was informed.
    outfile = args.outfile

# open the file
with open(outfile, 'w') as outfile:
    # if a directory was passed as input
    if args.fold_path:
        # check the directory existance.
        if os.path.isdir(args.fold_path):
            # transform all the directory files into a list.
            file_list = os.listdir(args.fold_path)
            # loop through all the files in the list
            for file in file_list:
                # adds the folder path to the file name, to avoid errors if the
                # program is not in the same directory.
                file = args.fold_path + file
                # check if the file exists with file_existance function
                if file_existance(file):
                    # check if the file is Copy Number Data with check_file 
                    # function
                    if check_file(file):
                        # finally call the function to find the fragments.
                        find_fragments(file)
    # if a single file was passed as input
    if infile:
        # check if the file exists
        if os.path.exists(infile):
             # check if the file is Copy Number Data with check_file function
            if check_file(infile):
                # finally call the function to find the fragments.
                find_fragments(infile)

# print the message 'Done', to confirm that the program is over.
print('Done!')
