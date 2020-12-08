
__all__ = ( 'stringsSimilar', 'parensClosed', 'convertCharsToLatex' )

from re import compile as re_compile
from difflib import SequenceMatcher

 ## Translation table for escaping Unicode chars using LateX commands.
CHARS_TO_LATEX = {
    'å': r'\r{a}', 'Å': r'\r{A}',  'ø': r'\o',    'Ø': r'\O',
    'æ': r'\ae',   'Æ': r'\AE',    'ò': r'\`{o}', 'Ò': r'\`{O}',   
    'ó': r'\'{o}', 'Ó': r'\'{O}',  'ö': r'\"{o}', 'Ö': r'\"{O}',   
    'à': r'\`{a}', 'À': r'\`{A}',  'á': r'\'{a}', 'Á': r'\'{A}',   
    'ä': r'\"{a}', 'Ä': r'\"{A}',  'ù': r'\`{u}', 'Ù': r'\`{U}',   
    'ú': r'\'{u}', 'Ú': r'\'{U}',  'ü': r'\"{u}', 'Ü': r'\"{U}',   
}

 ## Min similarity ratio between two strings to consider them [almost] identical.
STRING_SIMILARITY_THRESHOLD = 0.99
 ## Used for finding pairs of matching curly braces.
REGEX_CLOSED_PARENS = re_compile( r'\{[^{}]*\}' )
 ## Used to escape unicode chars following the rules in `CHARS_TO_LATEX`.
REGEX_UNICODE_CHARS = re_compile( r'('+'|'.join( CHARS_TO_LATEX.keys() ) + r')')


##########################################################################
#   @brief  Checks if strings are very similar, almost identical.
#   @param  s1  str
#   @param  s2  str
#   @returns    bool    True if similarity between strings is not lower than
#   `STRING_SIMILARITY_THRESHOLD`.
##########################################################################
def stringsSimilar ( s1, s2 ) :
    ratio = SequenceMatcher( None, s1.upper(), s2.upper() ).ratio()
    return ratio >= STRING_SIMILARITY_THRESHOLD


##########################################################################
#   @brief  Checks if each curly bracket have a matching pair inside a string.
#   @param  s  str
#   @returns    bool
##########################################################################
def parensClosed ( s ) :
    n_subs = 1
    while n_subs > 0 :
        s, n_subs = REGEX_CLOSED_PARENS.subn( '', s )
    return "{" not in s

##########################################################################
#   @brief  Escapes all unicode chars in string using LateX commands.
#   @param  s  `str`
#   @returns  str
##########################################################################
def convertCharsToLatex ( s ) :
    return REGEX_UNICODE_CHARS.sub( lambda c: "{"+CHARS_TO_LATEX[c.group()]+"}", s )

##########################################################################
def isEnclosed ( s ) :
    return s[0] == s[-1] == "" \
        or s[0] == "{" and s[-1] == "}"

