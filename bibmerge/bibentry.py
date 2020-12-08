
from re import compile as re_compile
from urllib.parse import urlparse
from bibmerge.bibutils import stringsSimilar

 ## Used in `_convertNewlines`. Matches multiple consecutive newline characters.
REGEX_NEWLINES = re_compile( r'\n{2,}' )

class BibEntry ( dict ) :

    def matchesOther ( self, entry2 ) :
        """Performs checks to compare this bib entry with another one.

        :param entry2: Some other instance of `BibEntry`.
    
        :returns: `True` if entries are considered duplicating each other.
        :rtype: bool
        """

        entry1 = self
    
        entry_type = entry1['_TYPE']
        if entry_type != entry2['_TYPE'] :
            return False
    
         # Publications in books: compare pages, chapter, and, possibly, isbn:
        if entry_type == 'INBOOK' :
             # If both isbns are defined and they are different, return false.
            isbn1 = entry1.get( 'ISBN' )
            isbn2 = entry2.get( 'ISBN' )
            if isbn1 and isbn2 and isbn1 != isbn2 :
                return False
            return entry1.get( 'CHAPTER' ) == entry2.get( 'CHAPTER' ) \
                and entry1.get( 'PAGES' ) == entry2.get( 'PAGES' )
    
        else :
             # If years or titles are different, then the entries are different
            year1 = entry1.get( 'YEAR' )
            year2 = entry2.get( 'YEAR' )
            if year1 and year2 and year1 != year2 \
            or not stringsSimilar( entry1.get( 'TITLE' ), entry2.get( 'TITLE' ) ) :
                return False
    
             # Assume that if both URLs are defined and are the same, then entries
             # are duplicates. TODO: is this correct for all entry types?
            url1 = entry1.get( 'URL' )
            url2 = entry2.get( 'URL' )
            if url1 and url2 :
                url1 = url1.strip()
                parsed = urlparse( url1 )
                if parsed.scheme and parsed.netloc and parsed.path and url1 != url2.strip() :
                    return False
    
             # There can be multiple entries (@MISC, for example) with the same
             # title and year, differing only in the "NOTE" fields.
            note1 = entry1.get( 'NOTE' )
            note2 = entry2.get( 'NOTE' )
            if note1 and note2 and note1 != note2 :
                return False
    
    #         # Topics must match exactly for the entries to be the same.
    #        if entry1.get( 'TOPIC',"" ).upper() != entry2.get( 'TOPIC',"" ).upper():
    #            return False
    
             # ...or they can differ in the following fields:
            if entry_type != "ARTICLE" :
    
                org1 = entry1.get( 'ORGANIZATION' )
                org2 = entry2.get( 'ORGANIZATION' )
                if org1 and org2 and org1 != org2 :
                    return False
    
                addr1 = entry1.get( 'ADDRESS' )
                addr2 = entry2.get( 'ADDRESS' )
                if addr1 and addr2 and addr1 != addr2 :
                    return False
    
                pages1 = entry1.get( 'PAGES' )
                pages2 = entry2.get( 'PAGES' )
                if pages1 and pages2 and pages1 != pages2 :
                    return False
    
        return True


    ##########################################################################
    #   @brief  Converts multiple consecutive newlines into two LaTeX linebreaks.
    ##########################################################################
    def convertNewlines ( self ) :
        for key,val in self.items() :
            self[key] = REGEX_NEWLINES.sub( r"\\\\ \\\\ ", val )

    ##########################################################################
    def toString ( self ) :
        lines = []
        lines.append( "".join( ( "@", self['_TYPE'], "{", self['_ID'], "," ) ) )
        i = 0
        for field in self :
            if field != "_TYPE" and field != "_ID" :
                comma = ""  if i == len( self ) - 3  else ","
                lines.append( "".join( ( "  ", field, " = {", self[field], "}", comma ) ) )
                i += 1
        lines.append( "}" )
        return "\n".join( lines )

