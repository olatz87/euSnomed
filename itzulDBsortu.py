#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys,os,getopt,datetime,codecs
from util.itzuldb import ItzulDB

def main(argv):
    path = '../../euSnomed/'
    hizkuntza = 2
    try:
        opts, args = getopt.getopt(argv,"hp:l:",["path=","hizkuntza="])
    except getopt.GetoptError:
        print('python3 itzulDBsortu.py -p <path> -l <hizkuntza>')
        sys.exit(2)
    for opt, arg in opts:
        if opt =='-h':
            print('python3 itzulDBsortu.py -p <path>')
            sys.exit()
        elif opt in ("-p","--path"):
            path = arg
        elif opt in ("-l","--hizkuntza"):
            hizkuntza = int(arg)
    itLag = ItzulDB(path,hizkuntza,True)

if __name__ == "__main__":
    main(sys.argv[1:])

