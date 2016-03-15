#!/soft_orokorra_linux_x86_64/python-3.4.2/bin/python3
# -*- coding: utf-8 -*-

import sys,os,getopt,datetime,codecs,threading,subprocess,gc,pickle,tempfile,argparse
from util.itzuldb import ItzulDB
from util.enumeratuak import Hierarkia,Hierarkia_RF2,Hierarkia_RF2_probak,Hierarkia_RF2_izen
from util.emaitzak import Emaitzak
from util.snomed import Snomed
# from util.terminotbxsnomed import TerminoTBXSnomed
from util.kontzeptutbx import KontzeptuTBX
# from util.snomedtbx import SnomedTBX
from util.ordaintbxitzuldb import OrdainTBXItzulDB
# import scriptak.morfosemantika as MS
# import scriptak.pharma_itzuli as PI
# import scriptak.terminoKonplexuaItzuli as TK
#import multiprocessing as mp
from multiprocessing.pool import ThreadPool
from multiprocessing import Pool, Lock
from termcolor import colored
from copy import deepcopy
#from analizatzaileak import analizatzailea_en
#from subprocess import Popen,PIPE
from lxml import etree as ET


def lexenEguneratzea(gehitzeko,hie,tok_kop):
    print("Lex-ak eguneratuko dira",hie.lower(),len(gehitzeko))
    if len(gehitzeko)>0:
        flex_ize = "scriptak/foma/lex/"+hie.lower()+'.lex'
        with codecs.open(flex_ize,encoding="utf-8") as flex:
            fList = flex.readlines()[:-1]
            for eng,eusak in gehitzeko.items():
                for ordT in eusak:
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


def lexentzat(ordList,gehitzeko,termLag):
    for ordL in ordList:
        ordT = OrdainTBXItzulDB(ordL)
        if termLag in gehitzeko:
            gehitzeko[termLag].add(ordT)
        else:
            gehitzeko[termLag] = {ordT}


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
    #print(hie,'egun',egun)
    #print(hie,'ord',ord_h)
    #print(hie,'ema',ema)
    tf_egun.close()
    tf_ord_h.close()
    tf_ema.close()

    snomed = Snomed(False,path)
    if tok_kop == i_min:
        if i_min > 1:
            snomed.kargatu(hie,"_ald")
        else:
            snomed.kargatu(hie)
    else:
        snomed.kargatu(hie,'_ald')

    gehitzeko = {}
    for eg in egun:
        ordList = eg['ordList']
        termS = snomed.getTerminoTBX(eg["term"]) #TerminoTBXSnomedo objektua itzultzen du
        term = termS.getTerminoa()
        if type(ordList) == type('kuku'):
            ord_lag = ord_h[ordList]
            ap = ''
            if "apl_patroiak" in ord_lag:
                ap = ord_lag["apl_patroiak"]
            lock.acquire()
            ordList = itzulDBeng.gehitu(ord_lag['ordList'],term,ord_lag['entrySource'],ord_lag['caseSig'],ord_lag['pOS'],ord_lag['tT'],ord_lag['rC'],ap)
            itzulEnHash[term] = ordList
            lock.release()
        elif type(ordList) == type(1):
            lock.acquire()
            if ordList == 0:
                ordList = itzulEnHash.get(term.lower())
            else:
                ordList = itzulSpHash.get(term.lower())
            lock.release()
        else:
            print(ordList)
        konTBX = snomed.getKontzeptuTBX(eg["konTBX"][1:])
        if not konTBX:
            print("EZ DAKIT ZER GERTATZEN DEN!!",hie,eg)

        konTBX.eguneratu(ordList,termS.term,eg['ema'],eg['zb']) #termS.term erabili behar da, kontutan izan nTig objektua bera berreskuratu nahi dugula
        if ordList != 1:
            lexentzat(ordList,gehitzeko,term.replace(' ','_'))

    lexenEguneratzea(gehitzeko,hie,tok_kop)
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
    snoBool = args.snomed # False
    itzulBool = args.itzuldb # False
    lexBool = args.lex #False
    # try:
    #     opts, args = getopt.getopt(argv,"hp:s:i:l",["path=","snomed=","itzuldb=","lex"])
    # except getopt.GetoptError:
    #     print('python3 euSnomed.py -p <path> -s <snomedBool> -i <itzulDBBool>')
    #     sys.exit(2)
    # for opt, arg in opts:
    #     if opt =='-h':
    #         print('python3 euSnomed.py -p <path> -s -i -l ')
    #         sys.exit()
    #     elif opt in ("-p","--path"):
    #         path = arg
    #     elif opt in ("-i","--itzuldb"):
    #         itzulBool = True
    #     elif opt in ('-s','--snomed'):
    #         snoBool = True
    #     elif opt in ('-l','--lex'):
    #         lexBool = True
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
    i_max = 10
    #i_max = 4
    pat_app = {}
    pool = ThreadPool(processes=6)
    lock = Lock()
    for tok_kop in range(i_min,i_max): #Kontuz!!! i_min inkrementatu dut!!!
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
        #results = [pool.apply_async(itzulpenaKudeatu,args=(hie,tok_kop,i_min,i_max,path,deepcopy(snomed),itzulDBeng,itzulEnHash,itzulSpHash,emFitx,emaitzak,lock,adj_hiz,kat_hiz)) for hie in Hierarkia_RF2_izen ]#Hierarkia_RF2_izen//probak
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
    #itzulDBspa.fitxategianGorde()
    #with open(emFitx) as fem:

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="deskribapenak.tsv fitxategietatik taulak ateratzeko.")
    parser.add_argument('-p',"--path",help="baliabideen patha",required = True)
    parser.add_argument('-i','--itzuldb',help="itzuldb hasieratu",action="store_true")
    parser.add_argument('-s','--snomed',help="snomed hasieratu",action="store_true")
    parser.add_argument('-l','--lex',help="lexak hasieratu",action="store_true")
    args = parser.parse_args()
    main(args)

