import subprocess
import argparse
from pathlib import Path

description = "This program takes an input PDF file and a text file containing a list of pdfmarks, and calls Ghostscript to create a new PDF with the appropriate bookmarks."
parser = argparse.ArgumentParser(description=description)
parser.add_argument("input", help="Original PDF")
parser.add_argument("marks", help="File containing list of pdfmarks")
parser.add_argument("--output", "-o", help="Output file")
args = parser.parse_args()

def add_bookmarks(original,pdfmarks,output):
    cmd = "gswin64c -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -sOutputFile=%s %s %s" % (output, original, pdfmarks)
    # print("Running command: %s" % (cmd))
    subprocess.run(cmd, capture_output=True)

input = args.input
pdfmarks = args.marks
if args.output:
    output = args.output
else:
    output = Path(input).stem+'_bookmarked.pdf'

add_bookmarks(input, pdfmarks, output)