import xml.etree.ElementTree as ET
import re
import argparse
import os
import sys

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input .sla file")
    parser.add_argument("--newfile", help="new PDF filename, otherwise defaults to existing name + '_nopoints'")
    parser.add_argument("--output", "-o", action="store_true", help="Create new .sla file with '_nopoints suffix'") # TODO: parameterise suffix?
    args = parser.parse_args()

    if args.newfile:
        if os.path.isfile(args.filename):
            new_filename = args.filename
        else:
            raise FileNotFoundError("Specified new filename does not exist")

    tree = ET.parse(args.input)
    root = tree.getroot()

    # print(root.attrib)
    pdf_pattern = r".+\.(pdf|ai)"
    pdf_re = re.compile(pdf_pattern)

    for element in root.findall(f'./DOCUMENT/PAGEOBJECT[@LAYER="3"]'): # TODO: look up correct layer number first
        if "PFILE" in element.attrib:
            if 'PFILE' in element.attrib:
                if pdf_re.match(element.get("PFILE")):
                    old_filename = os.path.splitext(element.get("PFILE"))[0]
                    if args.newfile:
                        element.set("PFILE",new_filename)
                    else:
                        element.set("PFILE", old_filename+'_nopoints.pdf')

    output_filename = os.path.splitext(args.input)[0]+'_nopoints.sla'
    if args.output:
        tree.write(output_filename)
    else:
        tree.write(args.input)

if __name__ == '__main__':
    main(sys.argv)