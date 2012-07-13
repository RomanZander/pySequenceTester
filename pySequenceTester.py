# -*- coding: utf-8 -*- 
'''
@summary: Sequence integrity tester, console version
@since: 2012.07.12
@version: 0.1.0 
@author: Roman Zander
@see:  https://github.com/RomanZander/pySequenceTester
'''
# ---------------------------------------------------------------------------------------------
# TODO
# ---------------------------------------------------------------------------------------------
"""
    -help argument
"""
# ---------------------------------------------------------------------------------------------
# CHANGELOG
# ---------------------------------------------------------------------------------------------
"""
+0.1.0 - 2012.07.12
    arguments reading (none = current dir, path = dir, [path/]wildcard = [dir/]files),
     
"""

import os
import sys
import re
from glob import glob

pst_pathToScan = ''
pst_wildcardToScan = ''
pst_rawFileList = [] 

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
    global pst_rawFileList
    pst_rawFileList = sorted( glob( os.path.join( pst_pathToScan, pst_wildcardToScan )), cmp=pstSortWithLen )
    

def pstCleanUpFileList():
    pass

def pstBuildSequences():
    pass

if __name__ == '__main__':
    pstReadArgv()
    pstGetRawFileList()
    pstCleanUpFileList()
    pstBuildSequences()
    
    ### test output
    print("\n" + 'pst_rawFileList = ')
    for i in pst_rawFileList:
        print (i)
    ###/
    
    