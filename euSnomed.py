#!/soft_orokorra_linux_x86_64/python-3.4.2/bin/python3
# -*- coding: utf-8 -*-

import sys,os,getopt,datetime,codecs,threading,subprocess,gc
from util.itzuldb import ItzulDB
from util.enumeratuak import Hierarkia,Hierarkia_RF2,Hierarkia_RF2_probak,Hierarkia_RF2_izen
from util.emaitzak import Emaitzak
from util.snomed import Snomed
from util.terminotbxsnomed import TerminoTBXSnomed
from util.kontzeptutbx import KontzeptuTBX
from util.snomedtbx import SnomedTBX
from util.ordaintbxitzuldb import OrdainTBXItzulDB
import scriptak.morfosemantika as MS
import scriptak.pharma_itzuli as PI
import scriptak.terminoKonplexuaItzuli as TK
#import multiprocessing as mp
from multiprocessing.pool import ThreadPool
from multiprocessing import Pool, Lock
from termcolor import colored
from copy import deepcopy
from analizatzaileak import analizatzailea_en
from subprocess import Popen,PIPE
from lxml import etree as ET

#Hierarkia_RF2 = ["SPECIAL"]
#@profile
def itzuli(snomed,itzulDBeng,ema,path,engHash,spaHash,kode_en,kode_es,tok_kop,lock,adj_hiz,kat_hiz):
    hie = snomed.getHierarkia()
    if tok_kop == 1 and hie in ['SITUATION','EVENT',"FINDING",'DISORDER']:
        snomed.mapGNS(ema)

    zbD = path+'/zerrendaBeltzak/'
    zb = {}
    if os.path.isfile(zbD+hie.lower()+'-ZB.txt'):
        with codecs.open(zbD+hie.lower()+'-ZB.txt',encoding='utf-8') as fitx:
            for line in fitx:
                lagLine = line.strip().split('\t')
                for ll in lagLine[1:]:
                    ll = ll.strip()
                    if ll:
                        lista = zb.get(lagLine[0],[])
                        lista.append(ll)
                        zb[lagLine[0]] = lista
    
    gehitzeko = {}
    i = 0
    denera = len(kode_en)+len(kode_es)
    morfo_hiz = {} 
    with codecs.open(path+"/baliabideak/morfoHiztegia.txt",encoding="utf-8") as fmor:
        for line in fmor:
            zat = line.strip().split('\t')
            morfo_hiz[zat[1]] = zat[2:]
    gc.collect()
    # sys.stdout.write("\r%d / %d" %(i,denera))
    # sys.stdout.flush()
    #for kontzeptu in snomed.getKontzeptuak():
    #if True:
    #    #konTBX = KontzeptuTBX(kontzeptu)
    #    #Aurrenik gaztelaniazko hiztegietatik elikatu
    #    #if i%10 == 0:
        
    #    #for el in konTBX.getTerminoak('es'):
    termL = tok_kop#len(term.split())
    for el in []:#kode_es:
        #Terminoen kontaketa egiten da estatistikak ateratzeko, zenbat termino ditugun hitz bakarrekoak....
        terminoS = snomed.getTerminoa(el)#TerminoTBXSnomed(el)
        if terminoS == None:
            print("terminoS == None",el,hie)
        konTBX = KontzeptuTBX(terminoS.getKontzeptua())
        #term = terminoS.getNormalizatua()
        term = terminoS.getTerminoa()
        if terminoS.getUsageNote() == "InitialInsensitive":
            term = term[0].lower()+term[1:]
        elif terminoS.getUsageNote() == "Insensitive":
            term = term.lower()
        ema.gehiToken(termL,'denera','es')
        ordList = spaHash.get(term.lower(),None)
        if ordList:
            ema.gehiToken(termL,'itzulia','es')
            konTBX.eguneratu(ordList,terminoS.term,ema,zb)
            ema.setTerminoa(term,'es','bai')
        else:
            ema.setTerminoa(term,'es','ez')
        i += 1
        if i%1000 == 0:
            print(hie,i,'/',denera)
        # sys.stdout.write("\r%d / %d" %(i,denera))
        # sys.stdout.flush()
    gc.collect()
    print(hie,"gaztelania eginda.",len(kode_en),"falta dira")
    # for ordL in engHash.get("evening"):
    #     print(ET.tounicode(ordL,pretty_print=True))
    i = len(kode_es)
    for el in kode_en:#konTBX.getTerminoak('en'):
        #print(el)
        itzulia = False
        terminoS = snomed.getTerminoa(el)#TerminoTBXSnomed(el)
        konTBX = KontzeptuTBX(terminoS.getKontzeptua())
        #pprint(konTBX)
        term = terminoS.getTerminoa()
        tid = terminoS.getId()
        if terminoS.getUsageNote() == "InitialInsensitive":
            term = term[0].lower()+term[1:]
        elif terminoS.getUsageNote() == "Insensitive":
            term = term.lower()

        termLag = term.replace(" ","_")
        ema.gehiToken(termL,'denera','en')
        #Lehenengo urratsa
        ordList = engHash.get(term.lower(),None)
        # print(el)
        if ordList:
            #print(termL,ordList)
            ema.gehiToken(termL,'itzulia','en')
            konTBX.eguneratu(ordList,terminoS.term,ema,zb)
            ema.setTerminoa(term,'en','bai')
            itzulia = True
            for ordL in ordList:
                ordT = OrdainTBXItzulDB(ordL)
                ordTerm = ordT.getKarKatea()
                if termLag in gehitzeko:
                    gehitzeko[termLag].add(ordT)
                else:
                    gehitzeko[termLag] = {ordT}
        if not itzulia:
            if tok_kop == 1:
                if tid in morfo_hiz:
                    irteera = morfo_hiz[tid]
                elif hie == "PHARMPRODUCT" or hie == "SUBSTANCE":
                    irteera = PI.main(['-t',term[0].lower()+term[1:]]).split('\t')
                else:
                    irteera = MS.main(['-t',term]).split('\t')
                if '+?' not in irteera[0]:
                    ema.gehiToken(termL,'itzulia','en')
                    if terminoS.getUsageNote() == 'Sensitive':
                        listLag = []
                        for irt in irteera:
                            listLag.append(irt.capitalize())
                        irteera = listLag
                    lock.acquire()
                    pos = set(["Izen"])
                    if len(term) > 4 and (term[-4:] in ["like","otic","able","adic"] or term[-3:] == "ous" or term[-2:] == "al"):
                        #print("Izenondo")
                        pos = set(["Izenondo"])
                    ordList = itzulDBeng.gehitu(irteera,term,'Morfologia',terminoS.getUsageNote(),pos,'TranscribedForm',7)
                    lock.release()
                    engHash[term] = ordList
                    konTBX.eguneratu(ordList,terminoS.term,ema,zb)
                    ema.setTerminoa(term,'en','bai')
                    itzulia = True
                    #print('Morfo',termLag,irteera)
                    for ordL in ordList:
                        ordT = OrdainTBXItzulDB(ordL)
                        if termLag in gehitzeko:
                            gehitzeko[termLag].add(ordT)
                        else:
                            gehitzeko[termLag] = {ordT}
                else: #EDBL-en ingelesekoa literalki agertzen bada, aurrera
                    if term in kat_hiz:
                        ordList = itzulDBeng.gehitu([term],term,'EDBL',terminoS.getUsageNote(),set(),'Literal',7)               
                        for ordL in ordList:
                            ordT = OrdainTBXItzulDB(ordL)
                            if termLag in gehitzeko:
                                gehitzeko[termLag].add(ordT)
                            else:
                                gehitzeko[termLag] = {ordT}
            else:
                try:
                    itzulpenak,apl_patroiak = TK.main(['-t',term])
                except Exception:
                    itzulpenak = set()
                if "" in itzulpenak:
                    itzulpenak.remove("")
                #print(itzulpenak,len(itzulpenak))
                if len(itzulpenak) >= 1:
                    lock.acquire()
                    ordList = itzulDBeng.gehitu(itzulpenak,term,"Patroiak",terminoS.getUsageNote(),set(["TerminoKonplexu"]),"",6,apl_patroiak)
                    lock.release()
                    engHash[term] = ordList
                    konTBX.eguneratu(ordList,terminoS.term,ema,zb)
                    ema.setTerminoa(term,'en','bai')
                    itzulia = True
                    #print('Patroiak',termLag,itzulpenak)
                    for ordL in ordList:
                        ordT = OrdainTBXItzulDB(ordL)
                        if termLag in gehitzeko:
                            gehitzeko[termLag].add(ordT)
                        else:
                            gehitzeko[termLag] = {ordT}
        if not itzulia:
            ema.setTerminoa(term,'en','ez')
        i += 1
        if i%1000 == 0:
            print(hie,i,'/',denera)
        #sys.stdout.write("\r%d / %d" %(i,denera))
        #sys.stdout.flush()
    gc.collect()
    print("Lex-ak eguneratuko dira",hie.lower(),len(gehitzeko))
    if len(gehitzeko)>0:
        flex_ize = "scriptak/foma/lex/"+hie.lower()+'.lex'
        with codecs.open(flex_ize) as flex:
            fList = flex.readlines()[:-1]
            for eng,eusak in gehitzeko.items():
                for ordT in eusak:
                    eus = ordT.getKarKatea()
                    pos = ordT.getPOS()
                    posE = ""
                    if hie == "QUALIFIER":
                        if not pos:
                            posE = "Adjektibo"
                        #print(eus,pos)

                    for posLag in pos:
                        posL = posLag.text
                        if hie == "QUALIFIER":
                            #print("posL",posL)
                            
                            if posL in ["Izenondo","Izenlagun"]:
                                posE = posL
                                break
                            elif posL == "Adjektibo":
                                posE = posL
                            else:
                                if posE not in ["Izenondo","Izenlagun","Adjektibo"]:
                                    posE = posL
                        else:
                            posE = posL
                    if tok_kop == 1 and posE == "Izenondo":# eus in adj_hiz:
                        #print(eus,adj_hiz[eus])
                        eus += "&&&ADJK"#+adj_hiz[eus].strip()
                    elif tok_kop == 1 and posE == "Izenlagun":
                        eus += "&&&IZLK"#+adj_hiz[eus].strip()
                    elif tok_kop == 1 and posE == "Adjektibo":
                        if len(eus)>3 and eus[-3:] == "ren":
                            eus += "&&&IZLK"#+adj_hiz[eus].strip()
                        elif len(eus)>3 and eus[-3] != "i" and eus[-2:] in ["ko","go"]:
                            eus += "&&&IZLK"
                        else:
                            eus += "&&&ADJK"
                    lagStr = eng+':'+eus.replace(' ','_')+' #;\n'
                    lagStr.replace("<","%<").replace(">","%>")
                    if lagStr.encode('utf-8') not in fList:
                        fList.append(lagStr.encode('utf-8'))
            fList.append(b'END\n')
        with codecs.open(flex_ize,'w',encoding='utf-8') as fout:
            lag = b''.join(fList)
            fout.write(lag.decode('utf-8'))
    #print()
    gc.collect()
    
#@profile
def itzulpenaKudeatu(hie,tok_kop,i_min,i_max,path,snomed,itzulDBeng,itzulEnHash,itzulSpHash,emFitx,emaitzak,lock,adj_hiz,kat_hiz):
    if tok_kop == i_min:
        ema = Emaitzak(hie)
        if i_min > 1:
            snomed.kargatu(hie,"_ald")
        else:
            snomed.kargatu(hie)
    else:
        ema = emaitzak[hie]
        snomed.kargatu(hie,'_ald')
    #,cli[j])

    kodeak_en = []
    kodeak_es = []
    with codecs.open(path+'/snomed/tokenak/'+hie.lower()+'.txt',encoding='utf-8') as fitx:
        i_lag = i_min
        while i_lag <= tok_kop:
            line = fitx.readline()
            if line:
                cId,i_lag = line.split("\t")
                i_lag = int(i_lag)
                if i_lag == tok_kop:
                    if cId[:2] == "es":
                        kodeak_es.append(cId)
                    else:
                        kodeak_en.append(cId)
            else:
                i_lag += i_max
    luz = len(kodeak_en)+len(kodeak_es)
    print(colored(hie+' Snomed kargatuta '+str(luz),"green"))
    
    itzuli(snomed,itzulDBeng,ema,path,itzulEnHash,itzulSpHash,kodeak_en,kodeak_es,tok_kop,lock,adj_hiz,kat_hiz)
    snomed.gorde()
    ema.setKontzeptuakItzulita(snomed.getItzulitakoKontzeptuKop())
    ema.setOrdainakItzulita(snomed.getItzulitakoOrdainKop())
    ema.setTerminoakItzulita(snomed.getItzulitakoTerminoKop())

    if tok_kop == i_max:
        with codecs.open(path+'/tartekoak/'+hie+'_bai_eng.txt','w',encoding='utf-8') as fitx:
            fitx.write(ema.getTerminoak('en','bai'))
        with codecs.open(path+'/tartekoak/'+hie+'_ez_eng.txt','w',encoding='utf-8') as fitx:
            fitx.write(ema.getTerminoak('en','ez'))
        with codecs.open(path+'/tartekoak/'+hie+'_bai_spa.txt','w',encoding='utf-8') as fitx:
            fitx.write(ema.getTerminoak('es','bai'))
        with codecs.open(path+'/tartekoak/'+hie+'_ez_spa.txt','w',encoding='utf-8') as fitx:
            fitx.write(ema.getTerminoak('es','ez'))
        with codecs.open(emFitx,'a',encoding='utf-8') as fitx:
            fitx.write(ema.idatzi())
    print(colored(hie+' bukatuta',"red"))
    return (ema,hie)

# def init(l):
#     global lock
#     lock = l

#@profile
def main(argv):
    path = '../../euSnomed/'
    snoBool = False
    itzulBool = False
    lexBool = False
    try:
        opts, args = getopt.getopt(argv,"hp:s:i:l",["path=","snomed=","itzuldb=","lex"])
    except getopt.GetoptError:
        print('python3 euSnomed.py -p <path> -s <snomedBool> -i <itzulDBBool>')
        sys.exit(2)
    for opt, arg in opts:
        if opt =='-h':
            print('python3 euSnomed.py -p <path> -s -i -l ')
            sys.exit()
        elif opt in ("-p","--path"):
            path = arg
        elif opt in ("-i","--itzuldb"):
            itzulBool = True
        elif opt in ('-s','--snomed'):
            snoBool = True
        elif opt in ('-l','--lex'):
            lexBool = True
    hizkuntza = 2
    snomed = Snomed(snoBool,path)
    if itzulBool:
        itLag = ItzulDB(path,hizkuntza,itzulBool)
        itLag = None
    itzulDBeng = ItzulDB(path,0)#en
    itzulEnHash = itzulDBeng.toHash()
    # for ordL in itzulEnHash["evening"]:
    #     print(ET.tounicode(ordL,pretty_print=True))
    print('Ingelesezko ItzulDB kargatuta')
    itzulDBspa = ItzulDB(path,1)#es
    itzulSpHash = itzulDBspa.toHash()
    #itzulDBspa = None
    #itzulSpHash = {}
    print('Gaztelaniazko ItzulDB kargatuta')
    date = datetime.datetime.now()
    emFitx = path+'/emaitzak/emaitza'+str(date.year)+str(date.month)+str(date.day)+'.'+str(date.hour)+str(date.minute)
    if lexBool:
        lexIdatz = "LEXICON Root\nEND"
        for hie in Hierarkia_RF2:
            with codecs.open("scriptak/foma/lex/"+hie.lower()+".lex",'w',encoding='utf-8') as flex:
                flex.write(lexIdatz)
    proba = False
    emaDen = Emaitzak("DENAK","")
    emaitzak = {}
    i_min = 6
    i_max = 52
    #i_max = 4
    pat_app = {}
    pool = ThreadPool(processes=6)
    lock = Lock()
    for tok_kop in range(i_min,i_max): #Kontuz!!! i_min inkrementatu dut!!!
        print("Itzulpena hasiko da: "+str(tok_kop)+" tokenetarako")  
        #pool = mp.Pool(processes=4)
        #hie = "SOCIAL"
        #itzulpenaKudeatu(hie,tok_kop,i_min,i_max,path,snomed,itzulDBeng,itzulDBspa,itzulEnHash,itzulSpHash,emFitx,emaitzak)
        #print("Proba ondo joan da")
        #results = [pool.apply_async(itzulpenaKudeatu,args=(hie,tok_kop,i_min,i_max,path,snomed,itzulDBeng,itzulDBspa,itzulEnHash,itzulSpHash,emFitx,emaitzak,)) for hie in Hierarkia_RF2]
        #output = [p.get() for p in results]
        #pool = Pool(processes=6,initializer=init,initargs=(1,))
        adj_hiz = {}
        kat_hiz = {}
        if tok_kop == 1:
            with codecs.open(path+"/baliabideak/edbl_adjektiboak.txt",encoding= "iso-8859-1") as adjf:
                lerroak = adjf.readlines()
                for line in lerroak[2:]:
                    if line:
                        zat = line.strip().split("\t")
                        adj_hiz[zat[1]] = zat[4]
            with codecs.open(path+"/baliabideak/edbl_kategoriak.txt",encoding= "iso-8859-1") as katf:
                lerroak = katf.readlines()
                for line in lerroak[2:]:
                    zat = line.strip().split("\t")
                    kat_hiz[zat[1]] = zat[3]
                lerroak = [] #memoria garbitzeko
                line = "" #memoria garbitzeko
        else:
            adj_hiz = {}
            kat_hiz = {}
        results = [pool.apply_async(itzulpenaKudeatu,args=(hie,tok_kop,i_min,i_max,path,deepcopy(snomed),itzulDBeng,itzulEnHash,itzulSpHash,emFitx,emaitzak,lock,adj_hiz,kat_hiz)) for hie in Hierarkia_RF2_izen ]#Hierarkia_RF2_izen//probak
        output = [p.get() for p in results]
        for em,hi in output:
            emaitzak[hi] = em
        if proba :
            break
        print('lex-en eguneraketak scriptetan eragina izateko birkonpilatuko dira\n')
        itzulDBeng.fitxategianGorde()
        subprocess.call('foma -l scriptak/foma/kategorizazioaOrokortuta.script',shell=True)
        subprocess.call('foma -l scriptak/foma/itzulpena.script',shell=True)
    emaDen.batuEmaitzakList(emaitzak)
    itzulDBeng.fitxategianGorde()
    with codecs.open(emFitx,'a',encoding='utf-8') as fitx:
        fitx.write(emaDen.idatzi())
    #itzulDBspa.fitxategianGorde()
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

