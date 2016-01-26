#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys,os,getopt,datetime,codecs
from copy import deepcopy
from util.itzuldb import ItzulDB
from util.enumeratuak import Hierarkia_RF2_izen
from util.emaitzak import Emaitzak
from util.snomed import Snomed
from util.terminotbxsnomed import TerminoTBXSnomed
from util.kontzeptutbx import KontzeptuTBX
import scriptak.morfosemantika as MS
import scriptak.pharma_itzuli as PI
from multiprocessing.pool import ThreadPool
from multiprocessing import Pool, Lock

import locale
locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()


def itzuli(snomed,itzulDBeng,itzulBool,ema,path,lock,hie):
    i = 0
    denera = len(snomed.getTerminoak('en'))
    sys.stdout.write("\r%d / %d\t%d" %(i,denera,hie))
    sys.stdout.flush()
    if True:
        for el in snomed.getTerminoak('en'):
            terminoS = TerminoTBXSnomed(el)
            term = terminoS.getTerminoa()
            termL = len(term.split())
            kodea = terminoS.getId()
            irteera = ['+?']
            usN = terminoS.getUsageNote()
            if termL == 1:
                if usN == "InitialInsensitive":
                    term = term[0].lower()+term[1:]
                if snomed.getHierarkia() == "PHARMPRODUCT" or snomed.getHierarkia() == "SUBSTANCE":
                    
                    irteera = PI.main(['-t',term]).split('\t')
                else:
                    
                    irteera = MS.main(['-t',term]).split('\t')
            if '+?' not in irteera[0]:
                # if usN == 'Sensitive':
                #     listLag = []
                #     for irt in irteera:
                #         listLag.append(irt.capitalize())
                #     irteera = listLag
                if itzulBool:
                    lock.acquire()
                    ordList = itzulDBeng.gehitu(irteera,term,'Morfologia',usN,'Izen','TranscribedForm',7)
                    lock.release()
                if terminoS.getUsageNote() == "Insensitive" or terminoS.getUsageNote() == "InitialInsensitive":
                    term = term.lower()
                    irteera = [x.lower() for x in irteera]
                lock.acquire()
                with codecs.open(path+'/baliabideak/morfoHiztegia.txt','a',encoding='utf-8') as fout:
                    fout.write(term+'\t'+kodea+'\t'+'\t'.join(irteera)+'\n')
                lock.release()
            i += 1
            sys.stdout.write("\r%d / %d" %(i,denera))
            sys.stdout.flush()
        print()

def itzulpenaKudeatu(hie,snomed,itzulDBeng,itzulBool,path,lock):
    print(hie,end='\t')
    snomed.kargatu(hie,'')
    print('Snomed kargatuta')
    itzuli(snomed,itzulDBeng,itzulBool,False,path,lock,hie)

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
    #for hie in Hierarkia:
        #hie = 'FORCE'
        #i = 1
        #cli = ['_ald','_ald']
        #if hie == 'CLINICAL':
        #    i = 2
        #    cli = ['_FIN_ald','_DIS_ald']
        #for j in range(0,i):

        pool = ThreadPool(processes=6)
        lock = Lock()
        #[pool.apply_async(itzulpenaKudeatu,args(hie,snomed,itzulDBeng,itzulBool,path,lock)) for hie in Hierarkia_RF2_izen]
        results = [pool.apply_async(itzulpenaKudeatu,args=(hie,deepcopy(snomed),itzulDBeng,itzulBool,path,lock)) for hie in Hierarkia_RF2_izen]#izen
        output = [p.get() for p in results]
            
    if itzulBool:
        itzulDBeng.fitxategianGorde()


if __name__ == "__main__":
    main(sys.argv[1:])

