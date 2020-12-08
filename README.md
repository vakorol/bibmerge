bibmerge
========

Merges BibTeX (.bib) files into a single list of bibliography entries, removing
duplicates. The list is output to stdout.

Prior to parsing, files are sorted by modification time. Therefore, bib entries
from newer files will appear at the top of the resulting merged list.

The script also escapes common non-latin characters and newlines using LaTeX
native commands.

Usage
-----
    bibmerge.py [-h] [--abbr abbr_file] [bib_file [bib_file ...]]

positional arguments:
    bib_file        Input .bib files to merge. If not specified, all .bib
                    files in the current directory will be used.

optional arguments:
    -h, --help        show this help message and exit
    --abbr abbr_file  BibText file(s) containing abbreviations to expand in the\
                      output. Multiple '--abbr' arguments may be specified.
    
URL
---
https://github.com/vakorol/bibmerge

License
-------
MIT
