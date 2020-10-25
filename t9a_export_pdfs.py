#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

try:
    # Please do not use 'from scribus import *' . If you must use a 'from import',
    # Do so _after_ the 'import scribus' and only import the names you need, such
    # as commonly used constants.
    import scribus
except ImportError as err:
    print("This Python script is written for the Scribus scripting interface.")
    print("It can only be run from within Scribus.")
    sys.exit(1)

#########################
# YOUR IMPORTS GO HERE  #
#########################

import sys
import os
import argparse
import re
import datetime
import shutil

OUTPUT_TYPES = ["high","low","print"]
FORMAT_TYPES = ["full","nopoints","norules"]

# globals
quit = False
num_files = 0
progress_step = 0
interactive = True
no_export = False


def get_rules_pages():
    rules_start = scribus.getAllText("rules_start")
    rules_end = scribus.getAllText("rules_end")
    return (int(rules_start),int(rules_end))

def create_norules():
    page_range = get_rules_pages()

    scribus.deselectAll()
   
    # Create backup of file first
    now = datetime.datetime.now()
    timestamp = now.strftime('%Y-%m-%dT%H-%M-%S')
    filename = scribus.getDocName()
    backup_filename = os.path.splitext(filename)[0]+'_backup_'+timestamp+'.sla'
    shutil.copy(filename,backup_filename) # don't use scribus built-in savceDocAs(), otherwise it will switch focus to the new file, which we don't want.

    # set version string - currently handled by export script
    version = scribus.getAllText("version_name")
    version = version.replace('Rules and Points version 2020', 'Background Book')
    scribus.setText(version,"version_name")
    scribus.setTextAlignment(scribus.ALIGN_CENTERED, "version_name")

    # unlock and delete background, rules toc headers
    frames = ["toc_header_background","toc_header_rules","TOC2"]
    for frame in frames:
         if scribus.isLocked(frame):
            scribus.lockObject(frame)
            scribus.deleteObject(frame)

    # delete rules hyperlinks
    scribus.deleteObject("rules_links")

    # check for alternate contents master page (e.g. smaller background)
    master = scribus.getMasterPage(7) # 7 should (hopefully) always be contents page
    if master.startswith('T -'):
        masters = scribus.masterPageNames()
        new_master = master
        for m in masters:
            print(m)
            if m.startswith('T0'):
                new_master = m
        scribus.applyMasterPage(new_master,7)    
    
    # delete pages
    pages = []
    scribus.statusMessage("Deleting Pages")
    scribus.setRedraw(False)
    for i in range(page_range[1],page_range[0]-1,-1): # need to start from last page as page count changes as pages are deleted
        scribus.deletePage(i)
        pages.append(i)
    scribus.docChanged(True)
    scribus.setRedraw(True)
    
    # set Epilogue hyperlink to correct page (same as rules_start)
    num_pages = page_range[1]-page_range[0] + 1
    original_epilogue = int(scribus.getAllText("epilogue_page"))
    new_epilogue = original_epilogue - num_pages
    scribus.setText(str(new_epilogue),"epilogue_page")
    scribus.setLinkAnnotation(new_epilogue,0,0,"bh_epilogue")
    
    # save _norules version of file
    
    new_filename = os.path.splitext(filename)[0].replace('_nopoints', '')+'_norules.sla'
    scribus.saveDocAs(new_filename)
    # shutil.copy(filename,backup_filename)

def export_pdf(filename,output):
    global progress_step
    global no_export
    if no_export:
        return
    if output == "screen":
        # screen 300 dpi settings
        # scribus.readPDFOptions("screen_pdfoptions.xml")
        pdf = scribus.PDFfile()
        output_file = os.path.splitext(filename)[0]+'_screen.pdf'
        pdf.file = output_file
        # pdf.quality = 0 # High
        # pdf.fontEmbedding = 0
        # pdf.version = 14
        # pdf.embedPDF = True
        # pdf.downsample = 300
        # pdf.resolution = 300
        # pdf.compress = True
        # pdf.compressmtd = 0 # Automatic compression
        # pdf.outdst = 0 # screen
        # pdf.displayBookmarks = True
        # pdf.useDocBleeds = False
        # pdf.cropMarks = False
        scribus.statusMessage("Exporting %i of %i: %s" % (progress_step, num_files, output_file))
        pdf.save()

    # if output == "print":
    #     # print 300 dpi
    #     pdf3 = scribus.PDFfile()
    #     output_file = os.path.splitext(filename)[0]+'_print.pdf'
    #     pdf3.file = output_file
    #     pdf3.quality = 1 # High
    #     pdf3.fontEmbedding = 0
    #     pdf3.version = 14
    #     pdf3.embedPDF = True
    #     pdf3.downsample = 300
    #     pdf3.compress = True
    #     pdf3.compressmtd = 0 # Automatic compression
    #     pdf3.outdst = 1 # print
    #     pdf3.useDocBleeds = True
    #     pdf3.cropMarks = True
    #     scribus.statusMessage("Exporting %i of %i: %s" % (progress_step, num_files, output_file))
    #     pdf3.save()

def replace_pdf(): # replaces linked rules pdf with '_nopoints' version
    pdf_pattern = r".+\.(pdf)"
    pdf_re = re.compile(pdf_pattern)
    page_range = get_rules_pages()
    pages = []
    
    for i in range(page_range[0],page_range[1]+1):
        scribus.gotoPage(i)
        items = scribus.getPageItems()
        for item in items:
            scribus.deselectAll()
            if item[1] == 2: # if an image frame
                file = scribus.getImageFile(item[0])
                if pdf_re.match(file):
                    new_file = os.path.splitext(file)[0]+'_nopoints.pdf'
                    if os.path.isfile(new_file):
                        scribus.loadImage(new_file,item[0])
                        pages.append(i)

def verify_output(output):
    if output in OUTPUT_TYPES:
        return output
    else:
        raise argparse.ArgumentTypeError("%s is not a valid output. Valid outputs are: %s" % (output, str(OUTPUT_TYPES)))


def verify_format(format):
    if format in FORMAT_TYPES:
        return format
    else:
        raise argparse.ArgumentTypeError("%s is not a valid format. Valid formats are: %s" % (format, str(FORMAT_TYPES))) 

def main(argv):
    global progress_step
    global num_files
    global interactive
    global no_export

    """This is a documentation string. Write a description of what your code
    does here. You should generally put documentation strings ("docstrings")
    on all your Python functions."""
    if len(argv)==1: # if called from within Scribus or with no arguments
        new_args = scribus.valueDialog('Set Arguments', 'Set Arguments:\nOptions for --output: screen, print\nOptions for --format: full, nopoints, norules', '--output screen --formats full  --noexport')
        if new_args == '':
            scribus.messageBox("Script Cancelled","Script was cancelled or no arguments were provided")
            return
        else:
            arg_list = new_args.split(' ')
            # scribus.messageBox("Arguments",str(argv))
            # return
    else:
        arg_list = argv[1:]
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', nargs='+', help='Which output types do you want? Available: "screen" (RGB) and "print" (CMYK). Defaults to screen only.', default="screen")
    parser.add_argument('--formats', '-f', nargs='+', help='Options: "full", "nopoints", and "norules". Default is "full".', default="full")
    parser.add_argument('--quit', help='Quit Scribus after export (e.g. when called as part of external script)', action="store_true")
    parser.add_argument('--noexport', help="Don't export PDFs, just make the changes to the file and save", action="store_true")

    try:
        args = parser.parse_args(arg_list)
    except argparse.ArgumentTypeError as e:
        raise e

    # filepath = getDocName()
    # filename = os.path.basename(filepath)
    # output_file =  os.path.splitext(filepath)[0]+'.pdf'
    if args.noexport:
        no_export = True
    if args.quit:
        interactive = False

    filename = scribus.getDocName()
    
    scribus.setLayerVisible("Rules", True)
    scribus.setLayerBlendmode("Rules", 3) # Multiply for Rules Layer

    # TODO: Count steps and set progress bar accordingly
    num_files = len(args.formats)*len(args.output)
    scribus.progressTotal(num_files)
    if "full" in args.formats:
        output_file = os.path.splitext(filename)[0]+'_full'
        for o in args.output:
            progress_step += 1
            export_pdf(output_file,o)
            scribus.progressSet(progress_step)
    if "nopoints" in args.formats:
        replace_pdf()
        version = scribus.getAllText("version_name")
        version = version.replace('Rules and Points version 2020', 'Rules Only version 2020')
        scribus.setText(version,"version_name")
        scribus.setTextAlignment(scribus.ALIGN_CENTERED, "version_name")
        output_file = os.path.splitext(filename)[0]+'_nopoints'
        for o in args.output:
            progress_step += 1
            export_pdf(output_file,o)
            scribus.progressSet(progress_step)
        new_filename = output_file+'.sla'
       # save copy of the nopoints .sla
        if "norules" in args.formats:
            shutil.copy(filename,new_filename) # don't want to saveAsDoc while we've got more to do
        else:
            scribus.saveDocAs(new_filename) # save copy of the _nopoints.sla

    if "norules" in args.formats:
        # remove rules
        scribus.statusMessage("Creating norules version")
        create_norules()
        output_file = os.path.splitext(filename)[0]+'_norules'
        for o in args.output:
            progress_step += 1
            export_pdf(output_file,o)
            scribus.progressSet(progress_step)
 


    # Unused settings for "low" quality screen PDF. Moved responsibility for low quality PDF to external script.
    # screen 96 dpi settings
    # pdf2 = scribus.PDFfile()
    # output_file = os.path.splitext(filename)[0]+'_low.pdf'
    # pdf2.file = output_file
    # pdf2.quality = 1 # High
    # pdf2.fontEmbedding = 0
    # pdf2.version = 14
    # pdf2.embedPDF = True
    # pdf2.downsample = 96
    # pdf2.compress = True
    # pdf2.compressmtd = 0 # Automatic
    # pdf2.outdst = 0 # screen
    # pdf2.displayBookmarks = True
    # pdf3.useDocBleeds = True
    # pdf3.cropMarks = True
    # scribus.statusMessage("Exporting %s" % output_file)
    # pdf2.save()


def main_wrapper(argv):
    global interactive
    """The main_wrapper() function disables redrawing, sets a sensible generic
    status bar message, and optionally sets up the progress bar. It then runs
    the main() function. Once everything finishes it cleans up after the main()
    function, making sure everything is sane before the script terminates."""
    try:
        scribus.setRedraw(False)
        scribus.statusMessage("Running script...")
        scribus.progressReset()
        main(argv)
    finally:
        # Exit neatly even if the script terminated with an exception,
        # so we leave the progress bar and status bar blank and make sure
        # drawing is enabled.
        if scribus.haveDoc():
            scribus.setRedraw(True)
        scribus.statusMessage("")
        scribus.progressReset()
        if not interactive:
            scribus.fileQuit()

# This code detects if the script is being run as a script, or imported as a module.
# It only runs main() if being run as a script. This permits you to import your script
# and control it manually for debugging.
if __name__ == '__main__':
    if scribus.haveDoc():
        main_wrapper(sys.argv)
    else:
        scribus.messageBox("No file open","You need to have a suitable file open to use this script")
# scribus.fileQuit() # TODO: handle optional switch to quit or not

