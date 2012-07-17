# -*- coding: utf-8 -*- 
'''
@summary: Sequence integrity tester, console version
@since: 2012.07.12
@version: 0.1.3
@author: Roman Zander
@see:  https://github.com/RomanZander/pySequenceTester
'''
# ---------------------------------------------------------------------------------------------
# TODO
# ---------------------------------------------------------------------------------------------
"""
    gap formatting
    -help argument
    more smart multipadding processing

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
+0.1.2 - 2012.07.16
    collect sequences
+0.1.3
    output chains/gaps
    multipadding trap
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
    # iterate collected sequences
    for currentSequence in pst_collectedSequences:
        # init chain start/finish from first file index/number
        chainStart = chainFinish = currentSequence[0]
        # init last number from first file number
        chainLastNumber = currentSequence[0][2] 
        outputChain = ' {prefix:s}[{start:s}-{finish:s}]{ext:s} - {count:d} frames'
        outputGap = ' {prefix:s}[ ... ]{ext:s} GAP, {count:d} frames'
        # new line before each sequence
        print "\n" 
        for currentIndex in range( 1, len( currentSequence )):
            # compare current number, if +1 increment
            if currentSequence[ currentIndex ][2] == ( chainLastNumber + 1 ):
                # redefine finish and number with current
                chainFinish = currentSequence[ currentIndex ]
                chainLastNumber = currentSequence[ currentIndex ][2]
            # trap multipadding in index, if equal
            elif currentSequence[ currentIndex ][2] == chainLastNumber :
                # create multipadding warning
                multipaddingMessage = u"\n WARNING: MULTIPADDING DETECTED!\n Files " + \
                    currentSequence[ currentIndex ][1] + \
                    currentSequence[ currentIndex ][3] + \
                    currentSequence[ currentIndex ][0] + \
                    " and " + \
                    chainFinish[1] + \
                    chainFinish[3] + \
                    chainFinish[0] + \
                    " found in the same directory."
                # exit with warning 
                raise SystemExit , multipaddingMessage
            # if not +1
            else: 
                # output remembered chain
                print outputChain.format( prefix = chainStart[1],
                    start = chainStart[3],
                    finish = chainFinish[3],
                    ext = chainStart[0],
                    count = chainFinish[2] - chainStart[2] + 1 )
                # compute and output gap
                print outputGap.format( prefix = chainStart[1],
                    ext = chainStart[0],
                    count = currentSequence[ currentIndex ][2] - chainFinish[2] - 1 )
                # redefine start, finish and number with current
                chainStart = chainFinish = currentSequence[ currentIndex ]
                chainLastNumber = currentSequence[ currentIndex ][2]
        # output final chain
        print outputChain.format( prefix = chainStart[1],
                    start = chainStart[3],
                    finish = chainFinish[3],
                    ext = chainStart[0],
                    count = chainFinish[2] - chainStart[2] + 1 )

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
    
    '''
    ### test output
    for item in pst_collectedSequences:
        print ''
        for items in item:
            print "\t" + str(items)
    '''
