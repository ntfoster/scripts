import xml.etree.ElementTree as ET
import csv
from pathlib import Path
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("input", help="input .sla file")
args = parser.parse_args()

if args.input:
    input = args.input

background_toc_frame = 'TOC'
rules_toc_frame = 'TOC2'
header_style = 'HEADER Level 1'

tree = ET.parse(input)
root = tree.getroot()
output = Path(input).stem+".toc.csv" 

# print(root.attrib)

def add_custom_labels(labels):
    custom_labels = [{"type":"General", "level":1, "label":"Cover", "page":1},{"type":"General", "level":1, "label":"Credits", "page":4}]
    labels.append(custom_labels)
    return labels

def parse_toc(frame): # scans text in the TOC_Background frame to build bookmarks
    toc_labels = []

    page_pattern = r"\d+"
    page_regex = re.compile(page_pattern)

    for element in root.findall(f"./DOCUMENT/PAGEOBJECT[@ANNAME='{frame}']/StoryText"):
        # para_style = "TOC level 1"
        level=1
        label = ""
        page = ""
        text = ""
        for child in element:
            if child.tag == "MARK":
                label = child.get("label")
            if child.tag == "ITEXT":
                if page_regex.match( child.get("CH").lstrip() ):
                    page = child.get("CH").lstrip()
                elif child.get("CH") != " ":
                    text = child.get("CH")
            if child.tag == "para":
                para_style = child.get("PARENT")
                if para_style == "TOC level 2":
                    level=2
                else:
                    level=1
                entry = {"level":level, "label":label, "text":text, "page":page}
                toc_labels.append(entry)
                label = ""
                page = ""
                text = ""
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
            entry["text"] = entry["label"]
            for mark in marks:
                if mark.get("label") == entry["label"]:
                    entry["text"] = mark.get("str")
            
    return labels

def write_csv(entries):
    with open(output, "w", newline="", encoding='utf-8') as csvfile:
        fieldnames = ["level","text","page","children"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # writer.writerows(entries)
        for entry in entries:
            if 'children' not in entry.keys():
                entry["children"] = 0
            writer.writerow({"level":entry["level"],"text":entry["text"],"page":entry["page"],"children":entry["children"]})
            # print(entry['type'])

# add same labels to front of every book
custom_labels = [{"level":"0", "label":"Cover", "page":"1"},{"level":"0", "label":"Credits", "page":"4"}]
labels_background = parse_toc(background_toc_frame)
background_count = len(labels_background)
labels_rules = parse_toc(rules_toc_frame)
rules_count = len(labels_rules)
labels = custom_labels + [{"level":"0", "label":"Background", "page":"1", "children":background_count}] + labels_background + [{"level":"0", "label":"Rules", "page":"1", "children":rules_count}] + labels_rules
entries = lookup_labels(labels)
# print(entries)
write_csv(entries)


