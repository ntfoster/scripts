import xml.etree.ElementTree as ET
import argparse
import re
import decimal

parser = argparse.ArgumentParser()
parser.add_argument("input", help="input .sla file")
parser.add_argument("--fix_scale",action="store_true",default=False)
parser.add_argument("--move_pdf",action="store_true",default=False)
parser.add_argument("--fix_links",action="store_true",default=False)

args = parser.parse_args()

input = args.input

tree = ET.parse(input)
root = tree.getroot()

file_pattern = r".+\.(pdf|ai)"
file_re = re.compile(file_pattern)

def fix_pdf_scale():
    for element in root.findall(f"./DOCUMENT/PAGEOBJECT[@LAYER='3']"): # if on rules layer
        if 'PFILE' in element.attrib:
            if file_re.match(element.get("PFILE")): # if a .pdf file
                if element.get("LOCALSCX") == "0.24":
                    element.set("LOCALSCX","1.00")
                    element.set("LOCALSCY","1.00")

def set_rules_pdf_pos(x,y):

    x_move = x * decimal.Decimal('2.83464566930343')
    y_move = y * decimal.Decimal('2.83464566930343')
     
    for element in root.findall(f"./DOCUMENT/PAGEOBJECT[@LAYER='3']"):
        if 'PFILE' in element.attrib:
            if file_re.match(element.get("PFILE")):
                decimal.getcontext().prec = 10
                old_ypos = decimal.Decimal(element.get("YPOS"))
                new_ypos = old_ypos + y_move
                element.set("YPOS",str(new_ypos))
                # print(f"Old value: {old_ypos}; New Value: {new_ypos}")

def fix_hyperlinks(links):
        for element in root.findall(f"./DOCUMENT/PAGEOBJECT[@ANTYPE='11']"):
                for link in links:
                    if link["name"] == element.get("ANNAME"):
                        # print("match!")
                        page = str(int(link["page"])-1)
                        element.set("ANZIEL",page)
                        element.set("ANACTION","0 0 0") # set target to top of page
if args.fix_scale:
    fix_pdf_scale()
if args.move_pdf:
    set_rules_pdf_pos(0,-3)
if args.fix_links:
    # se_links = [{"name":"rh1", "page":"38"}, {"name":"rh2", "page":"39"}, {"name":"rh3", "page":"40"}, {"name":"rh4", "page":"40"}, {"name":"rh5", "page":"41"}, {"name":"rh6", "page":"43"}, {"name":"rh7", "page":"43"}, {"name":"rh8", "page":"47"}, {"name":"rh9", "page":"49"}, {"name":"rh10", "page":"51"}, {"name":"rh11", "page":"54"}, {"name":"rh12", "page":"56"}]
    wdg_links = [{"name":"rh1","page":"88"}, {"name":"rh2","page":"90"}, {"name":"rh3","page":"90"}, {"name":"rh4","page":"91"}, {"name":"rh5","page":"91"}, {"name":"rh6","page":"95"}, {"name":"rh7","page":"99"}, {"name":"rh8","page":"101"}, {"name":"rh9","page":"107"}, {"name":"rh10", "page":"110"}]
    # ud_links = [{"name":"rh1", "page":"40"}, {"name":"rh2", "page":"41"}, {"name":"rh3", "page":"42"}, {"name":"rh4", "page":"43"}, {"name":"rh5", "page":"44"}, {"name":"rh6", "page":"44"}, {"name":"rh7", "page":"48"}, {"name":"rh8", "page":"50"}, {"name":"rh9", "page":"52"}, {"name":"rh10", "page":"54"}, {"name":"rh11", "page":"55"}, {"name":"rh12", "page":"56"}, {"name":"rh13", "page":"58"} ]
    fix_hyperlinks(wdg_links)
# for link in links:
#     print(f'{link["name"]} => {link["page"]}')
# fix_hyperlinks(links)

tree.write(input)