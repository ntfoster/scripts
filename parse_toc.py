import xml.etree.ElementTree as ET
import csv

input = "lab.sla" # TODO: Parameterise
tree = ET.parse(input)
root = tree.getroot()
output = input+".toc.csv" # TODO: strip extension

# print(root.attrib)

def parse_toc(): # scans text in the TOC_Background frame to build bookmarks
    toc_labels = []
    for element in root.findall("./DOCUMENT/PAGEOBJECT[@ANNAME='TOC_Background']/StoryText"):
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
    for element in root.findall("./DOCUMENT/PAGEOBJECT[@PSTYLE='HEADER Level 1']"):
        page = int(element.get("OwnPage"))+1
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


