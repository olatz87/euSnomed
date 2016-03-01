#!/usr/bin/python3
# -*- coding: utf-8 -*-
from util.itzuldbordain import ItzulDBOrdain
from util.itzuldbtbx import ItzulDBTBX
import csv,re,codecs
from lxml import etree as ET

class ItzulDB:
    
    def edbl2enum(self,kat,azpkat):
        pOs = set()
        if kat == "IZE":
            if azpKat[:3] == "LIB" or azpKat[:2] == "IB" :
                pOs.add("IzenBerezi")
            else:
                pOs.add("Izen")
        elif kat == "ADB":
            pOs.add("Aditzondo")
        elif kat == "SIG" or kat == "LAB" or kat == "SNB":
            pOs.add("Izen")
            termType = "Acronym"
        elif kat == "ADI":
            pOs.add("Aditz")
        else:
            pOs.add("Besterik")
        return pOs
        
    
    def hashSet(self,hasha,key,value,itur,caseSig,pOs,termType,rC,zb):
        key = key.strip()
        if 'Ã' in key :
            has = key
            key = key.replace('Ã¡','á')
            key = key.replace('Ã­','í')
            key = key.replace('Ã³','ó')
            key = key.replace('Ã©','é')
            key = key.replace('Ãº','ú')
        key = key.lower()
        if key not in zb:
            key = key.encode('utf-8')
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
            if not pOs:
                if value in self.itzTBX.adj_hiz:
                    if "\tIZLK" in self.itzTBX.adj_hiz[value]:
                        pOs.add("Izenlagun")
                    else:
                        pOs.add("Izenondo")
                elif value in self.itzTBX.kat_hiz:
                    kat = self.itzTBX.kat_hiz[value].split("\t")[3]
                    azpKat = self.itzTBX.kat_hiz[value].split("\t")[4]
                    pOs = self.edbl2enum(kat,azpKat)
            elif "Adjektibo" in pOs:
                if value in self.itzTBX.adj_hiz:
                    pOs.remove("Adjektibo")
                    if "\tIZLK" in self.itzTBX.adj_hiz[value]:
                        pOs.add("Izenlagun")
                    else:
                        pOs.add("Izenondo")
                else:
                    if len(value)> 3 and ((value[-2:] in [b"ko",b"go"] and value[-3] != b"i") or value[-3:] == b"ren"):
                        pOs.add("Izenlagun")
                    else:
                        pOs.add("Izenondo")
                    pOs.remove("Adjektibo")

            ordainDat = ordainList.get(value,ItzulDBOrdain())
            ordainDat.gehituDatuak(itur,caseSig,pOs,termType,rC)
            ordainList[value]=ordainDat
            hasha[key]=ordainList
      
      
    # def zt2hashXML(self,path,hizkuntza,zbEng,zbSpa):
    #     ztEng = {}
    #     ztSpa = {}
    #     ztGaiak = ['Zool.','Anat.','Med.','Fisiol.','Mikrob.','Biokim.','Biol.','Psikiat.','Genet.','Fisiol.']
    #     fitx = path+'ZTH_2013.xml'
    #     parser = ET.XMLParser(encoding='utf-8')
    #     tree = ET.parse(fitx,parser)
    #     erroa = tree.getroot()
    #     for tE in erroa.findall('body/termEntry'):
            

    def zt2hash(self,path,hizkuntza,zbEng,zbSpa):
        ztEng = {}
        ztSpa = {}
        ztGaiak = ['Zool.','Anat.','Med.','Fisiol.','Mikrob.','Biokim.','Biol.','Psikiat.','Genet.','Fisiol.']
        ztEzGaiak = ["Fis./Kim./Teknol. Elektr./Elektron.","Teknol./Kim.","Teknol. Elektr./Kim.","Teknol./Biokim.","Mat./Fis.","Kim./Teknol. Elektr./Fis.","Kim./Teknol.","Kim./Miner.","Kim./Geol.","Kim./Fis."]
        with codecs.open(path+'/baliabideak/zt_termino_ordainak_utf.txt',encoding='utf-8') as ztFitx:
            for sarrera in ztFitx:
                if not sarrera:
                    continue
                sarrera = sarrera.strip()
                ordainak = sarrera.split('\t')
                if len(ordainak) < 6:
                    continue
                if ordainak[2].strip() in ztEzGaiak:
                    continue
                gaiak = re.split(' |/',ordainak[2].strip())
                gaBool = False
                for gai in gaiak:
                    if gai in ztGaiak:
                        gaBool = True
                if len(ordainak) == 6 and gaBool:
                    eus = ordainak[0].strip()
                    pOS = set()
                    cS = 'InitialInsensitive'
                    tT = 'Unknown'
                    if eus.isupper():
                        tT = 'Acronym'
                        cS = 'Sensitive'
                        pOS.add('IzenBerezi')
                    if eus[0].isupper():
                        if ordainak[3] and ordainak[3][0].isupper():
                            cS = 'Sensitive'
                            pOS.add('IzenBerezi')
                        elif ordainak[5] and ordainak[5][0].isupper():
                            cS = 'Sensitive'
                            pOS.add('IzenBerezi')
                    if ordainak[3] != '' and (hizkuntza == 0 or hizkuntza == 2):
                        engAk = ordainak[3].strip().split(';')
                        for eng in engAk:
                            if '?' not in eng:
                                self.hashSet(ztEng,eng,eus,'ZT',cS,pOS,tT,9,zbEng)
                    if hizkuntza >=1:
                        spaAk = ordainak[5].strip().split(';')
                        for spaLag in spaAk:
                            spa = spaLag.split(', -')[0]
                            self.hashSet(ztSpa,spa,eus,'ZT',cS,pOS,tT,9,zbSpa)
#        print(ztEng,ztSpa)
        return ztEng,ztSpa
        
    def anatomia2hash(self,path,hizkuntza,engH,spaH,zbEng,zbSpa):
        with codecs.open(path+'/baliabideak/anatomia.txt',encoding='utf-8') as fitx:
            fitxategia = fitx.readlines()
            i = 5 
            while i+5 < len(fitxategia):
                j = 1
                lat = [fitxategia[i+j].strip()]
                while lat[-1][-1] == ';':
                    j += 1
                    lat.append(fitxategia[i+j].strip())
                j += 1

                eusL = fitxategia[i+j].strip()
                eusak = [eusL]
                if ';' in eusL[:-1]:
                    eusak = eusL.split(';')
                while eusak[-1][-1] == ';':
                    j += 1
                    eusak.append(fitxategia[i+j].strip())
                j += 1
                engL = fitxategia[i+j].strip()
                engak = [engL]
                if ';' in engL[:-1]:
                    engak = engL.split(';')
                while engak[-1][-1] == ';':
                    j += 1
                    engak.append(fitxategia[i+j].strip())
                j += 1
                spaL = fitxategia[i+j].strip()
                spaak = [spaL]
                if ';' in spaL[:-1]:
                    spaak = spaL.split(';')
                while spaak[-1][-1] == ';':
                    j += 1
                    spaak.append(fitxategia[i+j].strip())
                i += j + 1
                if (hizkuntza == 0 or hizkuntza == 2):
                    for eng in engak:
                        eng = eng.replace(';','')
                        for eus in eusak:
                            eus = eus.replace(';','')
                            cS = 'Unknown'
                            pOS = set()
                            pOS.add('Izen')
                            tT = 'Unknown'
                            self.hashSet(engH,eng,eus,'Anatomia',cS,pOS,tT,9,zbEng)
                if (hizkuntza >= 1):
                    for spa in spaak:
                        for eus in eusak:
                            cS = 'Unknown'
                            pOS = set()
                            pOS.add('Izen')
                            tT = 'Unknown'
                            self.hashSet(spaH,spa,eus,'Anatomia',cS,pOS,tT,9,zbSpa)
                                    
    def gns2hash(self,path,hizkuntza,engH,spaH,zbEng,zbSpa):
        with codecs.open(path+'/baliabideak/gns10garbi6.txt',encoding='utf-8') as fitx:
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
                        self.hashSet(engH,eng,eus,'GNS10',cS,pOS,tT,5,zbEng)
                    if hizkuntza >= 1 and spa and eus:
                        self.hashSet(spaH,spa,eus,'GNS10',cS,pOS,tT,5,zbSpa)

    def erizaintza2hash(self,path,hizkuntza,engH,spaH,zbEng,zbSpa):
        if hizkuntza == 0:
            hasha = engH
            fitx = path+'/baliabideak/erizaintza_en-eu.txt'
            zb = zbEng
        else:
            hasha = spaH
            fitx = path+'/baliabideak/erizaintza_es-eu.txt'
            zb = zbSpa
        with codecs.open(fitx,encoding='utf-8') as fit:
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
                            self.hashSet(hasha,terminoa,eus,'Erizaintza',cS,pOS,tT,7,zb)
                            
    def euskalterm2hash(self,path,hizkuntza,engH,spaH,zbEng,zbSpa):
        fitx = path+'/baliabideak/euskaltermOsoa2.txt'
        with codecs.open(fitx,encoding='iso-8859-15') as fit:
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
                                if eng[-1] != '.' and eus[-1] == '.':
                                    eus = eus[:-1]
                                self.hashSet(engH,eng,eus,'EuskalTerm',cS,pos,tT,8,zbEng)
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
                                self.hashSet(spaH,spa,eus,'EuskalTerm',cS,pos,tT,8,zbSpa)

    def elhuyar2hash(self,path,hizkuntza,engH,spaH,zbEng,zbSpa):
        if hizkuntza == 0 or hizkuntza == 2: #ingelesa
            with codecs.open(path+'baliabideak/HN_N_bakuna_opentrad_utf8.txt',encoding='utf-8') as fitx:
                for sarrera in fitx:
                    sarrera = sarrera.strip()
                    sar = sarrera.split('\t')
                    if len(sar) == 3:
                        engLag = sar[0]
                        if " {to}" in engLag:
                            engLag = engLag.replace(' {to}','')
                        engak = engLag.split(';')
                        for eng in engak:
                            eng = eng.strip()
                            lag = sar[2][:-1].split(". (joan)")[0]
                            if '<I>' in lag:
                                regex1 = re.compile('\[<I>[a-z ,]+<I>\]')
                                regex2 = re.compile('\(<I>[a-z ,]+<I>\)')
                                lag = regex1.sub('',lag)
                                lag = regex2.sub('',lag)
                            if '(' in lag:
                                regex = re.compile('\([^)]+?\)')
                                lag = regex.sub('',lag)
                            eusak = re.split(',|;',lag)
                            for eus in eusak:
                                if '/' in eus or '...' in eus or eus[-1] == '-' or eus[0] == '-' or "+" in eus:
                                    continue
                                if '[' in eus:
                                    regex = re.compile('\[[^]]+?\]')
                                    eus = regex.sub('',eus)
                                if '{' in eus:
                                    regex = re.compile('\{[^}]+?\}')
                                    eus = regex.sub('',eus)
                                # if '(' in eus:
                                #     regex = re.compile('\([^)]+?\)')
                                #     eus = regex.sub('',eus)
                                if '(joan)' in eus:
                                    print(sarrera)
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
                                self.hashSet(engH,eng,eus,'Elhuyar',cS,pos,tT,7,zbEng)
        if hizkuntza > 1:#gaztelania
            with codecs.open(path+'baliabideak/Elhuyar_es_eu-utf8.txt',encoding='utf-8') as fitx:
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
                            lag= sar[3]
                            if '(' in lag:
                                regex = re.compile('\([^)]+?\)')
                                lag = regex.sub('',lag)
                            eusak = re.split(',|;',lag)
                            for eus in eusak:
                                eus = eus.strip()
                                if not eus or '/' in eus or eus[-1] == '-' or eus[0] == '-':
                                    continue
                                if '<I>' in eus:
                                    print(sarrera)
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
                                self.hashSet(spaH,spa,eus,'Elhuyar',cS,pos,tT,7,zbSpa)

                            
                        
    def adminSan2hash(self,path,spaH,zbSpa):
        with codecs.open(path+'baliabideak/adm_san.txt',encoding='utf-8') as fitx:
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
                    self.hashSet(spaH,spa,eus,'AdminSan',cS,pos,tT,8,zbSpa)

    def morfo2Hash(self,path,engH,zbEng):
        with codecs.open(path+'baliabideak/morfoHiztegia.txt',encoding='utf-8') as fitx:
            for line in fitx:
                line = line.strip()
                lineLag = line.split('\t')
                eng = lineLag[0]
                eusak = lineLag[2:]
                for eus in eusak:
                    if eus[0].isupper():
                        us = "Sensitive"
                    else:
                        us = "InitialInsensitive"
                    self.hashSet(engH,eng,eus,'Morfologia',us,set(['Izen']),'TranscribedForm',7,zbEng)

    def medikuak2Hash(self,path,engH,zbEng):
        with codecs.open(path+'baliabideak/felixenPareak.txt',encoding='utf-8') as fitx:
            for line in fitx:
                line = line.strip()
                lineLag = line.split('\t')
                eng = lineLag[0][1:-1]
                eusak = lineLag[1:]
                if "" in eusak:
                    eusakLag.pop("")
                # eusak = []
                # if '"' in eusakLag:
                #     eusak = eusakLag[1:-1].split('","')
                # else:
                #     eusak = eusakLag.split(',')
                for eus in eusak:
                    cS = 'InitialInsensitive'
                    if eus[0].upper():
                        cS = 'Sensitive'
                    self.hashSet(engH,eng,eus[1:-1],'Medikuak',cS,set(['Izen']),'',9,zbEng)
                    
        with codecs.open(path+'baliabideak/karlosenPareak.txt',encoding='utf-8') as fitx:
            for line in fitx:
                line = line.strip()
                lineLag = line.split('\t')
                eng = lineLag[0]
                eusakLag = lineLag[1]
                eusak = []
                if '"' in eusakLag:
                    eusak = eusakLag[1:-1].split('","')
                else:
                    eusak = eusakLag.split(',')
                for eus in eusak:
                    cS = 'InitialInsensitive'
                    if eus[0].upper():
                        cS = 'Sensitive'
                    self.hashSet(engH,eng,eus,'Medikuak',cS,set(['Izen']),'',9,zbEng)

        with codecs.open(path+'baliabideak/felixenBestePareak.txt',encoding='utf-8') as fitx:
            for line in fitx:
                line = line.strip()
                lineLag = re.sub('\t+','\t',line.replace('_',' ')).split('\t')
                eng = lineLag[0]
                eusak = lineLag[1].split(',')
                for eus in eusak:
                    cS = 'InitialInsensitive'
                    if eus[0].upper():
                        cS = 'Sensitive'
                    pos = set(['Izen'])
                    if len(lineLag) > 2:
                        pos = set([lineLag[2]])
                    self.hashSet(engH,eng,eus,'Medikuak',cS,pos,'',8,zbEng)
        
        with codecs.open(path+'baliabideak/karlosenBestePareak.txt',encoding='utf-8') as fitx:
            for line in fitx:
                line = line.strip()
                lineLag = re.sub('\t+','\t',line.replace('_',' ')).split('\t')
                eng = lineLag[0]
                eusak = lineLag[1].split(',')
                for eus in eusak:
                    cS = 'InitialInsensitive'
                    if eus[0].upper():
                        cS = 'Sensitive'
                    pos = set(['Izen'])
                    if len(lineLag) > 2:
                        pos = set([lineLag[2]])
                    self.hashSet(engH,eng,eus,'Medikuak',cS,pos,'',8,zbEng)

    def hasieratu(self,path,hizkuntza):

        with codecs.open(path+'zerrendaBeltzak/stopWords-en.txt',encoding='utf-8') as fitx:
            zbEng = fitx.read().split('\n')
        with codecs.open(path+'zerrendaBeltzak/stopWords-es.txt',encoding='utf-8') as fitx:
            zbSpa = fitx.read().split('\n')
        engH,spaH = self.zt2hash(path,hizkuntza,zbEng,zbSpa)
        print('ZT',len(engH),len(spaH))
        self.anatomia2hash(path,hizkuntza,engH,spaH,zbEng,zbSpa)
        print('+Anatomia',len(engH),len(spaH))
        self.gns2hash(path,hizkuntza,engH,spaH,zbEng,zbSpa)
        print('+GNS10',len(engH),len(spaH))
        self.euskalterm2hash(path,hizkuntza,engH,spaH,zbEng,zbSpa)
        print('+Euskalterm',len(engH),len(spaH))
        if hizkuntza ==2:
            self.erizaintza2hash(path,0,engH,spaH,zbEng,zbSpa)
            self.erizaintza2hash(path,1,engH,spaH,zbEng,zbSpa)
            print('+Erizaintza',len(engH),len(spaH))
        else:
            self.erizaintza2hash(path,hizkuntza,engH,spaH,zbEng,zbSpa)
            print('+Erizaintza',len(engH),len(spaH))
        if hizkuntza >= 1:
            self.adminSan2hash(path,spaH,zbSpa)
            print('+AdminSan',len(engH),len(spaH))
        if hizkuntza == 2 or hizkuntza == 0:
            #self.morfo2Hash(path,engH,zbEng)
            #print('+Morfosemantika',len(engH),len(spaH))
            self.medikuak2Hash(path,engH,zbEng)
            print('+Medikuak',len(engH),len(spaH))
        self.elhuyar2hash(path,hizkuntza,engH,spaH,zbEng,zbSpa)
        print('+Elhuyar',len(engH),len(spaH))
        return engH,spaH
    

    def __init__(self,path,hizkuntza,itzulBool=False,fitxategia=''):
        if itzulBool:
            self.itzTBX = ItzulDBTBX(0,path)#berdin dio hizkuntza, gero matxakatuko dugu eta. adj eta kat hiztegiak kargatzeko baino ez da
            engH,spaH = self.hasieratu(path,hizkuntza)
            if hizkuntza == 0 or hizkuntza == 2:
                self.itzTBX = ItzulDBTBX(0,path)
                self.itzTBX.xmltanElkartu(engH)
            if hizkuntza >= 1:
                self.itzTBX = ItzulDBTBX(1,path)
                self.itzTBX.xmltanElkartu(spaH)
        else:
            self.itzTBX = ItzulDBTBX(hizkuntza,path)
            self.itzTBX.kargatu(fitxategia)

        
    def jaso(self,terminoa):
        return self.itzTBX.jaso(terminoa)

    def gehitu(self,ordList,term,entrySource,caseSig,pOs,tT,rC,orPat=""):
        return self.itzTBX.gehituParea(term,ordList,entrySource,caseSig,pOs,tT,rC,orPat)


    def fitxategianGorde(self):
        self.itzTBX.fitxategianGorde()

    def denakJaso(self):
        return self.itzTBX.denakJaso()

    def pareaJaso(self,terminoa):
        return self.itzTBX.pareaJaso(terminoa)

    def terminoaJaso(self,terminoa,hizkuntza):
        return self.itzTBX.terminoaJaso(terminoa,hizkuntza)

    def toHash(self):
        return self.itzTBX.toHash()
