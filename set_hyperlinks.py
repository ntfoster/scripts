#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

try:
    # Please do not use 'from scribus import *' . If you must use a 'from import',
    # Do so _after_ the 'import scribus' and only import the names you need, such
    # as commonly used constants.
    import scribus
except ImportError,err:
    print "This Python script is written for the Scribus scripting interface."
    print "It can only be run from within Scribus."
    sys.exit(1)

#########################
# YOUR IMPORTS GO HERE  #
#########################

from operator import itemgetter

def main(argv):
    """This is a documentation string. Write a description of what your code
    does here. You should generally put documentation strings ("docstrings")
    on all your Python functions."""
    #########################
    #  YOUR CODE GOES HERE  #
    #########################
    scribus.gotoPage(7) # contents page
    background_pos = scribus.getPosition("TOC")
    rules_pos = scribus.getPosition("TOC2")
    rules_size = scribus.getSize("TOC2") # width,height
    rules_br = ( rules_pos[0]+rules_size[0], rules_pos[1]+rules_size[1] ) # bottom right corner of TOC2 frame
    items = scribus.getPageItems()
    background_links = []
    rules_links = []
    for item in items:
        item_pos = scribus.getPosition(item[0])

        if item_pos[1] > background_pos[1]-1 and item_pos[1] < rules_pos[1]: # within background TOC
            if item[1] == 4: # text frame
                if scribus.getAllText(item[0]) == '': # hyperlinks don't have any text
                    background_links.append( (item[0], item_pos[0], item_pos[1]) )

        elif item_pos[1] > rules_pos[1]-1 and item_pos[1] < rules_br[1]: # within rules TOC
            if item[1] == 4: # text frame
                if scribus.getAllText(item[0]) == '': # hyperlinks don't have any text
                    rules_links.append( (item[0], item_pos[0], item_pos[1]) )

    background_links = sorted(background_links,key=itemgetter(1,2)) # sort into order of x then y coordinates (i.e. left column then right column)
    rules_links = sorted(rules_links,key=itemgetter(1,2))

    # rename hyperlinks
    i = 1
    for link in background_links:
        new_name = 'bh%i' % i
        scribus.setProperty(link[0],"itemName",new_name)
        i += 1
    epilogue_link = 'bh%i' % (len(background_links))
    scribus.setProperty(epilogue_link,"itemName","bh_epilogue")
    x = 1
    for link in rules_links:
        new_name = 'rh%i' % x
        scribus.setProperty(link[0],"itemName",new_name)
        x += 1

def main_wrapper(argv):
    """The main_wrapper() function disables redrawing, sets a sensible generic
    status bar message, and optionally sets up the progress bar. It then runs
    the main() function. Once everything finishes it cleans up after the main()
    function, making sure everything is sane before the script terminates."""
    try:
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

# This code detects if the script is being run as a script, or imported as a module.
# It only runs main() if being run as a script. This permits you to import your script
# and control it manually for debugging.
if __name__ == '__main__':
    main_wrapper(sys.argv)
