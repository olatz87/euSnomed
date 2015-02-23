#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys,os,getopt,datetime,codecs,xml.dom.minidom
import xml.etree.ElementTree as ET
from util.snomed import Snomed
from xml.dom import minidom
from util.enumeratuak import Hierarkia

def main(argv):
    path = '../../euSnomed/'
    hizkuntza = "en"
    hiztegi = '/hiztegiak/'
    sin = False
    #out = path+'/itzuliGabeak/'+hie+'-hitzBakarrekoak.txt'
    try:
        opts, args = getopt.getopt(argv,"hp:l:s",["path=","hizkuntza=","sinonimoak="])
    except getopt.GetoptError:
        print('python3 snomed2hiztegiak.py -p <path> -l <hizkuntza> -o <output> -s <sinonimoakBool>')
        sys.exit(2)
    for opt, arg in opts:
        if opt =='-h':
            print('python3 snomed2hiztegiak.py -p <path> -l <hizkuntza> -o <output> -s <sinonimoakBool>')
            sys.exit()
        elif opt in ("-p","--path"):
            path = arg
        elif opt in ("-l","--hizkuntza"):
            terminoa = arg
        elif opt in ("-s","--sinonimoakBool"):
            sin = True
            hiztegi = '/hiztegiakSinonimoak/'
        elif opt in ("-o","--output"):
            out = arg
        elif opt in ("-k","--hitzKopurua"):
            hitzKopurua = arg
    snomed = Snomed(False,path)
    for hie in Hierarkia:
        i = 1
        cli = ['_ald','_ald']
        if hie == 'CLINICAL':
            i = 2
            cli = ['_FIN_ald','_DIS_ald']
        for j in range(0,i):
            snomed.kargatu(hie.upper(),cli[j])
            out2 = path+hiztegi+hie.lower()+cli[j].lower().replace('_ald','')+'-hiztegiElebiduna.txt'
            out1 = path+hiztegi+hie.lower()+cli[j].lower().replace('_ald','')+'-hiztegiElebakarra.txt'
            itzGab = snomed.getItzuliGabeak(hizkuntza)
            irteera = []
            for ter in itzGab:
                irteera.append(ter.getTerminoa())
            with codecs.open(out1,'w',encoding='utf-8') as fout:
                fout.write('\n'.join(irteera))
            if sin:
                itzuliak = snomed.getItzuliakSinonimoak(hizkuntza)
            else:
                itzuliak = snomed.getItzuliak(hizkuntza)
            with codecs.open(out2,'w',encoding='utf-8') as fout:
                for term,ordainak in itzuliak.items():
                    fout.write(term+': '+';'.join(ordainak)+'\n')
            print(hie+cli[j]+' eginda!')

if __name__ == "__main__":
    main(sys.argv[1:])

