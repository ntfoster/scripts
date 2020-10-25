#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import argparse
# from pathlib import Path
import os

# TODO: switch for keeping original files or not
description = "This program takes an input PDF file and a text file containing a list of pdktk info marks, and calls pdftk to create a new PDF with the appropriate bookmarks."
parser = argparse.ArgumentParser(description=description)
parser.add_argument("input", help="Original PDF")
parser.add_argument("marks", help="File containing list of pdftk info")
parser.add_argument("--output", "-o", help="Output file")
parser.add_argument("--keep", action="store_true", help="keep copies of original files with '_original' suffix.", default=False)

args = parser.parse_args()

PDFTK_PATH = "pdftk" # TODO: Automatically handle Windows/macOS/Linux defaults?

def add_bookmarks(original,pdfmarks,output):

    arguments = f'"{original}" update_info_utf8 "{pdfmarks}" output "{output}"'

    cmd = f"{PDFTK_PATH} {arguments}"
    print("Running command: %s" % (cmd))
    subprocess.run(cmd, shell=True)

input = args.input
pdfmarks = args.marks

if args.output:
    output = args.output
else:
    output = os.path.splitext(input)[0]+'_bookmarked.pdf'

add_bookmarks(input, pdfmarks, output)
if args.keep:
    os.replace(input,os.path.splitext(input)[0]+'_original.pdf')
else:
    os.remove(input)
os.replace(output,input)
