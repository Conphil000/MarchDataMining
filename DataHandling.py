# -*- coding: utf-8 -*-
"""
Created on Thu Feb  3 13:53:37 2022

@author: Conor
"""
import os
import pandas as pd
import pickle

def getXLSX(
        file,
        page,
        folder = ''
    ):
    return \
        pd.read_excel(
            io = open(os.path.join(folder,file)+'.xlsx','rb'),
            sheet_name = page,
            engine='openpyxl'
        )
def exportPKL(
        obj,
        file,
        folder = '',
        schema = 'pkl'
    ):
    pickle.dump(
        obj,
        open(os.path.join(folder,file)+f'.{schema}','wb')
    )

def importPKL(
        file,
        folder = '',
        schema = 'pkl'
    ):
    with open(os.path.join(folder,file)+f'.{schema}','rb') as f:
        return pickle.load(f)
    
def main():
    print('unit test DataHandling')
    file = 'QA_T1'
    folder = '.\\pklSupport'
    
    qa_t1 = \
        importPKL(file,folder)

    exportPKL(qa_t1, 'QA_T1',folder = './/pklSupport')

if __name__ == '__main__':
    main()
























