import csv
import argparse
from pathlib import Path

description = "This program takes an input CSV file of bookmark names and page numbers and creates an output file of pdfmarks suitable for use with Ghostscript to create Bookmarks in a PDF file."
parser = argparse.ArgumentParser(description=description)
parser.add_argument("input", help="input filename")
args = parser.parse_args()

def create_pdfmarks(input_filename):
    output_filename = Path(input_filename).stem+'.pdfmarks'

    with open(input_filename, newline='', encoding="utf-8") as csvfile:
        fieldnames = ["level","text","page","children"]
        reader = csv.DictReader(csvfile, fieldnames=fieldnames, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        output_file = open(output_filename,'w',newline='', encoding="utf-8")

        output_file.write('[ /PageMode /UseOutlines  /Page 1  /DOCVIEW pdfmark\n')

        for row in reader:
            level = int(row["level"])
            title = row["text"]
            page = row["page"]
            children = int(row["children"])
            
            if children > 0:
                output_file.write(f'[/Count {children} /Title ({title}) /Page {page} /OUT pdfmark\n')
            else:
                output_file.write(f'[/Title ({title}) /Page {page} /OUT pdfmark\n')
        output_file.close
    csvfile.close

if args.input:
    create_pdfmarks(args.input)
else:
    print("You must specify an input filename with --input or -i")




