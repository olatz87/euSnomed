#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys,os,getopt,datetime,codecs,xml.dom.minidom
import xml.etree.ElementTree as ET
from util.snomed import Snomed
from xml.dom import minidom
from util.enumeratuak import Hierarkia_RF2_izen as Hierarkia

def main(argv):
    path = '../../euSnomed/'
    hizkuntza = "en"
    hiztegi = '/hiztegiak/'
    sin = False
    denak = '../../SintaxiMaila/terminoak/'
    zbD = "../../euSnomed/zerrendaBeltzak/"
    version = "20150731"
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
        zbCli = ['','']
        # if hie == 'CLINICAL':
        #     i = 2
        #     cli = ['_FIN_ald','_DIS_ald']
        #     zbCli = ["_fin","_dis"]
        for j in range(0,i):
            print(hie+cli[j])
            zb = {}
            if os.path.isfile(zbD+hie.lower()+zbCli[j].lower()+'-ZBen.txt'):
                with codecs.open(zbD+hie.lower()+zbCli[j].lower()+'-ZBen.txt',encoding='utf-8') as fitx:
                    print(hie,"zerrenda beltza kargatuta")
                    for line in fitx:
                        lagLine = line.strip().split('\t')
                        for ll in lagLine[1:]:
                            ll = ll.strip()
                            if ll:
                                lista = zb.get(lagLine[0],[])
                                lista.append(ll)
                                zb[lagLine[0]] = lista
            else:
                print(zbD+hie.lower()+zbCli[j].lower()+'-ZBen.txt')
            snomed.kargatu(hie.upper(),cli[j])
            out2 = path+hiztegi+hie.lower()+cli[j].lower().replace('_ald','')+'-hiztegiElebiduna_'+version+'.txt'
            out1 = path+hiztegi+hie.lower()+cli[j].lower().replace('_ald','')+'-hiztegiElebakarra_'+version+'.txt'
            out = denak+hie.upper()+cli[j].upper().replace('_ALD','')+'_DENAK_'+version+'.txt'
            itzGab = snomed.getItzuliGabeak(hizkuntza)
            irteera = []
            for ter in itzGab:
                lag = ter.getTerminoa()
                if ter.getUsageNote() != "Sensitive":
                    lag = lag[0].lower()+lag[1:]
                irteera.append(lag)
            with codecs.open(out1,'w',encoding='utf-8') as fout:
                fout.write('\n'.join(irteera))
            if sin:
                itzuliak = snomed.getItzuliakSinonimoak(hizkuntza)
            else:
                itzuliak,jatorria = snomed.getItzuliak(hizkuntza,True)
            with codecs.open(out2,'w',encoding='utf-8') as fout:
                for term,ordainak in itzuliak.items():
                    if term in zb:
                        for ordL in zb[term]:
                            if ordL in ordainak:
                                ordainak.remove(ordL)
                    lag = ""
                    if jatorria:
                        lag = "\t"+';'.join(jatorria)
                    fout.write(term+': '+';'.join(ordainak)+lag+'\n')
            with codecs.open(out,'w',encoding='utf-8') as fout:
                fout.write('\n'.join(irteera))
                lag = list(itzuliak.keys())
                fout.write('\n'.join(lag))
            print(hie+cli[j]+' eginda!')

if __name__ == "__main__":
    main(sys.argv[1:])

