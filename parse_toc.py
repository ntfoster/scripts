import xml.etree.ElementTree as ET
import csv
from pathlib import Path

input = "lab.sla" # TODO: Parameterise
background_toc_frame = 'TOC_Background'
rules_toc_frame = 'TOC_Rules'
header_style = 'HEADER Level 1'

tree = ET.parse(input)
root = tree.getroot()
output = Path(input).stem+".toc.csv" 

# print(root.attrib)

def parse_toc(): # scans text in the TOC_Background frame to build bookmarks
    toc_labels = []
    for element in root.findall(f"./DOCUMENT/PAGEOBJECT[@ANNAME='{background_toc_frame}']/StoryText"):
        for child in element:
            if child.tag == "MARK":
                label = child.get("label")
            if child.tag == "ITEXT":
                if child.get("CH") != " ":
                    page = child.get("CH").lstrip()
            if child.tag == "para":
                entry = {"label":label, "text":"", "page":page}
                toc_labels.append(entry)
    # print(toc_labels)
    return toc_labels

def parse_headers(): # scans for 'HEADER Level 1' text to build bookmarks
    header_labels = []
    # for object in root.findall("./DOCUMENT/PAGEOBJECT/StoryText/DefaultStyle[@PARENT='HEADER Level 1']"):
    for element in root.findall(f"./DOCUMENT/PAGEOBJECT[@PSTYLE='{header_style}']"):
        page = int(element.get("OwnPage"))+1 # Scribus interal page numbers start at 0, so are 1 less than 'real' page numbers 
        for storytext in element:
            for child in storytext:
                if child.tag == "MARK":
                    label = child.get("label")
                    entry = {"label":label, "text":"", "page":page}
                    header_labels.append(entry)
                    # print(entry)
                if child.tag == "ITEXT":
                    text = child.get("CH")
                    entry = {"label":"", "text":text, "page":page}
                    header_labels.append(entry)
    # print(header_labels)
    return header_labels

def lookup_labels(labels):
    marks = root.find("./DOCUMENT/Marks")
    for entry in labels:
        if entry["label"] != "":
            for mark in marks:
                if mark.get("label") == entry["label"]:
                    entry["text"] = mark.get("str")
    return labels

def write_csv(entries):
    with open(output, "w", newline="") as csvfile:
        fieldnames = ["text","page"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # writer.writerows(entries)
        for entry in entries:
            writer.writerow({'text':entry['text'],'page':entry['page']})


labels = parse_toc()
entries = lookup_labels(labels)
write_csv(entries)


