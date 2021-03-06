#!/soft_orokorra_linux_x86_64/python-3.4.2/bin/python3
# -*- coding: utf-8 -*-

import sys,os,getopt,datetime,codecs,threading,subprocess,gc,pickle,tempfile,argparse
from util.itzuldb import ItzulDB
from util.enumeratuak import Hierarkia,Hierarkia_RF2,Hierarkia_RF2_probak,Hierarkia_RF2_izen
from util.emaitzak import Emaitzak
from util.snomed import Snomed
from util.kontzeptutbx import KontzeptuTBX
from util.ordaintbxitzuldb import OrdainTBXItzulDB
from multiprocessing.pool import ThreadPool
from multiprocessing import Pool, Lock
from termcolor import colored
from copy import deepcopy
from subprocess import Popen,PIPE
from lxml import etree as ET


def rcHandienekoak(eusak,kop):
    eus_ord = sorted(eusak, key = lambda k: (-float(k.getReliabilityCode()),k.getKarKatea().count(" ")))
    return eus_ord[:kop]

def lexenEguneratzea(gehitzeko,hie,tok_kop):
    print("Lex-ak eguneratuko dira",hie.lower(),len(gehitzeko))
    if len(gehitzeko)>0:
        flex_ize = "scriptak/foma/lex/"+hie.lower()+'.lex'
        with open(flex_ize,"rb") as flex:
            fList = flex.readlines()[:-1]
            for eng,eusak in gehitzeko.items():
                i = 0
                #eusak = rcHandienekoak(eusak,4)
                for ordT in eusak:
                    i += 1
                    eus = ordT.getKarKatea()
                    if eus[-1] == ";":
                        eus = eus[:-1]
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
                    if hie != "QUALIFIER":
                        if "Izen" in pos:
                            posE = "Izen"
                        else:
                            posE = posL
                        
                    #if tok_kop == 1 and posE == "Izenondo":# eus in adj_hiz:
                    if posE == "Izenondo":# eus in adj_hiz:
                        #print(eus,adj_hiz[eus])
                        eus += "&&&ADJK"#+adj_hiz[eus].strip()
                        #elif tok_kop == 1 and posE == "Izenlagun":
                    elif posE == "Izenlagun":
                        eus += "&&&IZLK"#+adj_hiz[eus].strip()
                    elif posE == "Adjektibo":
                        #elif tok_kop == 1 and posE == "Adjektibo":
                        if len(eus)>3 and eus[-3:] == "ren":
                            eus += "&&&IZLK"#+adj_hiz[eus].strip()
                        elif len(eus)>3 and eus[-3] != "i" and eus[-2:] in ["ko","go"]:
                            eus += "&&&IZLK"
                        else:
                            eus += "&&&ADJK"
                        
                    lagStr = eng+':'+eus.replace(' ','_')+' #;\n'
                    lagStr = lagStr.replace("%","%%").replace("<","%<").replace(">","%>")
                    if lagStr.encode('utf-8') not in fList:
                        fList.append(lagStr.encode('utf-8'))
            fList.append(b'END\n')
        with codecs.open(flex_ize,'w',encoding='utf-8') as fout:
            lag = b''.join(fList)
            fout.write(lag.decode('utf-8'))


def lexentzat(ordList,gehitzeko,termLag,zb):
    zerrendaBeltza = zb.get(termLag.lower(),[])
    termLag = termLag.replace(" ","_")
    for ordL in ordList:
        ordT = OrdainTBXItzulDB(ordL)
        if ordT.getKarKatea() in zerrendaBeltza:
            continue
        if termLag in gehitzeko:
            gehitzeko[termLag].add(ordT)
        else:
            gehitzeko[termLag] = {ordT}

def pluralaGehitu(hitza):
    p2 = subprocess.Popen(['flookup -i -x -b  scriptak/foma/deklinabideak.fst'],stdin=PIPE,stdout=PIPE,shell=True)
    hitza += "+ak"
    returnwords = p2.communicate(input=hitza.encode('utf8'))
    plurala = returnwords[0].decode('utf8').split('\n')[0]
    #print(hitza,plurala)
    return plurala

def generoaEbatzi(term,hasha):
    lag = term[:-1]+"o"
    return hasha.get(lag,None)


def pluralaEbatzi(term,hasha,hiz,zb):
    lag = term[:-1]
    ordList = None
    #print("pluralaEbatzi",term)
    if lag in hasha:
        ordList = deepcopy(hasha[lag])
        zerrendaBeltza = zb.get(lag.lower(),[])
    else:
        if lag[-1] == "e":
            lag2 = lag[:-1]
            ordList = deepcopy(hasha.get(lag2,None))
            zerrendaBeltza = zb.get(lag2.lower(),[])
        elif lag[-1] == "a" and hiz == "es":
            lag2 = term[:-1]+"o"
            ordList = deepcopy(hasha.get(lag2,None))
            zerrendaBeltza = zb.get(lag2.lower(),[])
    if ordList:
        for ordL in ordList:
            ordainI = OrdainTBXItzulDB(ordL)
            if "Izen" not in ordainI.getPOSzerrenda(): # Ez da string bat, zerrenda bat baizik!!!
                ordList.remove(ordL) #Plurala izateko, izena izan behar da. Gainerako ordainak ezabatu zerrendatik.
                continue
            ordT = ordL.find('term')
            if ordT.text in zerrendaBeltza:
                ordList.remove(ordL) #Singularra zerrenda beltzean badago, ezabatu.
                continue
            plurala = pluralaGehitu(ordT.text)
            ordT.text = plurala
    return ordList



#@profile
def itzulpenaKudeatu(hie,tok_kop,i_min,i_max,path,itzulDBeng,emFitx,emaitzak,adj_hiz,kat_hiz,itzulEnHash,itzulSpHash,lock):
    tf_emaitzak = tempfile.NamedTemporaryFile(delete=False)
    pickle.dump(emaitzak,tf_emaitzak)
    tf_adj_hiz = tempfile.NamedTemporaryFile(delete=False)
    pickle.dump(adj_hiz,tf_adj_hiz)
    tf_kat_hiz = tempfile.NamedTemporaryFile(delete=False)    
    pickle.dump(kat_hiz,tf_kat_hiz)
    tf_egun = tempfile.NamedTemporaryFile(delete=False)
    tf_ord_h = tempfile.NamedTemporaryFile(delete=False)
    tf_ema = tempfile.NamedTemporaryFile(delete=False)
    tf_emaitzak.close()
    tf_adj_hiz.close()
    tf_kat_hiz.close()
    p = subprocess.call('python3 itzuli.py '+hie+' '+str(tok_kop)+" "+str(i_min)+" "+str(i_max)+' '+path+' '+emFitx+' '+tf_emaitzak.name+' '+tf_adj_hiz.name+' '+tf_kat_hiz.name+' '+tf_egun.name+' '+tf_ord_h.name+' '+tf_ema.name,shell=True)
    egun = pickle.load(tf_egun)
    ord_h = pickle.load(tf_ord_h)
    ema = pickle.load(tf_ema)
    # print(hie,'egun',egun)
    # print(hie,'ord',ord_h)
    # print(hie,'ema',ema)
    tf_egun.close()
    tf_ord_h.close()
    tf_ema.close()

    snomed = Snomed(False,path)
    if tok_kop == i_min:
        if i_min > 1:
            snomed.kargatu(hie,"_ald")
        else:
            snomed.kargatu(hie)
            if hie in ['SITUATION','EVENT',"FINDING",'DISORDER']:
                snomed.mapGNS(ema)
    else:
        snomed.kargatu(hie,'_ald')
    print(colored(hie+' gehitzeko prest '+str(len(egun)),"red"))
    gehitzeko = {}
    for eg in egun:
        #print(eg)
        ordList = eg['ordList']
        termS = snomed.getTerminoTBX(eg["term"]) #TerminoTBXSnomedo objektua itzultzen du
        term = termS.getTerminoa()
        # if term.lower() == "abdominal aorta":
        #     print("abdominal aorta egun-en, ordlist aztertzen")
        #     print(ordList)
        if type(ordList) == type('kuku'):
            ord_lag = ord_h[ordList]
            #print("Ordain berria da")
            #print(1,term,ord_lag['ordList'],ord_lag['entrySource'])
            ap = ''
            if "apl_patroiak" in ord_lag:
                ap = ord_lag["apl_patroiak"]
            lock.acquire()
            ordList = itzulDBeng.gehitu(ord_lag['ordList'],term,ord_lag['entrySource'],ord_lag['caseSig'],ord_lag['pOS'],ord_lag['tT'],ord_lag['rC'],ap)
            #print(2,ordList)
            itzulEnHash[term] = ordList
            lock.release()
        elif type(ordList) == type(1):
            #print("Ordaina ItzulDB-tik hartu da",term)
            if termS.getUsageNote() == "InitialInsensitive":
                term = term[0].lower()+term[1:]
            elif termS.getUsageNote() == "Insensitive":
                term = term.lower()
            #lock.acquire()
            if ordList == 0: #Ingelesetik jasotako ordaina(k)
                ordList = itzulEnHash.get(term.lower())
                if ordList == None:
                    #plurala
                    if term.endswith("s"):
                        ordList = pluralaEbatzi(term.lower(),itzulEnHash,"en",eg["zb"])
            else: #Gaztelaniatik jasotako ordaina(k)
                ordList = itzulSpHash.get(term.lower())
                if ordList == None:
                    #plurala eta generoa
                    if term.endswith("s"):
                        ordList = pluralaEbatzi(term.lower(),itzulSpHash,"es",eg["zb"])
                    elif term.endswith("a"):
                        ordList = generoaEbatzi(term.lower(),itzulSpHash)
                

            #lock.release()
        else:
            print(ordList)
        konTBX = snomed.getKontzeptuTBX(eg["konTBX"][1:])
        if not konTBX:
            print("EZ DAKIT ZER GERTATZEN DEN!!",hie,eg)
        konTBX.eguneratu(ordList,termS.term,ema,eg['zb']) #termS.term erabili behar da, kontutan izan nTig objektua bera berreskuratu nahi dugula
        #print("lexentzat if-aren aurretik",term,termS.getHizkuntza())
        if ordList != 1 and termS.getHizkuntza() == "en":
            #print("lexentzat if-ean",term)
            lexentzat(ordList,gehitzeko,term,eg['zb'])
    print(colored(hie+' gehituta',"red"))

    lexenEguneratzea(gehitzeko,hie,tok_kop)
    snomed.gorde()
    snomed = None
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


#@profile
def main(args):
    path = args.path #'../../euSnomed/'
    snoBool = args.snomed
    itzulBool = args.itzuldb
    lexBool = args.lex
    hizkuntza = 2

    snomed = Snomed(snoBool,path)
    if itzulBool:
        itLag = ItzulDB(path,hizkuntza,itzulBool)
        itLag = None
    itzulDBeng = ItzulDB(path,0)#en
    itzulEnHash = itzulDBeng.toHash()
    #print(itzulEnHash[list(itzulEnHash)[0]])
    # for ordL in itzulEnHash["evening"]:
    #     print(ET.tounicode(ordL,pretty_print=True))
    #print('Ingelesezko ItzulDB kargatuta')
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
    i_min = 1
    i_max = 9
    #i_max = 52
    pat_app = {}
    pool = ThreadPool(processes=3)
    lock = Lock()
    for tok_kop in range(i_min,i_max):
        print("Itzulpena hasiko da: "+str(tok_kop)+" tokenetarako")  
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
        #results = [pool.apply_async(itzulpenaKudeatu,args=(hie,tok_kop,i_min,i_max,path,deepcopy(snomed),itzulDBeng,itzulEnHash,itzulSpHash,emFitx,emaitzak,lock,adj_hiz,kat_hiz)) for hie in Hierarkia_RF2_probak ]#Hierarkia_RF2_izen//probak
        results = [pool.apply_async(itzulpenaKudeatu,args=(hie,tok_kop,i_min,i_max,path,itzulDBeng,emFitx,emaitzak,adj_hiz,kat_hiz,itzulEnHash,itzulSpHash,lock)) for hie in Hierarkia_RF2_izen ]#Hierarkia_RF2_izen//probak
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SNOMED CT euskaratzeko aplikazioa.")
    parser.add_argument('-p',"--path",help="baliabideen patha",required = True)
    parser.add_argument('-i','--itzuldb',help="itzuldb hasieratu",action="store_true")
    parser.add_argument('-s','--snomed',help="snomed hasieratu",action="store_true")
    parser.add_argument('-l','--lex',help="lexak hasieratu",action="store_true")
    args = parser.parse_args()
    main(args)

