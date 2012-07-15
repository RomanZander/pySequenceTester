# -*- coding: utf-8 -*- 
'''
@summary: Sequence integrity tester, console version
@since: 2012.07.12
@version: 0.1.1 
@author: Roman Zander
@see:  https://github.com/RomanZander/pySequenceTester
'''
# ---------------------------------------------------------------------------------------------
# TODO
# ---------------------------------------------------------------------------------------------
"""
    sequences and gaps recognition
    formatted output
    -help argument

"""
# ---------------------------------------------------------------------------------------------
# CHANGELOG
# ---------------------------------------------------------------------------------------------
"""
+0.1.0 - 2012.07.12
    arguments reading (none = current dir, path = dir, [path/]wildcard = [dir/]files),
    getting raw file list,
    dummy functions and SystemExits
+0.1.1 - 2012.07.14
    path cleanup from file list,
    regexp pattern cleanup from file list
"""

import os
import sys
import re
from glob import glob

pst_pathToScan = ''
pst_wildcardToScan = ''
pst_fileList = []
pst_collectedSequences = []
pst_sequenceList = []

# set and compile naming convention regexp pattern
pst_namingConventionPattern = '^(.*\D)?(\d+)(\.[^\.]+)$'
pst_compiledPattern = re.compile( pst_namingConventionPattern, re.I ) 

def pstReadArgv():
    global pst_pathToScan, pst_wildcardToScan
    # if arguments passed
    if len( sys.argv ) > 1:
        arg = sys.argv[1]
        # argument is a real directory
        if type( arg ) == str and os.path.isdir( arg ):
            pst_pathToScan = arg
            pst_wildcardToScan = '*' 
        # interpret arg as wildcard
        elif type( arg ) == str:
            pst_wildcardToScan = arg
        # WTF :)
        else:
            raise TypeError, u'Unsupported format for path argument'
    # scan current directory if no arguments
    else:
        pst_wildcardToScan = '.'
        pst_wildcardToScan = '*'

def pstGetRawFileList():
    global pst_fileList
    pst_fileList = sorted( glob( os.path.join( pst_pathToScan, pst_wildcardToScan )))
    

def pstCleanUpFileList():
    global pst_fileList
    # extract file basename
    pst_fileList = map(os.path.basename, pst_fileList) 
    # filter for name convention by regexp pattern
    pst_fileList = filter( pst_compiledPattern.match, pst_fileList )

def pstBuildSequences():
    global pst_fileList, pst_collectedSequences
    # build splitted file list (splitted by extention, filename prefix and file number)
    splittedList = [] 
    for fileName in pst_fileList:
        filePrefix = pst_compiledPattern.match( fileName ).group( 1 )
        fileIndex = pst_compiledPattern.match( fileName ).group( 2 )
        fileNumber = int( fileIndex, 10 )
        fileExt = pst_compiledPattern.match(fileName).group(3)
        splittedList.append( [fileExt, filePrefix, fileNumber, fileIndex] )
    # sort splitted file list
    splittedList.sort()
    # recollect by extention
    currentSequence = []
    lastToCompare = None
    for splittedElement in splittedList:
        # first iteration
        if lastToCompare == None:
            currentSequence.append(splittedElement)
            # remember extention and prefix
            lastToCompare = [ splittedElement[0], splittedElement[1] ]
        # same extention and prefix
        elif lastToCompare == [ splittedElement[0], splittedElement[1] ]:
            currentSequence.append(splittedElement)
        # extention or prefix changed
        else:
            pst_collectedSequences.append(currentSequence)
            lastToCompare = [ splittedElement[0], splittedElement[1] ]
            currentSequence = []
            currentSequence.append(splittedElement)
    # close (last loop) collection
    pst_collectedSequences.append(currentSequence)        
    # single elements removal
    pst_collectedSequences = [item for item in pst_collectedSequences if len(item) > 1 ]

def pstOutputSequences():
    global pst_collectedSequences
    for item in pst_collectedSequences:
        # ...
        pass
    

if __name__ == '__main__':
    pstReadArgv()
    pstGetRawFileList()
    if len( pst_fileList ) == 0: # nothing in the directory
        raise SystemExit , u"\n No files were found for this path or wildcard"
    
    pstCleanUpFileList()
    if len( pst_fileList ) == 0: # nothing sequence-like in list
        raise SystemExit , u"\n No sequence-like files were found for this path or wildcard"

    pstBuildSequences()
    if len( pst_collectedSequences ) == 0: # nothing sequence-like in list
        raise SystemExit , u"\n No sequences were found for this path or wildcard"
    pstOutputSequences()
    
    ### test output
    
    for item in pst_collectedSequences:
        print '['
        for items in item:
            print "\t" + str(items)
        print '],'
    
    ###/
