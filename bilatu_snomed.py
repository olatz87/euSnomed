#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys,os,getopt,datetime,codecs,xml.dom.minidom
#import xml.etree.ElementTree as ET
from lxml import etree as ET
from util.snomed import Snomed
from xml.dom import minidom

def main(argv):
    path = '../../euSnomed/'
    hizkuntza = 0 #en
    terminoa = ""
    try:
        opts, args = getopt.getopt(argv,"hp:t:i:c:",["path=","terminoa=","hierarkia=","kontzeptua="])
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
        elif opt in ("-c","--kontzeptua"):
            kon = arg
    snomed = Snomed(False,path)
    snomed.kargatu(hie,'_ald')
    #    snomed.kargatu(hie,'')
    if terminoa:
        irteera = snomed.pareaJaso(terminoa)
    else:
        irteera = snomed.kontzeptuaJaso(kon)
    if irteera is None:
        print("Ez da terminoa aurkitu")
    else:
#        lag = ET.tostring(irteera)#,'utf-8')
#        parsed = minidom.parseString(lag)
#        print(parsed.toprettyxml(indent="    "))
#        print(ET.tostring(irteera).decode('iso-8859-1'),pretty_print=True)
        termE = irteera.findall("langSet/ntig")
        print(len(termE))
        print(ET.tounicode(termE[1],pretty_print=True))
        print(ET.tounicode(irteera,pretty_print=True))

if __name__ == "__main__":
    main(sys.argv[1:])

