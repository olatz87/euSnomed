#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys,os,getopt,datetime,codecs
from util.itzuldb import ItzulDB
from util.enumeratuak import Hierarkia
from util.emaitzak import Emaitzak
from util.snomed import Snomed
from util.terminotbxsnomed import TerminoTBXSnomed
from util.kontzeptutbx import KontzeptuTBX
from util.snomedtbx import SnomedTBX
import scriptak.morfosemantika as MS

def main(argv):
    path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+'/'
    snoBool = False
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
        elif opt in ('-s','--snomed'):
            snoBool = arg
    hizkuntza = 2
    snomed = Snomed(snoBool,path)
    if itzulBool:
        itLag = ItzulDB(path,hizkuntza,itzulBool)
        itLag = None
    itzulDBeng = ItzulDB(path,0)#en
    print('Ingelesezko ItzulDB kargatuta')
    itzulDBspa = ItzulDB(path,1)#es
    print('Gaztelaniazko ItzulDB kargatuta')
    date = datetime.datetime.now()
    emFitx = path+'/emaitzak/emaitza'+str(date.year)+str(date.month)+str(date.day)+'.'+str(date.hour)+str(date.minute)
    proba = False
    for hie in Hierarkia:
        #hie = 'FORCE'
        i = 1
        cli = ['','']
        if hie == 'CLINICAL':
            i = 2
            cli = ['_FIN','_DIS']
        for j in range(0,i):
            ema = Emaitzak(hie,cli[j])
            print(hie+cli[j],end='\t')
            snomed.kargatu(hie,cli[j])
            print('Snomed kargatuta')
            itzuli(snomed,itzulDBeng,itzulDBspa,ema,path)
            snomed.gorde()
            ema.setKontzeptuakItzulita(snomed.getItzulitakoKontzeptuKop())
            ema.setOrdainakItzulita(snomed.getItzulitakoOrdainKop())
            ema.setTerminoakItzulita(snomed.getItzulitakoTerminoKop())
            with codecs.open(path+'/tartekoak/'+hie+cli[j]+'_bai_eng.txt','w',encoding='utf-8') as fitx:
                fitx.write(ema.getTerminoak('en','bai'))
            with codecs.open(path+'/tartekoak/'+hie+cli[j]+'_ez_eng.txt','w',encoding='utf-8') as fitx:
                fitx.write(ema.getTerminoak('en','ez'))
            with codecs.open(path+'/tartekoak/'+hie+cli[j]+'_bai_spa.txt','w',encoding='utf-8') as fitx:
                fitx.write(ema.getTerminoak('es','bai'))
            with codecs.open(path+'/tartekoak/'+hie+cli[j]+'_ez_spa.txt','w',encoding='utf-8') as fitx:
                fitx.write(ema.getTerminoak('es','ez'))
            with codecs.open(emFitx,'a',encoding='utf-8') as fitx:
                fitx.write(ema.idatzi())
                  
        if proba :
            break
    itzulDBeng.fitxategianGorde()
    itzulDBspa.fitxategianGorde()
    #with open(emFitx) as fem:

def semanticTagKopuruakLortu(hizkuntza):
    path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+'/'
    denden = 0
    for hie in Hierarkia:
        i = 1
        cli = ['','']
        if hie == 'CLINICAL':
            i = 2
            cli = ['_FIN','_DIS']
        for j in range(0,i):
            sno = Snomed(False,path)
            sno.kargatu(hie,cli[j])
            print(hie+cli[j])
            den = 0
            if hizkuntza == 'en':
                for key,value in sno.getSemanticTagKop().items():
                    print('\t',key,value)
                    den += value
                    print('Denera:',den)
                denden += den
            else:
                fsn = {}
                with codecs.open(path+'snomed/fsn_spa_active.txt',encoding='utf-8') as fitx:
                    for line in fitx:
                        fsn[line.split('\t')[4]]=line.split('\t')[7]
                kopList = {}
                for konId in sno.getKontzeptuIdak():
                    semTag = SnomedTBX.semanticTagLortu(fsn[konId],'es')
                    kop = kopList.get(semTag,0)
                    kopList[semTag] = kop + 1
                for key,value in kopList.items():
                    print('\t',key,value)
                    den += value
                print('Denera:',den)
                denden += den
    print('\n','Denden:',denden)

if __name__ == "__main__":
    main(sys.argv[1:])

