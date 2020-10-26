import os
from pathlib import Path
import subprocess
import argparse
import time
from datetime import datetime
import shutil

### Constants ####
HIGH_DPI = 300
LOW_DPI = 100
##################

def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")

parser = argparse.ArgumentParser()
# parser.add_argument("input", help=".sla files")
parser.add_argument('file', type=argparse.FileType('r'), nargs='+')
parser.add_argument('--noexport', help='Do not export PDFs from Scribus first, use existing files.', action="store_true", default=False)
parser.add_argument('--noprocess', help='Do not process PDFs after exporting', action="store_true", default=False)
parser.add_argument('--formats', '-f', nargs='+', help='Options: "full", "nopoints", and "norules". Default is "full".', default="full")
parser.add_argument('--quality', '-q', nargs='+', help='Which qualities of file do you want? Available: "high", "low", and "print". Defaults to "high" and "low"', default="high low")
parser.add_argument('--dest','-d', help='destination directory',type=dir_path)
args = parser.parse_args()

def run_command(cmd,output):

    now = datetime.now()
    time = now.strftime("%H:%M:%S")
    print(f"{time}: Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result

def generate_pdfs(input): # call Scribus to generate PDFs
    format_args = ' '.join(args.formats)
    quality_args = ' '.join(args.quality)
    run_command(f'scribus "{input}" --console -py ./t9a_export_pdfs.py --quit --format {format_args} --quality {quality_args}',False)

def process_pdf(input): # parse TOC and create CSV

    # TODO: save intermediate files in .sla's directory, not the script's directory, and delete if successfull.
    
    if "high" or "low" in args.quality:
        if "full" or "nopoints" in args.formats:
            # parse_toc
            run_command(f'python ./parse_toc.py "{input}"',False)
            # gen pdftk_marks
            csvfile = Path(input).stem+"_toc.csv"
            run_command(f'python ./create_pdftk_marks.py "{csvfile}"',False)

        if "norules" in args.formats:
            # parse_toc --norules
            file = os.path.splitext(input)[0]+'_norules.sla'
            run_command(f'python ./parse_toc.py --norules "{file}"',False)
            # gen pdftk_marks
            csvfile = Path(input).stem+"_norules_toc.csv"
            run_command(f'python ./create_pdftk_marks.py "{csvfile}"',False)

        for f in args.formats:
            # add bookmarks
            if f == "norules":
                pdfmarks = Path(input).stem+"_norules_toc_pdftk.txt"
            else:
                pdfmarks = Path(input).stem+"_toc_pdftk.txt"
            if "high" in args.quality:
                original_pdf = os.path.splitext(input)[0]+'_'+f+'_high.pdf'
                run_command(f'python ./add_bookmarks.py "{original_pdf}" "{pdfmarks}"',False)
            if "low" in args.quality:
                original_pdf = os.path.splitext(input)[0]+'_'+f+'_low.pdf'
                run_command(f'python ./add_bookmarks.py "{original_pdf}" "{pdfmarks}"',False)


    if "print" in args.quality:
        # no need for bookmarks in print version
        pass

    # rename and move files
    files = []
    for f in args.formats:
        for q in args.quality:
            new_filename = os.path.splitext(input)[0]+f'_{f}_{q}.pdf'
            files.append(new_filename)
    file_list = '"{0}"'.format('" "'.join(files))
    result = run_command(f"python ./rename_files.py --keep {file_list}",True)
    return result
    # resample PDFs (even "high", as Scribus PDF file sizes are quite large)
    # for f in args.formats:
    #     original_pdf = os.path.splitext(input)[0]+'_'+f+'_screen_bookmarked.pdf'
    #     if "high" in args.quality:
    #         new_dpi = HIGH_DPI
    #         new_pdf = os.path.splitext(input)[0]+'_'+f+'_high.pdf'
    #         # run_command(f'gswin64c -dBATCH -dNOPAUSE -dDownsampleColorImages=true -dDownsampleGrayImages=true -dDownsampleMonoImages=true -dColorImageResolution={new_dpi} -dGrayImageResolution={new_dpi} -dMonoImageResolution={new_dpi} -dColorImageDownsampleThreshold="1.0" -dGrayImageDownsampleThreshold="1.0" -dMonoImageDownsampleThreshold="1.0" -sDEVICE=pdfwrite -o "{new_pdf}" "{original_pdf}"',False)
    #         shutil.copy(original_pdf,new_pdf)
    #     if "low" in args.quality:
    #         new_dpi = LOW_DPI
    #         new_pdf = os.path.splitext(input)[0]+'_'+f+'.pdf'
    #         # run_command(f'gswin64c -dBATCH -dNOPAUSE -dDownsampleColorImages=true -dDownsampleGrayImages=true -dDownsampleMonoImages=true -dColorImageResolution={new_dpi} -dGrayImageResolution={new_dpi} -dMonoImageResolution={new_dpi} -dColorImageDownsampleThreshold="1.0" -dGrayImageDownsampleThreshold="1.0" -dMonoImageDownsampleThreshold="1.0" -sDEVICE=pdfwrite -o "{new_pdf}" "{original_pdf}"',False)
    #         shutil.copy(original_pdf,new_pdf)
    #     os.remove(original_pdf) # remove _bookmarked.pdf file

def move_pdfs(files, output_dir):
    # filename = (os.path.splitext(input)[0])+f'_{f}_{q}.pdf'
    # new_filename = output_dir + '\\'+ os.path.basename(filename)
    # shutil.move(filename, new_filename)
    for f in files:
        shutil.copy(f,output_dir)

def create_nopoints(input):
    cmd = f'python ./replace_pdf.py "{input}" -o' # create a '_nopoints.sla' file
    run_command(cmd,False)

for f in args.file:
    job = f.name
    if not args.noexport:
        generate_pdfs(job) # TODO: maybe parallelise
    if not args.noprocess:
        new_files = process_pdf(job).stdout.splitlines()
        print("Files created:")
        print(new_files)
        if args.dest:
            move_pdfs(new_files,args.dest)

# All done
now = datetime.now()
time = now.strftime("%H:%M:%S")
print(f"{time}: all done!")