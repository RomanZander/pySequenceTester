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
pst_sequenceList =[]

# set and compile naming convention regexp pattern
pst_namingConventionPattern = '^(.*\D)?(\d+)(\.[^\.]+)$'
pst_compiledPattern = re.compile( pst_namingConventionPattern, re.I ) 

# smart sorting function
def pstSortWithLen( a, b ):
    # for equal length
    if len( a ) == len( b ): 
        if a > b:
            return 1
        else:
            return -1
    # with different length: longer is the greatest    
    elif len( a ) > len( b ):
        return 1
    else:
        return -1

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
    # extract basename
    pst_fileList = map(os.path.basename, pst_fileList) 
    # filter for name convention by regexp pattern
    pst_fileList = filter( pst_compiledPattern.match, pst_fileList )
    pass

def pstBuildSequences():
    pass

def pstOutputSequences():
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
    #if len( pst_sequenceList ) == 0: # nothing sequence-like in list
    #    raise SystemExit , u'No sequences were found'
    pstOutputSequences()
    
    ### test output
    print("\n" + 'pst_rawFileList = ')
    for i in pst_fileList:
        print (i)
    ###/