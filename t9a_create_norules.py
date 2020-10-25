#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import scribus
import os
import re
import datetime
import shutil

def get_rules_pages():
    rules_start = scribus.getAllText("rules_start")
    rules_end = scribus.getAllText("rules_end")
    return (int(rules_start),int(rules_end))

def main(argv):

    page_range = get_rules_pages()

    scribus.deselectAll()
   
    # Create backup of file first
    now = datetime.datetime.now()
    timestamp = now.strftime('%Y-%m-%dT%H-%M-%S')
    filename = scribus.getDocName()
    backup_filename = os.path.splitext(filename)[0]+'_backup_'+timestamp+'.sla'
    shutil.copy(filename,backup_filename) # don't use scribus built-in savceDocAs(), otherwise it will switch focus to the new file, which we don't want.

    # set version string - currently handled by export script

    # unlock and delete background, rules toc headers
    frames = ["toc_header_background","toc_header_rules","TOC2"]
    for frame in frames:
         if scribus.isLocked(frame):
            scribus.lockObject(frame)
            scribus.deleteObject(frame)

    # delete rules hyperlinks
    scribus.deleteObject("rules_links")

    # set Epilogue hyperlink to correct page (same as rules_start)
    scribus.setLinkAnnotation(page_range[0],0,0,"bh_epilogue")
    
    # delete pages
    pages = []
    scribus.setRedraw(False)
    for i in range(page_range[1],page_range[0]-1,-1): # need to start from last page as page count changes as pages are deleted
        scribus.deletePage(i)
        pages.append(i)
    scribus.docChanged(True)
    scribus.setRedraw(True)
    
    # save _nopoints version of file
    new_filename = os.path.splitext(filename)[0]+'_nopoints.sla'
    scribus.saveDocAs(new_filename)
    # shutil.copy(filename,backup_filename)


    # # scribus.gotoPage(42)
    # # items = scribus.getPageItems()
    # for item in items:
    #     scribus.deselectAll()
    #     if item[1] == 2:
    #         atts = scribus.getPropertyNames(item[0])
    #         scribus.selectObject(item[0])
    #         file = scribus.getImageFile()
    #         if pdf_re.match(file):
    #             new_file = os.path.splitext(file)[0]+'_nopoints.pdf'
    #             # scribus.loadImage(new_file)
    #             # atts = scribus.getObjectAttributes()
    #             # ids.append(new_file)
    # # scribus.messageBox("List of Files", str(ids))
    # output = 'Rules start on page %i  and end on page %i' % (page_range[0], page_range[1])
    # scribus.messageBox("Output",'Pages deleted: %s' % (str(pages)))

if __name__ == '__main__':
    main(sys.argv)