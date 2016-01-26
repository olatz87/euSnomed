#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys,os,getopt,datetime,codecs,xml.dom.minidom
#import xml.etree.ElementTree as ET
from lxml import etree as ET
from util.snomed import Snomed
from util.kontzeptutbx import KontzeptuTBX
from util.terminotbxsnomed import TerminoTBXSnomed
from xml.dom import minidom
from util.enumeratuak import Hierarkia
from termcolor import colored

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
    outEn = "../../laburdurakEn.txt"
    outEs = "../../laburdurakEs.txt" 
    with codecs.open(outEn,'w',encoding='utf-8') as fout:
        fout.write('')
    with codecs.open(outEs,'w',encoding='utf-8') as fout:
        fout.write('')    
    for hie in Hierarkia:
        #hie = 'FORCE'
        i = 1
        cli = ['','']
        if hie == 'CLINICAL':
            i = 2
            cli = ['_FIN','_DIS']
        for j in range(0,i):
            print(hie+cli[j],end='\t')
            snomed.kargatu(hie,cli[j])
            print('Snomed kargatuta')
            for kontzeptu in snomed.getKontzeptuak():
                konTBX = KontzeptuTBX(kontzeptu)
                #Aurrena, ingelesezko terminoetan akronimoak ote dauden aztertu
                akron = False
                for el in konTBX.getTerminoak('en'):
                    terminoE = TerminoTBXSnomed(el)
                    term = terminoE.getTerminoa()
                    if " - " in term:
                        zatika = term.split(' - ')
                        if zatika[0].isupper():
                            akron = True
                            termeng = term
                            with codecs.open(outEn,'a',encoding='utf-8') as fout:
                                fout.write(konTBX.getKontzeptuId()[1:]+'\t'+term+'\n')
                if akron:
                    print(colored(termeng,'red'))
                    lag = ''
                    epAkr = False
                    for el in konTBX.getTerminoak('es'):
                        terminoS = TerminoTBXSnomed(el)
                        term = terminoS.getTerminoa()
                        lag += term+'\t'
                        if term.isupper():
                            epAkr = True
                            akr = term
                    print(colored(lag,'green'))
                    if epAkr:
                        for el in konTBX.getTerminoak('es'):
                            terminoS = TerminoTBXSnomed(el)
                            term = terminoS.getTerminoa()
                            if not term.isupper():
                                with codecs.open(outEs,'a',encoding='utf-8') as fout:
                                    fout.write(konTBX.getKontzeptuId()[1:]+'\t'+akr+' - '+term+'\n')
                            #print(ET.tounicode(kontzeptu,pretty_print=True))
            #with codecs.open(outEn,'a',encoding='utf-8') as fout:
            #    fout.write()

if __name__ == "__main__":
    main(sys.argv[1:])



###output: laburdura euren edapenarekin daukaten deskribapenak
