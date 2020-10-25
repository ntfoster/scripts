#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import scribus
import os
import re

def main(argv):
    scribus.messageBox("Arguments", str(argv))

if __name__ == '__main__':
    main(sys.argv)