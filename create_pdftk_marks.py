import csv
import argparse
from pathlib import Path

description = "This program takes an input CSV file of bookmark info in 'level,name,page,children' format, and creates an output file of pdfmarks suitable for use with pdftk to create bookmarks in a PDF file."
parser = argparse.ArgumentParser(description=description)
parser.add_argument("input", help="input filename")
args = parser.parse_args()

def create_pdfmarks(input_filename):
    output_filename = Path(input_filename).stem+'_pdftk.txt'

    with open(input_filename, newline='', encoding="utf-8") as csvfile:
        fieldnames = ["level","text","page","children"]
        reader = csv.DictReader(csvfile, fieldnames=fieldnames, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        of = open(output_filename,'w',newline='', encoding="utf-8") # output file

        # output_file.write('[ /PageMode /UseOutlines  /Page 1  /DOCVIEW pdfmark\n')

        for row in reader:
            level = int(row["level"])
            title = row["text"]
            page = row["page"]
            
            of.write('BookmarkBegin\n')
            of.write(f'BookmarkTitle: {title}\n')
            of.write(f'BookmarkLevel: {level+1}\n')
            of.write(f'BookmarkPageNumber: {page}\n')

        of.close
    csvfile.close

if args.input:
    create_pdfmarks(args.input)
else:
    print("You must specify an input filename with --input or -i")




