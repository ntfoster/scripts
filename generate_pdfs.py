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
    if output==True:
        subprocess.call(cmd, shell=True)
    else:
        subprocess.call(cmd, shell=True,stdout=subprocess.DEVNULL)

def generate_pdf(input): # call Scribus to generate PDFs


    # TODO: switch to quit
    
    output_args = ''
    if "print" in args.quality:
        output_args += 'print '
    if "high" or "low" in args.quality:
        output_args += 'screen ' # TODO: why is screen being passed to scribus when only print is passed here?

    if args.formats:
        format_args = ' '.join(args.formats)
    else:
        format_args = "full"

    run_command(f'scribus "{input}" --console -py ./t9a_export_pdfs.py --quit --format {format_args} --output {output_args}',False)

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
        # no need for bookmarks
        pass

    # if "norules" in args.formats:
    #     cmd = f'python ./parse_toc.py --norules "{input}"'
    #     now = datetime.now()
    #     time = now.strftime("%H:%M:%S")
    #     print(f"{time}: Running: {cmd}")
    #     subprocess.call(cmd, shell=True)

    # if "full" in args.formats:
    #     cmd = f'python ./parse_toc.py "{input}"'
    #     now = datetime.now()
    #     time = now.strftime("%H:%M:%S")
    #     print(f"{time}: Running: {cmd}")
    #     subprocess.call(cmd, shell=True)

    # # create pdfmarks file from CSV
    # csvfile = Path(input).stem+"_toc.csv"
    # cmd = f'python ./create_pdftk_marks.py "{csvfile}"'
    # now = datetime.now()
    # time = now.strftime("%H:%M:%S")
    # print(f"{time}: Running: {cmd}")
    # subprocess.call(cmd, shell=True)

    # # call pdftk to add pdfmarks
    # # original_pdf = Path(input).stem+"_high.pdf"
    # original_pdf = os.path.splitext(input)[0]+'_full_high.pdf'
    # pdfmarks = Path(input).stem+"_toc.pdftk_marks"
    # cmd = f'python ./add_bookmarks.py "{original_pdf}" "{pdfmarks}"'
    # now = datetime.now()
    # time = now.strftime("%H:%M:%S")
    # print(f"{time}: Running: {cmd}")
    # subprocess.call(cmd, shell=True,stdout=subprocess.DEVNULL)

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

def move_pdfs(input, output_dir):
    if args.noprocess:
        args.quality = ["screen"]
    for f in args.formats:
        for q in args.quality:
            filename = (os.path.splitext(input)[0])+f'_{f}_{q}.pdf'
            new_filename = output_dir + '\\'+ os.path.basename(filename)
            shutil.move(filename, new_filename)
    # os.remove(input)

    # output_file = os.path.splitext(input)[0]+'_high.pdf'
    # if os.path.isfile(output_file):
    #     shutil.copy(output_file, output_dir)
    # output_file = os.path.splitext(input)[0]+'_low.pdf'
    # if os.path.isfile(output_file):
    #     shutil.copy(output_file, output_dir)
    # output_file = os.path.splitext(input)[0]+'_print.pdf'
    # if os.path.isfile(output_file):
    #     shutil.copy(output_file, output_dir)

def create_nopoints(input):
    cmd = f'python ./replace_pdf.py "{input}" -o' # create a '_nopoints.sla' file
    now = datetime.now()
    time = now.strftime("%H:%M:%S")
    print(f"{time}: Running: {cmd}")
    subprocess.call(cmd, shell=True)

for f in args.file:
    # job_files = []
    # filename = f.name
    job = f.name
    if not args.noexport:
        generate_pdf(job) # TODO: parallelise; had an error during pdf creation
    if not args.noprocess:
        process_pdf(job)
    if args.dest:
        move_pdfs(f.name,args.dest)

    # if "full" in args.formats:
    #     job_file = os.path.splitext(filename)[0] + '.sla'
    #     job_files.append(job_file)
    # if "nopoints" in args.formats:
    #     create_nopoints(filename)
    #     job_file = os.path.splitext(filename)[0] + '_nopoints.sla'
    #     job_files.append(job_file)
    # # if "norules" in args.formats: # norules not yet implemented
    # #     job_file = os.path.splitext(filename)[0] + '_norules.sla'
    # #     job_files.append(job_file)

    # for job in job_files:
    #     if not args.noexport:
    #         generate_pdf(job) # TODO: parallelise; had an error during pdf creation
    #     if not args.noprocess:
    #         process_pdf(job)
    #     if args.dest:
    #         move_pdfs(job,output_dir)

# All done
now = datetime.now()
time = now.strftime("%H:%M:%S")
print(f"{time}: all done!")