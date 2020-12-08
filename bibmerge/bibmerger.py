"""
/bibmerge/bibmerger.py
~~~~~~~~~~~~~~~~~~~~~~

This file is part of the `bibmerge` package.

URL: https://github.com/vakorol/bibmerge
License: MIT
"""

############################################################################

__author__ = "Vasili Korol (https://github.com/vakorol)"
__license__ = "MIT"
__version__ = "0.1"
__all__ = ( 'BibMerger', )

############################################################################

from re import compile as re_compile
from sys import stdout
from os.path import getmtime

from bibmerge.bibentry import BibEntry
from bibmerge.bibutils import convertCharsToLatex, parensClosed, isEnclosed

############################################################################

 ## Start of a bibtex entry ( "@ARTICLE{blahblah," ).
REGEX_ENTRY_START = re_compile( r'^\s*\@(\w+)\s*\{\s*(\w+)\s*,' )
 ## Definition of an entry field ( "FIELD = {foobar}," ).
REGEX_ENTRY_FIELD = re_compile( r'^\s*(\w+)\s*=\s*(.+?),?\s*$' )
 ## Multiline field value continued on next lines.
REGEX_ENTRY_FIELD_CONTINUED = re_compile( r'^\s*(.*?),?\s*$' )
 ## End of bibtex entry (just a closing curly bracket).
REGEX_ENTRY_END = re_compile( r'^\s*\}\s*$' )

REGEX_ABBR_DEF = re_compile( r'^\s*@string\{\s*(\w+)\s*=\s*("|\{)(.+?)(?:"|\})\s*\}\s*$' )

YEAR_SEPARATOR = """
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Publications in {}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

"""

UNCATEGORIZED_SEPARATOR = """
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

"""

############################################################################
class BibMerger :

    #######################################################################
    def __init__ ( self, bib_files, abbr_files=None ) :
        self.bib_files = bib_files
        self.bib_files.sort( key=getmtime, reverse=True )
        self.abbr_files = abbr_files
        self._merged_yearly = {}
        self._abbreviations = {}

        self._cur_fname = None
        self._cur_entry = None
        self._cur_field = None
        self._cur_field_val =None
        self._cur_separator = None
        self._cur_end_separator = None
        self._cur_entries = None

        self._loadAbbreviations()


    ########################################################################
    def merge ( self ) :
        """Parses the input files and merges the data internally.
        """

        for fname in self.bib_files :

            self._parseBibFile( fname )

            for new_entry in self._cur_entries :

                 # Gather all "misc" entries under one dummy year, so that they
                 # all appear at the very end of the combined bibliograpy:
                if new_entry['_TYPE'] == "misc" :
                    year = "0"
                else :
                    year = new_entry.get( 'YEAR', "0" )

                is_duplicate = False

                merged_db = self._merged_yearly.get( year )
                if merged_db :
                    for entry in merged_db :
                        is_duplicate = entry.matchesOther( new_entry )
                        if is_duplicate :
                            break

                if not is_duplicate :
                    new_entry.convertNewlines()
                    bib_for_year = self._merged_yearly.setdefault( year, [] )
                    bib_for_year.append( new_entry )

        return self

    #######################################################################
    def export ( self, out_file=stdout ) :
        """Export the BibTex entries as text, sorted by years.

        :param out_file: Some file-like object (stream) to write output to. \
        Defaults to `sys.stdout`.
        """
        for year in sorted( self._merged_yearly.keys(), reverse=True ) :
            self._exportEntriesForYear( year, out_file )


    ######################################################################
    def _exportEntriesForYear ( self, year, out_file ) :

        if year != "0" :
            out_file.write( YEAR_SEPARATOR.format( year ) )
        else :
            out_file.write( UNCATEGORIZED_SEPARATOR )

        entries = self._merged_yearly[year]

        for entry in entries :
            out_file.write( entry.toString() )
            out_file.write( "\n\n" )

    ######################################################################
    def _loadAbbreviations ( self ) :
        if not self.abbr_files :
            return
        for fname in self.abbr_files :
            self._parseAbbrFile( fname )

    ######################################################################
    def _parseAbbrFile ( self, fname ) :
        with open( fname ) as f :
            for line in f :
                match = REGEX_ABBR_DEF.match( line )
                if match :
                    key = match.group( 1 )
                    separator = match.group( 2 )
                    val = match.group( 3 )

                    end_separator = "}" if separator == "{"  else separator
                    if val[-1] == end_separator \
                    and ( separator != "{" \
                        or separator == "{" and parensClosed( separator + field_val ) ) :
                            val = convertCharsToLatex( val[:-1] )

                    self._abbreviations[key] = val

    ##########################################################################
    def _parseBibFile ( self, fname ) :
        """Parses a .bib file into a list of entries.

        :param fname: Path to a .bib file to parse.
        :type fname: str

        :returns: A list of :class:`bibmerge.bibentry.BibEntry` objects.
        :rtype: list

        :raises: `SyntaxError` when failed to find the end of a multiline field\
        value or field value not enclosed in curly braces / quotes.

        .. note:: This is a rather dumb parser which does not follow the BibTex\
        format accurately. On the other hand, it's behavior is more \
        straight-forward and predictable compared to other Python .bib parsers.
        """

        self._cur_entries = []
        self._cur_fname = fname

        with open( fname, 'r', 2 ) as f :
            line_num = 0
            try :
                for line in f :
                    line_num += 1
                    self._parseLine( line, line_num )
            except UnicodeError :
                raise UnicodeError(
                    "Bad Unicode char in file '{}' at line {}."
                        .format( fname, line_num )
                )

    ##########################################################################
    def _parseLine ( self, line, line_num ) :

         # If we are currently reading some entry:
        if self._cur_entry :

            if not self._cur_field :

                 # Reading a new field:
                match = REGEX_ENTRY_FIELD.match( line )

                if match :

                    self._cur_field = match.group( 1 ).upper()
                    val = match.group( 2 )

                    if isEnclosed( val ) and parensClosed( val ) :
                        self._cur_entry[self._cur_field] = convertCharsToLatex(
                            val[1:-1].strip()
                        )
                        self._cur_field = None
                    elif val[0] in '"{' :
                        self._cur_separator = val[0]
                        self._cur_end_separator = '}' \
                            if self._cur_separator == '{' \
                            else '"'
                        self._cur_field_val = val[1:]
                    else :
                        self._cur_field_val = self._abbreviations.get( val )
                        if self._cur_field_val is None :
                            raise SyntaxError(
                                "Field value must either be a valid "
                                "abbreviation, or be enclosed in curly braces "
                                "or quotes in file '{}' at line {}."
                                    .format( self._cur_fname, line_num )
                            )
                        self._cur_entry[self._cur_field] = self._cur_field_val
                        self._cur_field = None

                 # Entry ends with a closing curly bracket:
                elif REGEX_ENTRY_END.match( line ) :
                    self._cur_entries.append( self._cur_entry )
                    self._cur_entry = None

            else :
                 # Continue reading the field value:
                match = REGEX_ENTRY_FIELD_CONTINUED.match( line )
                 # TODO: it seems like this regex will always match.
                if not match :
                    raise SyntaxError(
                        "Bad syntax in file '{}' at line {}."
                            .format( self._cur_fname, line_num )
                    )
                self._cur_field_val += match.group( 1 )
                if self._entryEnded() :
                    self._cur_entry[self._cur_field] = convertCharsToLatex(
                        self._cur_field_val[:-1]
                    )
                    self._cur_field = None
                 # The string is still unfinished => add a LaTeX line break:
                else :
                    self._cur_field_val += "\n"

         # Starting new entry:
        else :
            matches = REGEX_ENTRY_START.match( line )
            if matches :
                entry_type = matches.group( 1 ).upper()
                entry_id = matches.group( 2 )
                self._cur_entry = BibEntry( {
                    "_ID": entry_id,
                    "_TYPE": entry_type
                } )
                self._cur_field = None


    ##########################################################################
    def _entryEnded ( self ) :
        return self._cur_field_val[-1] == self._cur_end_separator \
            and (
                self._cur_separator != "{"
                or (
                    self._cur_separator == "{"
                    and parensClosed( self._cur_separator + self._cur_field_val)
                )
            )

