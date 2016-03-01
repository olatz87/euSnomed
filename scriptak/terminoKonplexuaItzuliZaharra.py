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
    elif '+a+ri' in term:
        term = term.replace('+a+ri','+ei')
    return term

def itzulpenaPrestatu(term,analisia):
    p = subprocess.Popen(['flookup -i -x -b scriptak/foma/kategorizazioaPatroiaGabe.fst'],stdin=PIPE,stdout=PIPE,shell=True,close_fds=True)
    returnword = p.communicate(input=term.encode('utf-8'))
    trans = returnword[0].decode('utf-8').strip()
    itzultzeko = []
    plurala = ''
    pluB = False
    if trans == '+?':
        p = subprocess.Popen(['flookup -i -x -b scriptak/foma/kategorizazioaPatroiaGabe.fst'],stdin=PIPE,stdout=PIPE,shell=True,close_fds=True)
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
                        p = subprocess.Popen(['flookup -i -x -b scriptak/foma/kategorizazioaPatroiaGabe.fst'],stdin=PIPE,stdout=PIPE,shell=True,close_fds=True)
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
            if pluB:
                jat = etik.split(" ")
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
                jat = etik.split(' ')[:-1]
                ordAld = jat[1:]
                ordAld.append(jat[0])
                itzultzeko.append(' '.join(ordAld))
            elif "&LehenaEtaAzkena" in etik:
                jat = etik.split(' ')[:-1]
                ordAld = jat[:]
                leh = jat[0]
                azk = jat[-1]
                ordAld[0] = azk
                ordAld[-1] = leh
                itzultzeko.append(' '.join(ordAld))
            else:
                itzultzeko.append(etik)
                #print("Tartekoak: "+" ".join(itzultzeko))
    #print(itzultzeko)
    return itzultzeko


def itzulpena(term,analisia):
    #print(term,analisia)
    itzultzeko = itzulpenaPrestatu(term,analisia)
    #print(itzultzeko)
    lag = set()    
    idatz = "" 
    for s in itzultzeko:
        p1 = subprocess.Popen(['flookup -i -x -b scriptak/foma/itzulpena.fst'],stdin=PIPE,stdout=PIPE,shell=True)
        returnwords = p1.communicate(input=s.encode('utf8'))
        for itzul in returnwords[0].decode('utf8').split('\n'):
            #print(itzul)
            if itzul == "" :
                continue
            itzul = itzul.strip()
            plus = False
            eig = False
            if " + " in itzul:
                itzul = itzul.replace(' + ',' &&& ')
                plus = True
            itzLag = itzul.split('+')
            itzLag[0] = itzLag[0].replace('E','&e&').replace('M','&m&').replace('R','&r&').replace('1','&bat&').replace('3','&hiru&').replace('4','&lau&').replace('/','&barra&').replace('\\','&kontrabarra&')
            itzul = '+'.join(itzLag)
            p2 = subprocess.Popen(['flookup -i -x -b scriptak/foma/deklinabideak.fst'],stdin=PIPE,stdout=PIPE,shell=True)
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
    return lag


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
    term = term.strip()
    if not term:
        return emaitza
    analisia,multzoak = analizatzailea_en.analizatu(term,True,True)
    if analisia == None:
        return emaitza
    for mulL in multzoak:
        emaitza = emaitza.union(itzulpena(' '.join(mulL),analisia))
    return emaitza

if __name__ == "__main__":
    print(main(sys.argv[1:]))

