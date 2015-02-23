#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys,os,getopt,datetime,codecs
from util.itzuldb import ItzulDB
import scriptak.morfosemantika as MS

def main(argv):
    path = '../../euSnomed/'
    hiz = 'en'
    out = ''
    try:
        opts, args = getopt.getopt(argv,"hp:l:o:",["path=","output=","hizkuntza="])
    except getopt.GetoptError:
        print('python3 ituzldb2txt.py -p <path> -o <outputFile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt =='-h':
            print('python3 euSnomed.py -p <path> -o <outpuFile>')
            sys.exit()
        elif opt in ("-p","--path"):
            path = arg
        elif opt in ("-o","--output"):
            out = arg
        elif opt in ("-l","--hizkuntza"):
            hiz = arg

    if hiz == 'en':
        hizkuntza = 0
    elif hiz == 'es':
        hizkuntza = 1

    if not out:
        out = path+'/baliabideak/itzulDB'+hiz+'.txt'

    itzulDBeng = ItzulDB(path,hizkuntza,fitxategia=path+'/baliabideak/ItzulDB'+hiz+'Has.xml')#en
    print('ItzulDB kargatuta')
    denak = itzulDBeng.denakJaso()
    with codecs.open(out,'w',encoding='utf-8') as fout:
        for key,value in denak.items():
            fout.write(key+'\t'+'\t'.join(value)+'\n')


if __name__ == "__main__":
    main(sys.argv[1:])

