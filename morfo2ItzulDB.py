#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys,os,getopt,datetime,codecs
from util.itzuldb import ItzulDB
from util.enumeratuak import Hierarkia
from util.emaitzak import Emaitzak
from util.snomed import Snomed
from util.terminotbxsnomed import TerminoTBXSnomed
from util.kontzeptutbx import KontzeptuTBX
import scriptak.morfosemantika as MS
import scriptak.pharma_itzuli as PI

def itzuli(snomed,itzulDBeng,itzulBool,ema,path):
    i = 0
    denera = len(snomed.getTerminoak('en'))
    sys.stdout.write("\r%d / %d" %(i,denera))
    sys.stdout.flush()
    with codecs.open(path+'/baliabideak/morfoHiztegia.txt','a',encoding='utf-8') as fout:
        for el in snomed.getTerminoak('en'):
            terminoS = TerminoTBXSnomed(el)
            term = terminoS.getTerminoa()
            termL = len(term.split())
            kodea = terminoS.getId()
            irteera = ['+?']
            if termL == 1:
                if snomed.getHierarkia() == "PHARMPRODUCT" or snomed.getHierarkia() == "SUBSTANCE":
                    irteera = PI.main(['-t',term[0].lower()+term[1:]]).split('\t')
                else:
                    irteera = MS.main(['-t',term.lower()]).split('\t')
            if '+?' not in irteera[0]:
                if terminoS.getUsageNote() == 'Sensitive':
                    listLag = []
                    for irt in irteera:
                        listLag.append(irt.capitalize())
                    irteera = listLag
                if itzulBool:
                    ordList = itzulDBeng.gehitu(irteera,term,'Morfologia',terminoS.getUsageNote(),'Izen','TranscribedForm',7)
                if terminoS.getUsageNote() == "Insensitive" or terminoS.getUsageNote() == "InitialInsensitive":
                    term = term.lower()
                    irteera = [x.lower() for x in irteera]
                fout.write(term+'\t'+kodea+'\t'+','.join(irteera)+'\n')
            i += 1
            sys.stdout.write("\r%d / %d" %(i,denera))
            sys.stdout.flush()
        print()


def main(argv):
    path = '../../euSnomed/'
    itzulBool = False
    try:
        opts, args = getopt.getopt(argv,"hp:s:i:",["path=","snomed=","itzuldb="])
    except getopt.GetoptError:
        print('python3 euSnomed.py -p <path> -s <snomedBool> -i <itzulDBBool>')
        sys.exit(2)
    for opt, arg in opts:
        if opt =='-h':
            print('python3 euSnomed.py -p <path> -s <snomedBool> -i <itzulDBBool>')
            sys.exit()
        elif opt in ("-p","--path"):
            path = arg
        elif opt in ("-i","--itzuldb"):
            itzulBool = arg
    hizkuntza = 2
    snomed = Snomed(False,path)
    if itzulBool:
        itzulDBeng = ItzulDB(path,0)#en
    else:
        itzulDBeng = None
    print('Ingelesezko ItzulDB kargatuta')
    with codecs.open(path+'/baliabideak/morfoHiztegia.txt','w',encoding='utf-8') as fout:
        fout.write('')
    for hie in Hierarkia:
        #hie = 'FORCE'
        i = 1
        cli = ['_ald','_ald']
        if hie == 'CLINICAL':
            i = 2
            cli = ['_FIN_ald','_DIS_ald']
        for j in range(0,i):
            print(hie+cli[j],end='\t')
            snomed.kargatu(hie,cli[j])
            print('Snomed kargatuta')
            itzuli(snomed,itzulDBeng,itzulBool,False,path)
    itzulDBeng.fitxategianGorde()


if __name__ == "__main__":
    main(sys.argv[1:])

