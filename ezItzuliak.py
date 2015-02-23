#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys,os,getopt,datetime,codecs,xml.dom.minidom
import xml.etree.ElementTree as ET
from util.snomed import Snomed
from xml.dom import minidom

def main(argv):
    path = '../../euSnomed'
    hizkuntza = "en"
    hitzKopurua = 1
    hie = 'pharmproduct'
    #out = path+'/itzuliGabeak/'+hie+'-hitzBakarrekoak.txt'
    try:
        opts, args = getopt.getopt(argv,"hp:l:i:o",["path=","terminoa=","hierarkia="])
    except getopt.GetoptError:
        print('python3 ezItzuliak.py -p <path> -l <hizkuntza> -i <hierarkia> -o <output> -k <hitzKopurua>')
        sys.exit(2)
    for opt, arg in opts:
        if opt =='-h':
            print('python3 ezItzuliak.py -p <path> -l <hizkuntza> -i <hierarkia> -o <output> -k <hitzKopurua>')
            sys.exit()
        elif opt in ("-p","--path"):
            path = arg
        elif opt in ("-l","--hizkuntza"):
            terminoa = arg
        elif opt in ("-i","--hierarkia"):
            hie = arg
        elif opt in ("-o","--output"):
            out = arg
        elif opt in ("-k","--hitzKopurua"):
            hitzKopurua = arg
    out = path+'/itzuliGabeak/'+hie+'-hitzBakarrekoak.txt'
    snomed = Snomed(False,path)
    snomed.kargatu(hie.upper(),'_ald')
    itzGab = snomed.getItzuliGabeak(hizkuntza)
    irteera = []
    for ter in itzGab:
        if hitzKopurua == 1:
            if len(ter.getTerminoa().split()) == 1:
                irteera.append(ter.getTerminoa())
        else:
            irteera.append(ter.getTerminoa())
    with codecs.open(out,'w',encoding='utf-8') as fout:
        fout.write('\n'.join(irteera))
if __name__ == "__main__":
    main(sys.argv[1:])

