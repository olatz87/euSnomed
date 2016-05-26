#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys,getopt,codecs
import re,subprocess
from subprocess import Popen,PIPE
import nltk
from analizatzaileak import analizatzailea_en


def pluraleraPasa(term):
    if '+ReM' in term:
        term = term.replace('+ReM','+eM')
    elif '+ari' in term:
        term = term.replace('+ari','+ei')
    elif '+ri' in term:
        term = term.replace('+ri','+ei')
    elif '+areM' in term:
        term = term.replace('+areM','+eM')
    elif '+arekiM' in term:
        term = term.replace('+arekiM','+ekiM')
    elif '+Ean' in term:
        term = term.replace('+Ean','+etan')
    elif '+Eko' in term:
        term = term.replace('+Eko','+etako')
    elif '+ako' in term:
        term = term.replace('+ako','+etako')
    elif '+' in term:
        term = term.replace('+ako','+etako')
    elif '+agatikako' in term:
        term = term.replace('+agatikako','+engatikako')
    elif '+ak_eragindako' in term:
        term = term.replace('+ak_eragindako','+ek_eragindako')
    elif '+Erako' in term:
        term = term.replace('+Erako','+etarako')
    elif '+a' in term:
        term = term.replace('+a','+ak')
    return term

# def analisiakKargatu():
#     hiztegia = {}
#     with codecs.open('/ixadata/users/operezdevina001/Doktoretza/euSnomed/baliabideak/analisienHiztegia.txt',encoding='utf-8') as fitx:
#         for line in fitx:
#             line = line.strip()
#             jatorri,analisi = line.split(':\t')
#             hiztegia[jatorri.lower()] = analisi
#     return hiztegia

def itzulpenaPrestatu(term,analisia):
    p = subprocess.Popen(['flookup -a -i -x -b  scriptak/foma/kategorizazioaOrokortuta.fst'],stdin=PIPE,stdout=PIPE,shell=True,close_fds=True)
    returnword = p.communicate(input=term.encode('utf-8'))
    trans = returnword[0].decode('utf-8').strip()
    itzultzeko = []
    patroiak = set()
    plurala = ''
    pluB = False
    if trans == '+?':
        p = subprocess.Popen(['flookup -a -i -x -b scriptak/foma/kategorizazioaOrokortuta.fst'],stdin=PIPE,stdout=PIPE,shell=True,close_fds=True)
        lehenaMaius = term[0].upper()+term[1:]
        returnword = p.communicate(input=lehenaMaius.encode('utf-8'))
        trans = returnword[0].decode('utf-8').strip()
        if trans == '+?':
            #analisiak = analisiakKargatu()
            txurikin = term.replace('_',' ').strip().lower()
            #print(analisiak[txurikin])
            #if txurikin in analisiak:
                #analisia = analisiak[txurikin]
            formaLemak = {}
            formak = []
            for lag in analisia:
                forma,info = lag
                formaLemak[forma] = info["Lemma"]
                formak.append(forma)
            #formak = term.split()
            i = 0
            #print(formak)
            while i < len(formak) and trans == "+?":
                for1 = formak[i]
                #if "_" not in for1 and for1[-1] == 's':
                if  for1 and for1[-1] == 's':
                    termBerria = ''
                    if "_" not in for1:
                        if for1 in formaLemak and for1 != formaLemak[for1]:
                            termB = formak[:]
                            termB[i] = formaLemak[for1]
                            termBerria = " ".join(termB)
                            plurala = formaLemak[for1]
                    else:
                        forLag = for1.split('_')[-1]
                        if forLag in formaLemak and forLag != formaLemak[forLag]:
                            forB = '_'.join(for1.split('_')[:-1])+'_'+formaLemak[forLag]
                            termB = formak[:]
                            termB[i] = forB
                            termBerria = " ".join(termB)
                            plurala = forB
                            #print(termB)
                    if termBerria != '':
                        p = subprocess.Popen(['flookup -a -i -x -b  scriptak/foma/kategorizazioaOrokortuta.fst'],stdin=PIPE,stdout=PIPE,shell=True,close_fds=True)
                        returnword = p.communicate(input=termBerria.encode('utf-8'))
                        trans = returnword[0].decode('utf-8').strip()
                        if trans != "+?":
                            pluB = True
                            #print("PLURALA")
                i += 1
    if trans != "+?":
        etiketatuak = trans.split('\n')
        for etik in etiketatuak:
            if etik == "":
                continue
            #print(etik)
            jat = etik.split(" ")
            aplik_patroia = jat[-1]
            jat = jat[:-1]
            #print(aplik_patroia)
            #print(jat)
            if pluB:
                aurkitua = False
                j = 0
                #print(jat,len(jat),plurala)
                while not aurkitua and j < len(jat):
                    lag = jat[j].split('|')[0]
                    if lag == plurala:
                        aurkitua = True
                    else:
                        j += 1
                plu = jat[j]
                #print('plu:',plu,'jat:',jat)
                jat[j] = pluraleraPasa(plu)
                etik = " ".join(jat)
                #print(etik)
            if "&LehenaAzkenera" in etik:
                #print(jat)
                ordAld = jat[1:-1]
                ordAld.append(jat[0])
                itzultzeko.append(' '.join(ordAld))
                #print(ordAld)
            elif "&LehenaEtaAzkena" in etik:
                ordAld = jat[:-1]
                leh = jat[0]
                azk = jat[-1]
                ordAld[0] = azk
                ordAld[-1] = leh
                itzultzeko.append(' '.join(ordAld))
            else:
                itzultzeko.append(" ".join(jat))
            patroiak.add(aplik_patroia)
                #print("Tartekoak: "+" ".join(itzultzeko))
    #print(itzultzeko)
    return itzultzeko,patroiak

def jatorrizkoPluralaEbatzi(term):
    term = pluraleraPasa(term)
    term = term.replace("ak+",'')
    return term


def itzulpena(term,analisia):
    #print(term,analisia)
    itzultzeko,apl_patroiak = itzulpenaPrestatu(term,analisia)
    #print(itzultzeko)
    lag = set()    
    idatz = "" 
    for s in itzultzeko:
        p1 = subprocess.Popen(['flookup -i -x -b  scriptak/foma/itzulpena.fst'],stdin=PIPE,stdout=PIPE,shell=True)
        returnwords = p1.communicate(input=s.encode('utf8'))
        for itzul in returnwords[0].decode('utf8').split('\n'):
            #print(itzul)
            if itzul == "" or itzul == "+?":
                continue
            itzul = itzul.strip()
            if ("&&&ADJK" in itzul or "&&&IZLK" in itzul):
                if "&&&ADJK" in itzul and "ADJK+a+gatikako" not in itzul and "ADJK+ak_eragindako" not in itzul: #Izenondoak
                    jat = itzul.split(" ")
                    ordAld = []
                    i = 0
                    while i < len(jat) :
                        unekoa = jat[i]
                        if "&&&ADJK" in unekoa and i < len(jat)-1: 
                            hurrengoa = jat[i+1]
                            j = 0
                            if "&&&ADJK" in hurrengoa:
                                if i == len(jat)-2:
                                    ordAld.append(unekoa.replace("&&&ADJK",""))
                                    ordAld.append(hurrengoa.replace("&&&ADJK",""))
                                    j = 1
                                else:
                                    ordAld.append(jat[i+2])
                                    j = 1
                                    ordAld.append(hurrengoa.replace("&&&ADJK",""))
                                    ordAld.append(jat[i].replace("&&&ADJK",""))

                            elif "&&&IZLK" in hurrengoa:
                                ordAld.append(hurrengoa.replace("&&&IZLK",""))
                                ordAld.append(jat[i+2])
                                ordAld.append(jat[i].replace("&&&ADJK",""))
                                j = 1
                            else:
                                ordAld.append(hurrengoa)
                                ordAld.append(jat[i].replace("&&&ADJK",""))
                            i += 1 + j
                        else:
                            ordAld.append(jat[i].replace("&&&ADJK",""))
                        i += 1
                    itzul = " ".join(ordAld)
                else: #Izenlagunak
                    itzul = itzul.replace("&&&IZLK","")
                    itzul = itzul.replace("&&&ADJK","")
            plus = False
            eig = False
            if " + " in itzul:
                itzul = itzul.replace(' + ',' &&& ')
                plus = True
            itzTokenak = itzul.split(" ")
            for i in range (0,len(itzTokenak)):
                itzTok = itzTokenak[i]
                itzLag = itzTok.split('+')
                print(itzLag)
                itzLag[0] = itzLag[0].replace('E','&e&').replace('M','&m&').replace('R','&r&').replace('1','&bat&').replace('3','&hiru&').replace('4','&lau&').replace('/','&barra&').replace('\\','&kontrabarra&')
                itzTok = '+'.join(itzLag)
                if itzLag[0].endswith("ak"):
                    print("pluralean dago!!!")
                    itzTok = jatorrizkoPluralaEbatzi(itzTok)
                itzTokenak[i] = itzTok
            itzul = " ".join(itzTokenak)
            p2 = subprocess.Popen(['flookup -i -x -b  scriptak/foma/deklinabideak.fst'],stdin=PIPE,stdout=PIPE,shell=True)
            returnwords = p2.communicate(input=itzul.encode('utf8'))
            itzul1 = returnwords[0].decode('utf8').split('\n')[0]
            if plus:
                itzul1 = itzul1.replace(' &&& ',' + ')
            itzul1 = itzul1.replace('&e&','E').replace('&m&','M').replace('&r&','R').replace('&bat&','1').replace('&hiru&','3').replace('&lau&','4').replace('&barra&','/').replace('&kontrabarra&','\\')
            if itzul1 not in lag:
                lag.add(itzul1)
                if idatz == '':
                    idatz = itzul1.replace('_',' ')
                else:
                    idatz += ','+itzul1.replace('_',' ')
    return lag,apl_patroiak


def main(argv):
    try:
        opts, args = getopt.getopt(argv,"ht:",["terminoa="])
    except getopt.GetoptError:
        print('python3 terminoKonplexuaItzuli.py -t <terminoa> ' )
        sys.exit(2)
    for opt, arg in opts:
        if opt =='-h':
            print('python3 patroiakItzuli.py -o <outputdir> -i <inputfile>')
            sys.exit()
        elif opt in ("-t","--terminoa"):
            term = arg
    emaitza = set()
    ema_pat = set()
    term = term.strip()
    if not term:
        return emaitza
    analisia,multzoak = analizatzailea_en.analizatu(term,True,True)
    if analisia == None:
        return emaitza
    #print(analisia)
    #print(multzoak)
    mul_ord = {}
    for mulL in multzoak:
        el = mul_ord.get(len(mulL),[])
        el.append(mulL)
        mul_ord[len(mulL)] = el
    i_ord = sorted(mul_ord)
    i = 0
    aurkitua = False
    while not aurkitua and i < len(i_ord):
        mulLak = mul_ord[i_ord[i]]
        #print(mulLak)
        for mulL in mulLak:
            ema,ap_pat = itzulpena(' '.join(mulL),analisia)
            emaitza = emaitza.union(ema)
            ema_pat = ema_pat.union(ap_pat)
            #print(emaitza,ema_pat)
        if emaitza:
            aurkitua = True
        else:
            i += 1
    #print(emaitza)
    return emaitza,ema_pat
    #idatz = itzulpena(term)
    #print(idatz)

if __name__ == "__main__":
    #print(main(sys.argv[1:])[0])
    print(main(sys.argv[1:]))

