#!/soft_orokorra_linux_x86_64/python-3.4.2/bin/python3
# -*- coding: utf-8 -*-

import pickle,codecs,os,gc,random,sys,subprocess,re
import scriptak.morfosemantika as MS
import scriptak.pharma_itzuli as PI
import scriptak.terminoKonplexuaItzuli as TK
#from util.ordaintbxitzuldb import OrdainTBXItzulDB
from util.kontzeptutbx import KontzeptuTBX
from util.snomed import Snomed
from util.emaitzak import Emaitzak
from util.itzuldb import ItzulDB

from subprocess import PIPE,Popen

from termcolor import colored
from lxml import etree as ET

# def lexentzat(ordList,gehitzeko,termLag):
#     for ordL in ordList:
#         ordT = OrdainTBXItzulDB(ordL)
#         if termLag in gehitzeko:
#             gehitzeko[termLag].add(ordT)
#         else:
#             gehitzeko[termLag] = {ordT}

# def pluralaGehitu(hitza):
#     p2 = subprocess.Popen(['flookup -i -x -b  scriptak/foma/deklinabideak.fst'],stdin=PIPE,stdout=PIPE,shell=True)
#     hitza += "+ak"
#     returnwords = p2.communicate(input=hitza.encode('utf8'))
#     plurala = returnwords[0].decode('utf8').split('\n')[0]
#     return plurala

def generoaEbatzi(term,hasha):
    lag = term[:-1]+"o"
    return lag in hasha

def pluralaEbatzi(term,hasha,hiz):
    lag = term[:-1]
    ordList = False
    if lag in hasha:
        ordList = True
    else:
        if lag[-1] == "e":
            lag2 = lag[:-1]
            ordList = lag2 in hasha
        elif lag[-1] == "a" and hiz == "es":
            lag2 = term[:-1]+"o"
            ordList = lag2 in hasha
    return ordList

#Hierarkia_RF2 = ["SPECIAL"]
#@profile
#def itzuli(snomed,itzulDBeng,ema,path,engHash,spaHash,kode_en,kode_es,tok_kop,lock,adj_hiz,kat_hiz):
def itzuli(snomed,ema,path,engHash,spaHash,kode_en,kode_es,tok_kop,adj_hiz,kat_hiz):
    hie = snomed.getHierarkia()
    # if tok_kop == 1 and hie in ['SITUATION','EVENT',"FINDING",'DISORDER']:
    #     snomed.mapGNS(ema)
    zbD = path+'/zerrendaBeltzak/'
    zb_en = {}
    zb_es = {}
    if os.path.isfile(zbD+hie.lower()+'-ZBen.txt'):
        with codecs.open(zbD+hie.lower()+'-ZBen.txt',encoding='utf-8') as fitx:
            for line in fitx:
                line = re.sub("  +","\t",line.strip())
                lagLine = line.split('\t')
                for ll in lagLine[1:]:
                    ll = ll.strip()
                    if ll:
                        lista = zb_en.get(lagLine[0],[])
                        lista.append(ll)
                        zb_en[lagLine[0]] = lista

    if os.path.isfile(zbD+hie.lower()+'-ZBes.txt'):
        with codecs.open(zbD+hie.lower()+'-ZBes.txt',encoding='utf-8') as fitx:
            for line in fitx:
                lagLine = line.strip().split('\t')
                for ll in lagLine[1:]:
                    ll = ll.strip()
                    if ll:
                        lista = zb_es.get(lagLine[0],[])
                        lista.append(ll)
                        zb_es[lagLine[0]] = lista

    
    #gehitzeko = {}
    i = 0
    denera = len(kode_en)+len(kode_es)
    # morfo_hiz = {} 
    # with codecs.open(path+"/baliabideak/morfoHiztegia.txt",encoding="utf-8") as fmor:
    #     for line in fmor:
    #         zat = line.strip().split('\t')
    #         morfo_hiz[zat[1]] = zat[2:]
    gc.collect()
    eguneratzekoak = []
    ord_hiztegia = {}
    termL = tok_kop#len(term.split())
    for el in kode_es:
        #Terminoen kontaketa egiten da estatistikak ateratzeko, zenbat termino ditugun hitz bakarrekoak....
        terminoS = snomed.getTerminoTBX(el)#TerminoTBXSnomed(el)
        if terminoS == None:
            print("terminoS == None",el,hie)
        konTBX = KontzeptuTBX(terminoS.getKontzeptua())
        konId = konTBX.getKontzeptuId()
        #term = terminoS.getNormalizatua()
        term = terminoS.getTerminoa()
        if terminoS.getUsageNote() == "InitialInsensitive":
            term = term[0].lower()+term[1:]
        elif terminoS.getUsageNote() == "Insensitive":
            term = term.lower()
        ema.gehiToken(termL,'denera','es')
        ordList = term.lower() in spaHash
        if ordList == False:
            #plurala eta generoa
            if term.endswith("s"):
                ordList = pluralaEbatzi(term.lower(),spaHash,"es")
            elif term.endswith("a"):
                ordList = generoaEbatzi(term.lower(),spaHash)
        if ordList:
            ema.gehiToken(termL,'itzulia','es')
            #konTBX.eguneratu(ordList,terminoS.term,ema,zb)
            egu_lag = {'konTBX':konId,'ordList':1,'term':terminoS.getId(),'zb':zb_es}
            #print(egu_lag)
            eguneratzekoak.append(egu_lag)
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
        itzulia = False
        terminoS = snomed.getTerminoTBX(el)#TerminoTBXSnomed(el)
        konTBX = KontzeptuTBX(terminoS.getKontzeptua())
        konId = konTBX.getKontzeptuId()
        #pprint(konTBX)
        term = terminoS.getTerminoa()
        tid = terminoS.getId()
        if terminoS.getUsageNote() == "InitialInsensitive":
            term = term[0].lower()+term[1:]
        elif terminoS.getUsageNote() == "Insensitive":
            term = term.lower()
        #termLag = term.replace(" ","_")
        ema.gehiToken(termL,'denera','en')
        #Lehenengo urratsa
        ordList = term.lower() in engHash
        #QUALIFIER-en kasuan, letra bakarrekoak ez itzuli.
        if tok_kop == 1 and len(term) == 1:# and hie == "QUALIFIER":
            #print("literala!!!",term)
            pos = set(["Izen"])
            ord_lag = {'ordList':term,'term':term,'entrySource':'Literala','caseSig':terminoS.getUsageNote(),'pOS':pos,'tT':'TranscribedForm','rC':7}
            ord_key = term+'-'+str(random.randrange(1,1000))
            ord_hiztegia[ord_key]=ord_lag
            egu_lag = {'konTBX':konId,'ordList':ord_key,'term':tid,'ema':ema,'zb':zb_en}
            eguneratzekoak.append(egu_lag)
            ema.setTerminoa(term,'en','bai')
            itzulia = True
            ordList = False
        #print(el)
        if ordList == False:
            #plurala
            if len(term) > 1 and term.endswith("s"):
                ordList = pluralaEbatzi(term.lower(),engHash,"en")

        if ordList:
            ema.gehiToken(termL,'itzulia','en')
            #konTBX.eguneratu(ordList,terminoS.term,ema,zb)
            egu_lag = {'konTBX':konId,'ordList':0,'term':terminoS.getId(),'zb':zb_en}
            eguneratzekoak.append(egu_lag)
            ema.setTerminoa(term,'en','bai')
            itzulia = True
            #lexentzat(ordList,gehitzeko)
        #print(term,"itzulia:",itzulia)
        if not itzulia:
            if tok_kop == 1:
                # if tid in morfo_hiz:
                #     irteera = morfo_hiz[tid]
                if hie == "PHARMPRODUCT" or hie == "SUBSTANCE":
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
                    #lock.acquire()
                    pos = set(["Izen"])
                    if len(term) > 4 and term.endswith(("like","able","ic","ous","al","ive","ible","ful","less")):
                        #print("Izenondo")
                        pos = set(["Izenondo"])
                    ord_lag = {'ordList':irteera,'term':term,'entrySource':'Morfologia','caseSig':terminoS.getUsageNote(),'pOS':pos,'tT':'TranscribedForm','rC':7}
                    ord_key = term+'-'+str(random.randrange(1,1000))
                    ord_hiztegia[ord_key]=ord_lag
                    egu_lag = {'konTBX':konId,'ordList':ord_key,'term':terminoS.getId(),'zb':zb_en}
                    eguneratzekoak.append(egu_lag)
                    ema.setTerminoa(term,'en','bai')
                    itzulia = True
                    #print('Morfo',termLag,irteera)
                    #lexentzat(ordList,gehitzeko,termLag)
                else: #EDBL-en ingelesekoa literalki agertzen bada, aurrera
                    if term in kat_hiz or term in adj_hiz:
                        #ordList = itzulDBeng.gehitu([term],term,'EDBL',terminoS.getUsageNote(),set(),'Literal',7)     
                        #pos set() gisa uzten dugu, itzuldbtbx arduratuko baita egokia ipintzeaz
                        ord_lag = {'ordList':[term],'term':term,'entrySource':'EDBL','caseSig':terminoS.getUsageNote(),'pOS':set(),'tT':'Literal','rC':7}
                        ord_key = term+'-'+str(random.randrange(1,1000))
                        ord_hiztegia[ord_key]=ord_lag
                        egu_lag = {'konTBX':konId,'ordList':ord_key,'term':terminoS.getId(),'zb':zb_en}
                        #print(egu_lag)
                        eguneratzekoak.append(egu_lag)
                        #lexentzat(ordList,gehitzeko,termLag)
                        
            else:
                try:
                    itzulpenak,apl_patroiak = TK.main(term)
                except Exception:
                    itzulpenak = set()
                if "" in itzulpenak:
                    itzulpenak.remove("")
                #print(itzulpenak,len(itzulpenak))
                if len(itzulpenak) >= 1:
                    #print("TK-tik jasotakoa",itzulpenak)
                    # lock.acquire()
                    # ordList = itzulDBeng.gehitu(itzulpenak,term,"Patroiak",terminoS.getUsageNote(),"TerminoKonplexu","",6,apl_patroiak)
                    # lock.release()
                    # engHash[term] = ordList
                    # konTBX.eguneratu(ordList,terminoS.term,ema,zb)
                    ord_lag = {'ordList':itzulpenak,'term':term,'entrySource':'Patroiak','caseSig':terminoS.getUsageNote(),'pOS':set(['TerminoKonplexu']),'tT':'','rC':6,'apl_patroiak':apl_patroiak}
                    #print(ord_lag)
                    ord_key = term+'-'+str(random.randrange(1,1000))
                    ord_hiztegia[ord_key]=ord_lag
                    egu_lag = {'konTBX':konId,'ordList':ord_key,'term':terminoS.getId(),'zb':zb_en}
                    #print(egu_lag)
                    eguneratzekoak.append(egu_lag)
                    ema.setTerminoa(term,'en','bai')
                    itzulia = True
                    #print('Patroiak',termLag,itzulpenak)
                    #lexentzat(ordList,gehitzeko,termLag)
        if not itzulia:
            ###HEMEN MATXINI DEITU BEHARKO NIOKE
            ema.setTerminoa(term,'en','ez')
        i += 1
        if i%1000 == 0:
            print(hie,i,'/',denera)
        #sys.stdout.write("\r%d / %d" %(i,denera))
        #sys.stdout.flush()
    gc.collect()
    #print()
    #lexenEguneratzea(gehitzeko,hie)
    #gc.collect()
    return eguneratzekoak,ord_hiztegia

def itzulpenaKudeatu(hie,tok_kop,i_min,i_max,path,emFitx,emaitzak,adj_hiz,kat_hiz):
    itzulDBeng = ItzulDB(path,0)
    engHash = itzulDBeng.toHash()
    itzulDBeng = ""
    #print("Ingelesezko ItzulDB kargatuta")
    itzulDBspa = ItzulDB(path,1)
    spaHash = itzulDBspa.toHash()
    itzulDBeng = ""
    #print("Gaztelaniazko ItzulDB kargatuta")
    snomed = Snomed(False,path)
    
    if tok_kop == i_min:
        ema = Emaitzak(hie)
        if i_min > 1:
            snomed.kargatu(hie,"_ald")
        else:
            snomed.kargatu(hie)
    else:
        ema = emaitzak[hie]
        snomed.kargatu(hie,'_ald')

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

    egun,ord_hiz = itzuli(snomed,ema,path,engHash,spaHash,kodeak_en,kodeak_es,tok_kop,adj_hiz,kat_hiz)
    print(colored(hie+' itzulpena bukatuta. Aldaketak gordetzen...',"magenta"))
    #snomed.gorde() #Ez da hemen gorde behar. euSnomed.py arduratuko da honetaz.
    ema.setKontzeptuakItzulita(snomed.getItzulitakoKontzeptuKop())
    ema.setOrdainakItzulita(snomed.getItzulitakoOrdainKop())
    ema.setTerminoakItzulita(snomed.getItzulitakoTerminoKop())
    #print('itzuli.py','egun',len(egun))
    return ema,egun,ord_hiz

def main(argv):
    print(argv,len(argv))
    hie = argv[0]
    tok_kop = int(argv[1])
    i_min = int(argv[2])
    i_max = int(argv[3])
    path = argv[4]
    emFitx = argv[5]
    emaitzak = pickle.load(open(argv[6],'rb'))
    adj_hiz = pickle.load(open(argv[7],"rb"))
    kat_hiz = pickle.load(open(argv[8],"rb"))
    tf_egun = open(argv[9],"wb")
    tf_ord_h = open(argv[10],'wb')
    tf_ema = open(argv[11],'wb')
    for i in [6,7,8]:
        os.remove(argv[i])
    ema,egun,ord_hiz = itzulpenaKudeatu(hie,tok_kop,i_min,i_max,path,emFitx,emaitzak,adj_hiz,kat_hiz)
    #egun,ord_hiz = itzuli(snomed,ema,path,itzulEnHash,itzulSpHash,kodeak_en,kodeak_es,tok_kop,adj_hiz,kat_hiz)

    pickle.dump(egun,tf_egun)
    pickle.dump(ord_hiz,tf_ord_h)
    pickle.dump(ema,tf_ema)
    tf_egun.close()
    tf_ord_h.close()
    tf_ema.close()
    
        

if __name__ == "__main__":
    main(sys.argv[1:])
