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
    snomed.kargatu(hie,'_ald')
#    snomed.kargatu(hie,'')
    irteera = snomed.pareaJaso(terminoa)
    if irteera is None:
        print("Ez da terminoa aurkitu")
    else:
#        lag = ET.tostring(irteera)#,'utf-8')
#        parsed = minidom.parseString(lag)
#        print(parsed.toprettyxml(indent="    "))
        print(ET.tounicode(irteera,pretty_print=True))

if __name__ == "__main__":
    main(sys.argv[1:])

