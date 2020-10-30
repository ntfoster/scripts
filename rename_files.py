import os
import re
import argparse
import shutil

# An example input filename is "T9A-FB_LAB_UD_EN_v1_full_high.pdf"

parser = argparse.ArgumentParser()
parser.add_argument("files", type=argparse.FileType('r'), nargs='+', help="file to be renamed")
parser.add_argument('--version','-v', help="rules version")
parser.add_argument("--keep", action="store_true", help="Do not delete original files", default=False)
args = parser.parse_args()

if args.version:
    version = args.version
else:
    version = "2020"

files = args.files

t9a_pattern = r't9a-fb_lab_(\w+)_(\w+)_v1_(\w+)_(\w+)\.pdf'
t9a_re = re.compile(t9a_pattern)

for f in files:
    with f:
        filename = os.path.basename(f.name)
    result = t9a_re.match(filename.lower())
    if result:
        army = result.group(1)
        lang = result.group(2)
        format = result.group(3)
        quality = result.group(4)
        if quality =="print":
            quality = "press"
        if quality == "low":
            quality = "online"
        if quality == "high":
            quality = "print"
        if format == "norules":
            format = "background"
            new_filename = f"t9a-fb_lab_{quality}_{army}_{format}_{lang}.pdf" # no version string needed for background book
        else:
            new_filename = f"t9a-fb_lab_{quality}_{army}_{format}_{version}_{lang}.pdf"
        new_filename = os.path.dirname(f.name) + '\\' + new_filename.replace("_wdg_", "_wotdg_") # TODO: split off into separate function with dictionary of replacements
    # print(f'{f.name} => {new_filename}')
    print(new_filename)
    shutil.copy(f.name,new_filename)
    if not args.keep:
        os.remove(f.name)