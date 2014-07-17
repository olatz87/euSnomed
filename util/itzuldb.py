#!/usr/bin/python3
# -*- coding: utf-8 -*-
from util.itzuldbordain import ItzulDBOrdain
from util.itzuldbtbx import ItzulDBTBX
import csv,re

class ItzulDB:

    def hashSet(self,hasha,key,value,itur,caseSig,pOs,termType,rC):
        key = key.strip().lower().encode('utf-8')
        if caseSig == 'Unknown':
            value = value.lower()
        elif caseSig == 'InitialInsensitive':
            value = value[0].lower()+value[1:]
        value = value.strip().encode('utf-8')
        ordainList = hasha.get(key,{})
        if itur == 'Elhuyar' and ordainList:
            elBerria = False
            for ket,ordain in ordainList.items():
                if 'Elhuyar' not in ordain.getHiztegiZerrenda():
                    return None
        ordainDat = ordainList.get(value,ItzulDBOrdain())
        ordainDat.gehituDatuak(itur,caseSig,pOs,termType,rC)
        ordainList[value]=ordainDat
        hasha[key]=ordainList

    def zt2hash(self,path,hizkuntza=2):
        ztEng = {}
        ztSpa = {}
        with open(path+'/baliabideak/ZTSnomed.txt') as ztFitx:
            for sarrera in ztFitx:
                sarrera = sarrera.strip()
                ordainak = sarrera.split('\t')
                if len(ordainak) == 3:
                    eus = ordainak[0]
                    pOS = set()
                    cS = 'InitialInsensitive'
                    tT = 'Unknown'
                    if eus[0].isupper():
                        cS = 'Sensitive'
                        pOS.add('IzenBerezi')
                        if eus.isupper():
                            tT = 'Acronym'
                    if ordainak[1] != '' and (hizkuntza == 0 or hizkuntza == 2):
                        engAk = ordainak[1].split(';')
                        for eng in engAk:
                            if '?' not in eng:
                                self.hashSet(ztEng,eng,eus,'ZT',cS,pOS,tT,9)
                    if hizkuntza >=1:
                        spaAk = ordainak[2].split(';')
                        for spaLag in spaAk:
                            spa = spaLag.split(', -')[0]
                            self.hashSet(ztSpa,spa,eus,'ZT',cS,pOS,tT,9)
#        print(ztEng,ztSpa)
        return ztEng,ztSpa
        
    def anatomia2hash(self,path,hizkuntza,engH,spaH):
        with open(path+'/baliabideak/anatomia_glos.tsv') as fitx:
            tsvin = csv.reader(fitx,delimiter='\t')
            for ordainak in tsvin:
                if ordainak[2] != '' and ordainak[3] != '':
                    eusak = re.split(', |; |\. ',ordainak[0])
                    engak = re.split(', |; |\. ',ordainak[3])
                    spaak = re.split(', |; |\. ',ordainak[2])
                    if (hizkuntza == 0 or hizkuntza == 2) and ordainak[3] != '' and '---' not in ordainak[3]:
                        for eng in engak:
                            if '?' not in eng:
                                for eus in eusak:
                                    cS = 'Unknown'
                                    pOS = set()
                                    tT = 'Unknown'
                                    self.hashSet(engH,eng,eus,'Anatomia',cS,pOS,tT,6)
                    if (hizkuntza >= 1) and ordainak[2] != '' and '---' not in ordainak[2]:
                        for spa in spaak:
                            if '?' not in spa:
                                for eus in eusak:
                                    cS = 'Unknown'
                                    pOS = set()
                                    tT = 'Unknown'
                                    self.hashSet(spaH,spa,eus,'Anatomia',cS,pOS,tT,6)
                                    
    def gns2hash(self,path,hizkuntza,engH,spaH):
        with open(path+'/baliabideak/gns10garbi6.txt') as fitx:
            tsvin = csv.reader(fitx,delimiter='\t')
            for ordainak in tsvin:
                ordainak.append('')
                eng = ordainak[1].strip()
                spa = ordainak[2].strip()
                eusak = ordainak[3].strip().split('; ')
                for eus in eusak:
                    cS = 'Unknown'
                    pOS = set()
                    tT = 'Unknown'
                    if (hizkuntza == 0 or hizkuntza == 2) and eng and eus:
                        self.hashSet(engH,eng,eus,'GNS10',cS,pOS,tT,5)
                    if hizkuntza >= 1 and spa and eus:
                        self.hashSet(spaH,spa,eus,'GNS10',cS,pOS,tT,5)

    def erizaintza2hash(self,path,hizkuntza,engH,spaH):
        if hizkuntza == 0:
            hasha = engH
            fitx = path+'/baliabideak/erizaintza_en-eu.txt'
        else:
            hasha = spaH
            fitx = path+'/baliabideak/erizaintza_es-eu.txt'
        with open(fitx) as fit:
            for sarrera in fit:
                if ':' in sarrera:
                    bana = sarrera.split(':')
                    terminoa = re.split('(, -a)|(,-a)',bana[0].strip())[0]
                    ordainak = bana[1].split(',')
                    if ',' not in terminoa:
                        for orda in ordainak:
                            eus = orda.strip()
                            cS = 'Unknown'
                            pOS = set()
                            tT = 'Unknown'
                            if eus.isupper():
                                tT = 'Acronym'
                                pOS.add('IzenBerezi')
                                cS = 'Sensitive'
                            else:
                                eus = eus.lower()
                            self.hashSet(hasha,terminoa,eus,'Erizaintza',cS,pOS,tT,7)
                            
    def euskalterm2hash(self,path,hizkuntza,engH,spaH):
        fitx = path+'/baliabideak/euskaltermOsoa2_utf8.txt'
        with open(fitx) as fit:
            tsvin = csv.reader(fit,delimiter='\t')
            for sarrera in tsvin:
                gaztelaniazkoak = sarrera[0].strip()
                euskarazkoak = sarrera[1].strip()
                ingelesezkoak = sarrera[2].strip()
                pattern = "Administrazio sanitarioa|Anfibioen izenak|Arnas aparatua|Arrainen izenak|Alderdi biologikoa|Biokimika|Biologia|Botanika|Digestio-aparatua|Ekologia|Fisika|Genetika|Hematologia|Kimika|Laborategia|Landareen izenak|Magnetismoa|Medikuntza|Mikrobiologia|Narrastien izenak|Oftalmologia|Oinarrizko partikulak|Oinarrisko psikologia|Optika|Ornogabeen izenak|Otorrinolaringologia|Pediatria|Psikobiologia|Psikologia|Sistema genitourinarioa|Termodinamika|Traumatologia|Ugaztunen izenak|Zirkulazio-aparatua|Zitologia|Zoologia"
                if euskarazkoak and re.search(pattern,sarrera[4]):
                    regex = re.compile('\(.+?\)')
                    #eusak = regex.sub('',euskarazkoak).split('\\')
                    #spaak = regex.sub('',gaztelaniazkoak).split('\\')
                    #engak = regex.sub('',ingelesezkoak).split('\\')
                    eusak = euskarazkoak.split('\\')
                    spaak = gaztelaniazkoak.split('\\')
                    engak = ingelesezkoak.split('\\')
                    if engak[0] != '':
                        for eng in engak:
                            pos = set()
                            if '(v.)' in eng:
                                pos.add('Aditz')
                            elif '(izond.)' in eng:
                                pos.add('Aditzondo')
                            elif '(adj.)' in eng:
                                pos.add('Adjektibo')
                            elif '(n.)' in eng or '(iz.)' in eng:
                                pos.add('Izen')
                            eng = regex.sub('',eng)
                            for eus in eusak:
                                if '(v.)' in eus or '(ad.)' in eus:
                                    pos.add('Aditz')
                                elif '(izond.)' in eus:
                                    pos.add('Aditzondo')
                                elif '(adj.)' in eus:
                                    pos.add('Adjektibo')
                                elif '(n.)' in eus or '(iz.)' in eus:
                                    pos.add('Izen')
                                eus = regex.sub('',eus)
                                cS = 'InitialInsensitive'
                                tT = 'Unknown'
                                if eus[0].isupper():
                                    cS ='Sensitive'
                                    pos.add('IzenBerezi')
                                    if eus.isupper():
                                        tT = 'Acronym'
                                self.hashSet(engH,eng,eus,'EuskalTerm',cS,pos,tT,8)
                    if spaak[0] != '':
                        for spa in spaak:
                            pos = set()
                            if '(v.)' in spa:
                                pos.add('Aditz')
                            elif '(izond.)' in spa:
                                pos.add('Aditzondo')
                            elif '(adj.)' in spa:
                                pos.add('Adjektibo')
                            elif '(n.)' in spa or '(iz.)' in spa:
                                pos.add('Izen')
                            spa = regex.sub('',spa)
                            for eus in eusak:
                                if '(v.)' in eus or '(ad.)' in eus:
                                    pos.add('Aditz')
                                elif '(izond.)' in eus:
                                    pos.add('Aditzondo')
                                elif '(adj.)' in eus:
                                    pos.add('Adjektibo')
                                elif '(n.)' in eus or '(iz.)' in eus:
                                    pos.add('Izen')
                                eus = regex.sub('',eus)
                                cS = 'InitialInsensitive'
                                tT = 'Unknown'
                                if eus[0].isupper():
                                    cS ='Sensitive'
                                    pos.add('IzenBerezi')
                                    if eus.isupper():
                                        tT = 'Acronym'
                                self.hashSet(spaH,spa,eus,'EuskalTerm',cS,pos,tT,8)

    def elhuyar2hash(self,path,hizkuntza,engH,spaH):
        if hizkuntza == 0 or hizkuntza == 2: #ingelesa
            with open(path+'baliabideak/HN_N_bakuna_opentrad_utf8.txt') as fitx:
                for sarrera in fitx:
                    sar = sarrera.split('\t')
                    if len(sar) == 3:
                        engLag = sar[0]
                        if " {to}" in engLag:
                            engLag = engLag.replace(' {to}','')
                        engak = engLag.split(';')
                        for eng in engak:
                            eusak = re.split(',|;',sar[2][:-2])
                            for eus in eusak:
                                if '/' in eus:
                                    continue
                                if '<I>' in eus:
                                    regex1 = re.compile('\[<I>[a-z ]+<I>\]')
                                    regex2 = re.compile('\(<I>[a-z ]+<I>\)')
                                    eus = regex1.sub('',eus)
                                    eus = regex2.sub('',eus)
                                elif '[' in eus:
                                    regex = re.compile('\[.+?\]')
                                    eus = regex.sub('',eus)
                                pos = set()
                                if eus[0].isupper():
                                    cS ='Sensitive'
                                    pos.add('IzenBerezi')
                                    if eus.isupper():
                                        tT = 'Acronym'
                                    else:
                                        tT = 'Unknown'
                                else:
                                    cS = 'InitialInsensitive'
                                    tT = 'Unknown'
                                if len(eus.split())>2:
                                    tT = 'SetPhase'
                                if sar[1] and sar[1][0] == 'v':
                                    pos.add('Aditz')
                                if 'adj.' in sar[1]:
                                    pos.add('Adjektibo')
                                if 'n.' in sar[1] and 'IzenBerezi' not in pos:
                                    pos.add('Izen')
                                if 'adv.' in sar[1]:
                                    pos.add('Aditzondo')
                                if not pos:
                                    pos.add('Besterik')
                                self.hashSet(engH,eng,eus,'Elhuyar',cS,pos,tT,7)
        if hizkuntza > 1:#gaztelania
            with open(path+'baliabideak/Elhuyar_es_eu-utf8.txt') as fitx:
                for sarrera in fitx:
                    sar = sarrera.split('\t')
                    spaLag = sar[0]
                    if '{' in spaLag:
                        continue
                    spaak = spaLag.split(';')
                    if len(sar) >= 4:
                        for spa in spaak:
                            spa = spa.split(', -')[0]
                            if spa[:2] == '1 ' or spa[:2] == '2 ' or spa[:2] == '3 ' or spa[:2] == '4 ':
                                spa = spa[2:]
                            
                            eusak = re.split(',|;',sar[3])
                            for eus in eusak:
                                eus = eus.strip()
                                if not eus or '/' in eus:
                                    continue
                                if '<I>' in eus:
                                    regex1 = re.compile('\[<I>[a-z ]+<I>\]')
                                    regex2 = re.compile('\(<I>[a-z ]+<I>\)')
                                    eus = regex1.sub('',eus)
                                    eus = regex2.sub('',eus)
                                elif '[' in eus:
                                    regex = re.compile('\[.+?\]')
                                    eus = regex.sub('',eus)
                                pos = set()
                                if eus[0].isupper():
                                    cS ='Sensitive'
                                    pos.add('IzenBerezi')
                                    if eus.isupper():
                                        tT = 'Acronym'
                                    else:
                                        tT = 'Unknown'
                                else:
                                    cS = 'InitialInsensitive'
                                    tT = 'Unknown'
                                if len(eus.split())>2:
                                    tT = 'SetPhase'
                                if sar[1] and sar[1][0] == 'v':
                                    pos.add('Aditz')
                                if 'adj.' in sar[1]:
                                    pos.add('Adjektibo')
                                if 's.' in sar[1] and 'IzenBerezi' not in pos:
                                    pos.add('Izen')
                                if 'adv.' in sar[1]:
                                    pos.add('Aditzondo')
                                if not pos:
                                    pos.add('Besterik')
                                self.hashSet(spaH,spa,eus,'Elhuyar',cS,pos,tT,7)

                            
                        
    def adminSan2hash(self,path,spaH):
        with open(path+'baliabideak/adm_san.txt') as fitx:
            while True:
                spa = fitx.readline().strip()
                if not spa: break
                fitx.readline()
                eusLag = fitx.readline().strip().split(' / ')
                fitx.readline()
                if '/a' in spa:
                    spa = spa.replace('/as','').replace('/a','')
                regex = re.compile('\(.+?\)')
                for eus in eusLag:
                    pos = set()
                    if eus[0].isupper():
                        cS = 'Sensitive'
                        pos.add('IzenBerezi')
                        if eus.isupper():
                            tT = 'Acronym'
                        else:
                            tT = 'Unknown'
                    else:
                        cS = 'InitialInsensitive'
                        tT = 'Unknown'
                    if '(adj.)' in spa or '(adj.)' in eus:
                        pos.add('Adjektibo')
                    if '(sust.)' in spa or '(sust.)' in eus or '(iz.)' in spa or '(iz.)' in eus:
                        pos.add('Izen')
                    if '(v.)' in spa or '(v.)' in eus:
                        pos.add('Aditz')
                    if '(' in spa:
                        spa = regex.sub('',spa)
                    if '(' in eus:
                        eus = regex.sub('',eus)
                    self.hashSet(spaH,spa,eus,'AdminSan',cS,pos,tT,8)

    def hasieratu(self,path,hizkuntza):
        engH,spaH = self.zt2hash(path,hizkuntza)
        print('ZT',len(engH),len(spaH))
        self.anatomia2hash(path,hizkuntza,engH,spaH)
        print('+Anatomia',len(engH),len(spaH))
        self.gns2hash(path,hizkuntza,engH,spaH)
        print('+GNS10',len(engH),len(spaH))
        self.euskalterm2hash(path,hizkuntza,engH,spaH)
        print('+Euskalterm',len(engH),len(spaH))
        if hizkuntza ==2:
            self.erizaintza2hash(path,0,engH,spaH)
            self.erizaintza2hash(path,1,engH,spaH)
            print('+Erizaintza',len(engH),len(spaH))
        else:
            self.erizaintza2hash(path,hizkuntza,engH,spaH)
            print('+Erizaintza',len(engH),len(spaH))
        if hizkuntza >= 1:
            self.adminSan2hash(path,spaH)
            print('+AdminSan',len(engH),len(spaH))
        self.elhuyar2hash(path,hizkuntza,engH,spaH)
        print('+Elhuyar',len(engH),len(spaH))
        return engH,spaH
    
    def __init__(self,path,hizkuntza,itzulBool=False):
        if itzulBool:
            engH,spaH = self.hasieratu(path,hizkuntza)
            if hizkuntza == 0 or hizkuntza == 2:
                itzTBX = ItzulDBTBX(0,path)
                itzTBX.xmltanElkartu(engH)
            if hizkuntza >= 1:
                itzTBX = ItzulDBTBX(1,path)
                itzTBX.xmltanElkartu(spaH)
        else:
            self.itzTBX = ItzulDBTBX(hizkuntza,path)
            self.itzTBX.kargatu()

        
    def jaso(self,terminoa):
        return self.itzTBX.jaso(terminoa)

    def gehitu(self,ordList,term,entrySource,caseSig,pOS,tT,rC):
        return self.itzTBX.gehituParea(term,ordList,entrySource,caseSig,pOS,tT,rC)


    def fitxategianGorde(self):
        self.itzTBX.fitxategianGorde()
