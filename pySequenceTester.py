# -*- coding: utf-8 -*- 
'''
@summary: Sequence integrity tester, console version
@since: 2012.07.12
@version: 0.1.4
@author: Roman Zander
@see:  https://github.com/RomanZander/pySequenceTester
'''
# ---------------------------------------------------------------------------------------------
# TODO
# ---------------------------------------------------------------------------------------------
"""
    -output path when directory/subdirectory scaned
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
+0.1.2 - 2012.07.16
    collect sequences
+0.1.3
    output chains/gaps
    multipadding trap
+0.1.4
    smart gap output
"""

import os
import sys
import re
from glob import glob

pst_pathToScan = ''
pst_wildcardToScan = ''
pst_fileList = []
pst_collectedSequences = []

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
        pst_pathToScan = '.'
        pst_wildcardToScan = '*'
    
    ###
    print
    print 'pst_pathToScan = ' + pst_pathToScan
    print 'pst_wildcardToScan = ' + pst_wildcardToScan 
    ###/

def pstSmartSort( a, b ):
    aListed = [ a['path'], a['ext'], a['prefix'], a['number'], a['index'] ]
    bListed = [ b['path'], b['ext'], b['prefix'], b['number'], b['index'] ]
    if aListed > bListed:
        return 1
    elif aListed == bListed:
        return 0
    else:
        return -1

def pstGetRawFileList():
    global pst_fileList
    pst_fileList = sorted( glob( os.path.join( pst_pathToScan, pst_wildcardToScan )))
    

def pstCleanUpFileList():
    global pst_fileList
    
    ###
    '''
    print pst_fileList
    print '-----------------'
    '''
    ###/
    
    # extract file basename
    #pst_fileList = map(os.path.basename, pst_fileList)
    
     
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
        splittedList.append( {'path':pst_pathToScan, 'ext':fileExt, 'prefix':filePrefix, 'number':fileNumber, 'index':fileIndex} )
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
    