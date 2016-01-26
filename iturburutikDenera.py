#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys,os,getopt,datetime,codecs,xml.dom.minidom
import xml.etree.ElementTree as ET
from util.snomed import Snomed
from util.enumeratuak import Iturburua
from util.enumeratuak import Hierarkia
from xml.dom import minidom

def main(argv):
    path = '../../euSnomed'
    #hizkuntza = "en"
    hie = 'clinical_dis'
    #out = path+'/itzuliGabeak/'+hie+'-hitzBakarrekoak.txt'
    try:
        opts, args = getopt.getopt(argv,"hi:j:p:",["path=","iturburua=","hierarkia="])
    except getopt.GetoptError:
        print('python3 iturburutikDenera.py -p <path> -l <hizkuntza> -i <hierarkia> -o <output> -k <hitzKopurua>')
        sys.exit(2)
    for opt, arg in opts:
        if opt =='-h':
            print('python3 iturburutikDenera.py -p <path> -l <hizkuntza> -i <hierarkia> -o <output> -k <hitzKopurua>')
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
    if hie != 'denak':
        HierarkiaLag = [hie]
    else:
        HierarkiaLag = Hierarkia
    snomed = Snomed(False,path)
    ordainKopuruak = {Iturburua['ZT'][0]:0,Iturburua["Erizaintza"][0]:0,Iturburua['Anatomia'][0]:0,Iturburua['GNS10'][0]:0,Iturburua['EuskalTerm'][0]:0,Iturburua['Elhuyar'][0]:0,Iturburua['AdminSan'][0]:0,Iturburua['Medikuak'][0]:0,Iturburua['MapGNS'][0]:0,Iturburua['Morfologia'][0]:0}
    for hie in HierarkiaLag:
        print(hie)
        i = 1
        cli = ['_ald','_ald']
        if hie == 'CLINICAL':
            i = 2
            cli = ['_FIN_ald','_DIS_ald']
        for j in range(0,i):
            snomed.kargatu(hie.upper(),cli[j])
            
            ordainKopLag = snomed.getIturburutik()
            Iturburua1 = ['ZT',"Erizaintza",'Anatomia','GNS10','EuskalTerm','Elhuyar','AdminSan','Medikuak','MapGNS','Morfologia']
            for it in Iturburua1:
                if Iturburua[it][0] in ordainKopLag:
                    ordainKopuruak[Iturburua[it][0]] += ordainKopLag[Iturburua[it][0]]


    for it in Iturburua1:
        if Iturburua[it][0] in ordainKopuruak:
            print(it,'ordainKop:',ordainKopuruak[Iturburua[it][0]])


if __name__ == "__main__":
    main(sys.argv[1:])

