#!python3
"""
/bibmerge.py
~~~~~~~~~~~~

Merges BibTeX (.bib) files into a single list of bibliography entries, removing
duplicates. The list is output to stdout.\

Prior to parsing, files are sorted by modification time. Therefore, bib entries\
from newer files will appear at the top of the resulting merged list. \

The script also escapes common non-latin characters and newlines using LaTeX \
native commands.

Usage:
    bibmerge.py [-h] [--abbr abbr_file] [bib_file [bib_file ...]]

positional arguments:
    bib_file        Input .bib files to merge. If not specified, all .bib \
                    files in the current directory will be used.

optional arguments:
    -h, --help        show this help message and exit
    --abbr abbr_file  BibText file(s) containing abbreviations to expand in the\
                      output. Multiple '--abbr' arguments may be specified.
    
URL:
    https://github.com/vakorol/bibmerge

License:
    MIT
"""

############################################################################

__author__ = "Vasili Korol (https://github.com/vakorol)"
__license__ = "MIT"
__version__ = "0.1"

############################################################################

from glob import glob
from argparse import ArgumentParser
from bibmerge.bibmerger import BibMerger

############################################################################

arg_parser = ArgumentParser(
    description="Merges multiple BibTex files into one."
)

arg_parser.add_argument(
    'bib_files',
    metavar="bib_file",
    type=str,
    nargs='*',
    help="Input .bib files to merge. If not specified, all .bib files in the " \
        "current directory will be used."
)

arg_parser.add_argument(
    '--abbr',
    action="append",
    metavar="abbr_file",
    type=str,
    help="BibText file(s) containing abbreviations to expand in the output. " \
        "Multiple '--abbr' arguments may be specified."
)

args = arg_parser.parse_args()

bib_files = args.bib_files or glob( '*.bib' )
abbr_files = args.abbr

############################################################################

merger = BibMerger( bib_files=bib_files, abbr_files=abbr_files )
merger.merge()
merger.export()

