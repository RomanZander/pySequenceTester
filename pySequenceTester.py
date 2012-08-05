# -*- coding: utf-8 -*- 
'''
@summary: File sequence integrity tester, console version
@since: 2012.07.12
@version: 0.1.7
@author: Roman Zander
@see:  https://github.com/RomanZander/pySequenceTester
'''
# ---------------------------------------------------------------------------------------------
# TODO
# ---------------------------------------------------------------------------------------------
"""
    recursive mode
"""
# ---------------------------------------------------------------------------------------------
# CHANGELOG
# ---------------------------------------------------------------------------------------------
"""
+0.1.7
    -h -help argument
+0.1.6
    folder issue#2 fixed
+0.1.5
    folders scan
    output path when directory/subdirectory scanned 
+0.1.4
    smart gap output
+0.1.3
    output chains/gaps
    multipadding trap
+0.1.2 - 2012.07.16
    collect sequences
+0.1.1 - 2012.07.14
    path cleanup from file list,
    regexp pattern cleanup from file list
+0.1.0 - 2012.07.12
    arguments reading (none = current dir, path = dir, [path/]wildcard = [dir/]files),
    getting raw file list,
    dummy functions and SystemExits
"""

import os
import re
import argparse
from glob import glob

pst_pathToScan = ''
pst_wildcardToScan = ''
# pst_mode = '' # TODO recursive scan mode, not implemented
pst_fileList = []
pst_collectedSequences = []

# set and compile naming convention regexp pattern
pst_namingConventionPattern = '^(.*\D)?(\d+)(\.[^\.]+)$'
pst_compiledPattern = re.compile( pst_namingConventionPattern, re.I ) 

def pstParseArgs():
    global pst_pathToScan, pst_wildcardToScan
    parser = argparse.ArgumentParser( description = 'Image|file sequence integrity tester' )
    '''
    # TODO recursive scan mode, not implemented
    parser.add_argument( 
        '-r', '--recursive',
        action = 'store_true',
        dest = 'recursive',
        help = 'scan folders recursive' 
        )
    '''
    parser.add_argument( 
        'whatToScan',
        nargs='?',
        default='',
        metavar='PATH|WILDCARD', 
        help='path and/or wildcard to scan, "./*" by default' 
        )
    args = parser.parse_args()
    
    # argument is not passed (default)
    if args.whatToScan == '':
        pst_pathToScan = '.'
        pst_wildcardToScan = '*'
    # argument is a real directory
    elif os.path.isdir( args.whatToScan ):
        pst_pathToScan = args.whatToScan
        pst_wildcardToScan = '*'
    # treat argument as wildcard 
    else:
        pst_wildcardToScan = args.whatToScan

def pstSmartSort( a, b ):
    aListed = [ a['path'], a['ext'], a['prefix'], a['number'], a['index'] ]
    bListed = [ b['path'], b['ext'], b['prefix'], b['number'], b['index'] ]
    if aListed > bListed:
        return 1
    elif aListed == bListed:
        return 0
    else:
        return -1

def pstSmartPattern( item ):
    mutchResult = pst_compiledPattern.match( item[1] )
    if mutchResult == None:
        return False
    else:
        return os.path.isfile( os.path.join( item[0], item[1] ))
     
def pstGetRawFileList():
    global pst_fileList
    pst_fileList = sorted( glob( os.path.join( pst_pathToScan, pst_wildcardToScan )))
    
def pstCleanUpFileList():
    global pst_fileList
    # extract file basename
    pst_fileList = map(os.path.split, pst_fileList)
    # filter for name convention by regexp pattern
    pst_fileList = filter( pstSmartPattern, pst_fileList )
    
def pstBuildSequences():
    global pst_fileList, pst_collectedSequences
    # build splitted file list (splitted by extention, filename prefix and file number)
    splittedList = [] 
    for fileName in pst_fileList:
        filePath = fileName[0]
        filePrefix = pst_compiledPattern.match( fileName[1] ).group( 1 )
        fileIndex = pst_compiledPattern.match( fileName[1] ).group( 2 )
        fileNumber = int( fileIndex, 10 )
        fileExt = pst_compiledPattern.match( fileName[1] ).group(3)
        splittedList.append( {'path':filePath, 'ext':fileExt, 'prefix':filePrefix, 'number':fileNumber, 'index':fileIndex} )
    # sort splitted file list
    splittedList.sort( cmp = pstSmartSort )
    # recollect by extention
    currentSequence = []
    lastToCompare = None
    for splittedElement in splittedList:
        # first iteration
        if lastToCompare == None:
            currentSequence.append(splittedElement)
            # remember extention and prefix
            lastToCompare = [ splittedElement['ext'], splittedElement['prefix'] ]
        # same extention and prefix
        elif lastToCompare == [ splittedElement['ext'], splittedElement['prefix'] ]:
            currentSequence.append(splittedElement)
        # extention or prefix changed
        else:
            pst_collectedSequences.append(currentSequence)
            lastToCompare = [ splittedElement['ext'], splittedElement['prefix'] ]
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
        chainLastNumber = currentSequence[0]['number'] 
        outputChain = '{path:s}' + os.sep + '{prefix:s}[{start:s}-{finish:s}]{ext:s} - {count:d} frames'
        outputGap = '{path:s}' + os.sep + '{prefix:s}[{start:s}-{finish:s}]{ext:s} GAP FOUND, {count:d} frames'
        # blank line before each sequence
        print ' ' 
        for currentIndex in range( 1, len( currentSequence )):
            # compare current number, if +1 increment
            if currentSequence[ currentIndex ]['number'] == ( chainLastNumber + 1 ):
                # redefine finish and number with current
                chainFinish = currentSequence[ currentIndex ]
                chainLastNumber = currentSequence[ currentIndex ]['number']
            # trap multipadding in index, if equal
            elif currentSequence[ currentIndex ]['number'] == chainLastNumber :
                # create multipadding warning
                multipaddingMessage = u"\n WARNING: MULTIPADDING DETECTED!\n Files " + \
                    currentSequence[ currentIndex ]['prefix'] + \
                    currentSequence[ currentIndex ]['index'] + \
                    currentSequence[ currentIndex ]['ext'] + \
                    " and " + \
                    chainFinish['prefix'] + \
                    chainFinish['index'] + \
                    chainFinish['ext'] + \
                    " found in the same directory."
                # exit with warning 
                raise SystemExit , multipaddingMessage
            # if not +1
            else: 
                # compute and output remembered chain
                chainPathOut = chainStart['path']
                chainPrefixOut = chainStart['prefix']
                if chainPrefixOut == None: 
                    chainPrefixOut = ''
                chainStartOut = chainStart['index']
                chainFinishOut = chainFinish['index']
                chainExtOut = chainStart['ext']
                chainCountOut = chainFinish['number'] - chainStart['number'] + 1
                print outputChain.format( path = chainPathOut,
                                          prefix = chainPrefixOut,
                                          start = chainStartOut,
                                          finish = chainFinishOut,
                                          ext = chainExtOut,
                                          count = chainCountOut )
                # compute and output recognized gap
                gapPathOut = chainStart['path']
                gapPrefixOut = chainStart['prefix']
                if gapPrefixOut == None: 
                    gapPrefixOut = ''
                gapStartOut = str( chainFinish['number'] + 1 ).zfill( len( chainFinish['index'] )) ###
                gapFinishOut = str( currentSequence[ currentIndex ]['number'] - 1 ).zfill( len( currentSequence[currentIndex ]['index'] ))
                gapExtOut = chainStart['ext']
                gapCountOut = currentSequence[ currentIndex ]['number'] - chainFinish['number'] - 1
                print outputGap.format( path = gapPathOut,
                                        prefix = gapPrefixOut,
                                        start = gapStartOut,
                                        finish = gapFinishOut,
                                        ext = gapExtOut,
                                        count = gapCountOut )
                # redefine start, finish and number with current
                chainStart = chainFinish = currentSequence[ currentIndex ]
                chainLastNumber = currentSequence[ currentIndex ]['number']
        # compute and output final chain
        chainPathOut = chainStart['path']
        chainPrefixOut = chainStart['prefix']
        if chainPrefixOut == None: 
            chainPrefixOut = ''
        chainStartOut = chainStart['index']
        chainFinishOut = chainFinish['index']
        chainExtOut = chainStart['ext']
        chainCountOut = chainFinish['number'] - chainStart['number'] + 1
        print outputChain.format( path = chainPathOut,
                                  prefix = chainPrefixOut,
                                  start = chainStartOut,
                                  finish = chainFinishOut,
                                  ext = chainExtOut,
                                  count = chainCountOut )
    # blank line after all
    print ' '

if __name__ == '__main__':
    
    pstParseArgs()
    
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
    