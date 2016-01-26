#!/usr/bin/python3
# -*- coding: utf-8 -*-
from util.enumeratuak import Hierarkia
import sys,os,getopt,datetime,codecs,xml.dom.minidom
from util.snomed import Snomed

def main(argv):
    path = '../../euSnomed/'
    hizkuntza = 0 #en
    hie = 'denak'
    try:
        opts, args = getopt.getopt(argv,"hp:t:i:",["path=","terminoa=","hierarkia="])
    except getopt.GetoptError:
        print('python3 bilatu_itzulDB.py -p <path> -t <terminoa> -i <hierarkia>')
        sys.exit(2)
    for opt, arg in opts:
        if opt =='-h':
            print('python3 bilatu_itzulDB.py -p <path> -t <terminoa> -i <hierarkia>')
            sys.exit()
        elif opt in ("-p","--path"):
            path = arg
        elif opt in ("-t","--terminoa"):
            terminoa = arg
        elif opt in ("-i","--hierarkia"):
            hie = arg
    snomed = Snomed(False,path)
    irteera = 0
    if hie == 'denak':
        HierarkiaLag = Hierarkia
    else:
        HierarkiaLag = [hie]
    for hie in HierarkiaLag:
        print(hie)
        i = 1
        cli = ['','']
        if hie == 'CLINICAL':
            i = 2
            cli = ['_FIN','_DIS']
        for j in range(0,i):
            snomed.kargatu(hie.upper(),cli[j]+'_ald')
            irteera += snomed.getMorfologiakBakarrik()
    print(irteera)
if __name__ == "__main__":
    main(sys.argv[1:])

