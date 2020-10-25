import csv
import argparse
from pathlib import Path

description = "This program takes an input CSV file of bookmark names and page numbers and creates an output file of pdfmarks suitable for use with Ghostscript to create Bookmarks in a PDF file."
parser = argparse.ArgumentParser(description=description)
parser.add_argument("input", help="input filename")
args = parser.parse_args()

def get_children(rows,level):
    myit = iter(rows)
    row = next(myit)
    if get_children(next(myit))
    row_level = int(row['level'])
    print(row)
    if row_level == level:
        # print("Same level: %i" % level)
        print("Children: 0")
        return None
    elif row_level > level:
        get_children(myit,row_level)
    # print((next(myit)["text"]))


def create_pdfmarks(input_filename):
    output_filename = Path(input_filename).stem+'.pdfmarks'

    with open(input_filename, newline='', encoding="utf-8") as csvfile:
        fieldnames = ["toc_type","level","text","page"]
        reader = csv.DictReader(csvfile, fieldnames=fieldnames, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        output_file = open(output_filename,'w',newline='', encoding="utf-8")
        toc_level = 0
        background_count = 0
        rules_count = 0
        prev_level = 0
        current_section = ""
        prev_section = ""
        prev_toc_type = ""
        parent = {}
        entry_list = []
        entries = []
        last_entry = {"level":-1}
        children = []

        for row in reader:
            toc_type = row["toc_type"]
            level = int(row["level"])
            title = row["text"]
            page = row["page"]
            
            if level == int(last_entry["level"]):
                if int(last_entry["level"]) == 0:
                    entry_list.append(last_entry)
                else:
                    entries.append(last_entry)
            elif level > int(last_entry["level"]):
                entry_list.append(last_entry)
                
                if level == 0:
                    for child in children:
                        entries.append(child)
                        print(f"adding {child['text']} with no children")
                else:
                    parent = last_entry
                    print(f"{parent['text']} is now a parent")
            elif level < int(last_entry["level"]):
                parent["children"] = children
                entries.append(parent)
                print(f"adding {parent['text']} with {len(parent['children'])} children")
            last_entry = row

        for entry in entries:
            if "children" in entry.keys():
                print(len(entry["children"]))
if args.input:
    # create_pdfmarks(args.input)
    with open(args.input, newline='', encoding="utf-8") as csvfile:
        fieldnames = ["toc_type","level","text","page"]
        reader = csv.DictReader(csvfile, fieldnames=fieldnames, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        for row in reader:
            get_children(reader,0)
else:
    print("You must specify an input filename with --input or -i")




