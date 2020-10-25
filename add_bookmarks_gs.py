#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import argparse
from pathlib import Path
import os

description = "This program takes an input PDF file and a text file containing a list of pdfmarks, and calls Ghostscript to create a new PDF with the appropriate bookmarks."
parser = argparse.ArgumentParser(description=description)
parser.add_argument("input", help="Original PDF")
parser.add_argument("marks", help="File containing list of pdfmarks")
parser.add_argument("--output", "-o", help="Output file")
args = parser.parse_args()

ghostscript_path = "gswin64c" # TODO: Automatically handle Windows/macOS/Linux defaults?

def add_bookmarks(original,pdfmarks,output):

    ghostscript_arguments = f'-dBATCH -dNOPAUSE -sDEVICE=pdfwrite -o "{output}" "{original}" "{pdfmarks}"'

    # cmd = "gswin64c -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -sOutputFile=%s %s %s" % (output, original, pdfmarks)
    cmd = f"{ghostscript_path} {ghostscript_arguments}"
    print("Running command: %s" % (cmd))
    subprocess.run(cmd, shell=True)

input = args.input
pdfmarks = args.marks
if args.output:
    output = args.output
else:
    output = str(Path(input).parent) + '\\' + Path(input).stem+'_bookmarked.pdf'
    # output = input+'_bookmarked.pdf'

add_bookmarks(input, pdfmarks, output)
# os.remove(input)
# os.rename(output,input)
