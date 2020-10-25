import os
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("files", type=argparse.FileType('r'), nargs='+', help="file to be renamed")
parser.add_argument('--version','-v', help="rules version")
args = parser.parse_args()

if args.version:
    version = args.version
else:
    version = "2020"

files = args.file

target_filename = "t9a-fb_fab_print_wotdg_2-2_en.pdf"

t9a_pattern = r't9a-fb_lab_(\w+)_(\w+)_v1_(\w+)_(\w+)\.pdf'
t9a_re = re.compile(t9a_pattern)

for f in files:
    filename = os.path.basename(f)#.replace("_v1","")
    result = t9a_re.match(filename.lower())
    if result:
        # print (f)
        army = result.group(1)
        lang = result.group(2)
        format = result.group(3)
        if format == "norules":
            format = "background"
        quality = result.group(4)
        if quality == "high":
            quality = "print"
        if quality == "low":
            quality = "online"
        # print(f"{result.group(1)} {result.group(2)} {result.group(3)} {result.group(4)}")
        new_filename = f"t9a-fb_lab_{quality}_{army}_{format}_{version}_{lang}.pdf"
        new_filename = new_filename.replace("_wdg_", "_wotdg_")
        print(f'{f} => {new_filename}')
        # os.rename(f,new_filename)