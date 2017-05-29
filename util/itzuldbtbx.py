#!/usr/bin/python3
# -*- coding: utf-8 -*-
#import xml.etree.ElementTree as ET
from lxml import etree as ET
import unidecode,codecs
from datetime import date

class ItzulDBTBX:

    def transakzioInfoGehitu(self,termEntry,tr_type="importation"):
        trG = termEntry.find("transacGrp")
        if trG is not None:
            #trG.find("transac").text = tr_type
            trG.find("date").text = date.today().isoformat()
        else:
            trG = ET.SubElement(termEntry,"transacGrp")
            #trT = ET.SubElement(trG,"transac",type="transactionType").text = tr_type
            trD = ET.SubElement(trG,"date").text= date.today().isoformat()
        return trG


    def adjKargatu(self,path):
        self.adj_hiz = {}
        with codecs.open(path+"/baliabideak/edbl_adjektiboak.txt",encoding= "iso-8859-1") as adjf:
            lerroak = adjf.readlines()
            for line in lerroak[2:]:
                if line:
                    zat = line.strip().split("\t")
                    self.adj_hiz[zat[1]] = zat[4]

    def katKargatu(self,path):
        self.kat_hiz = {}
        with codecs.open(path+"/baliabideak/edbl_kategoriak.txt",encoding= "iso-8859-1") as katf:
            lerroak = katf.readlines()
            for line in lerroak[2:]:
                zat = line.strip().split("\t")
                self.kat_hiz[zat[1]] = zat[3]+'\t'+zat[4]

    def edbl2enum(self,kat,azpKat):
        #print(kat,azpKat)
        if kat == "IZE":
            if azpKat[:3] == "LIB" or azpKat[:2] == "IB" :
                pOs = "IzenBerezi"
            else:
                pOs = "Izen"
        elif kat == "ADB":
            pOs = "Aditzondo"
        elif kat == "SIG" or kat == "LAB" or kat == "SNB":
            pOs = "Izen"
            termType = "Acronym"
        elif kat == "ADI":
            pOs = "Aditz"
        else:
            pOs = "Besterik"
        #print(pOs)
        return pOs

    def __init__(self,hizkuntza,path):
        self.adjKargatu(path)
        self.katKargatu(path)
        self.hizkuntza = hizkuntza
        if hizkuntza == 0:
            hiz = 'en'
        elif hizkuntza == 1:
            hiz = 'es'
        if type(hizkuntza) == type(2):
            self.hizkuntza = hiz
        self.path = path
        self.entryIdAlt=0
        self.termIdAlt=0
        
    def burukoaXMLItzulDB(self):
        header = ET.Element('martifHeader')
        h1 = ET.SubElement(header,'fileDesc')
        h2 = ET.SubElement(h1,'titleStmt')
        title = ET.SubElement(h2,'title').text='SNOMED Itzultzeko - ItzulDB'+self.hizkuntza
        note = ET.SubElement(h2,'note').text ='TZOS-en erabiltzen den TBX erabili dugu, gure beharretara pixka bat moldatuaz.'
        note1 = ET.SubElement(h2,'note').text ='ZT hiztegia, Elhuyar, Erizaintza hiztegia, eta abar hiztegi elkarbildurik'
        sourDes = ET.SubElement(h1,'sourceDesc')
        p1 = ET.SubElement(sourDes,'p').text = 'Snomed CT itzultzeko erabiliteko baliabideen elkarketa.'
        h3 = ET.SubElement(header,'encodingDesc')
        p = ET.SubElement(h3,"p",type="XCSURI").text = "TBXXCSV02_TZOS.xcs"
        return header
        
    def hash2tbx(self,hasha):
        body = ET.Element('body')
        #print(hasha[b'meningitis'])
        for erd,hz in hasha.items():
            erd = erd.decode('utf-8')
            termEntry = ET.SubElement(body,'termEntry',id='p'+str(self.entryIdAlt))
            admin = ET.SubElement(termEntry,'admin',type='elementWorkingStatus').text = 'importedElement'
            langSetErd = ET.SubElement(termEntry,'langSet')
            langSetErd.set('{http://www.w3.org/XML/1998/namespace}lang',self.hizkuntza)
            tigErd = ET.SubElement(langSetErd,'tig',id='t'+str(self.termIdAlt))
            termErd = ET.SubElement(tigErd,'term').text = erd
            sKeyEn = ET.SubElement(tigErd,'admin',type='sortKey').text = unidecode.unidecode(erd)
            self.termIdAlt += 1
            langSet = ET.SubElement(termEntry,'langSet')
            langSet.set('{http://www.w3.org/XML/1998/namespace}lang','eu')
            izena = False
            for eu,orda in hz.items():
                eu = eu.decode('utf-8')
                posak = orda.getPOS()
                if izena and ("Aditz" in posak or "Aditzondo" in posak or "Adjektibo" in posak) and "Izen" not in posak and "IzenBerezi" not in posak:
                    continue
                tig = ET.SubElement(langSet,'tig',id='t'+str(self.termIdAlt))
                term = ET.SubElement(tig,'term').text = eu
                sKey = ET.SubElement(tig,'admin',type='sortKey').text = unidecode.unidecode(eu)
                ews = ET.SubElement(tig,'admin',type='elementWorkingStatus').text = 'starterElement'
                hizt_kop = len(orda.getHiztegiZerrenda())
                for hiz in orda.getHiztegiZerrenda():
                    enSo = ET.SubElement(tig,'admin',type='entrySource').text = hiz
                if not orda.getPOS():
                    if " " not in eu and eu.endswith(('ko','go')):
                        orda.setPOS('Izenlagun')
                    else:
                        orda.setPOS('Izen')
                for pos in posak:
                    #print(erd,eu,pos)
                    ePOS = ET.SubElement(tig,'termNote',type='partOfSpeech').text =pos
                    #print("tig",ET.tounicode(tig,pretty_print=True))
                    if pos in ["Izen","IzenBerezi"]:
                        izena = True
                rel = ET.SubElement(tig,'descrip',type='reliabilityCode').text = str(orda.getReliabilityCode()+hizt_kop*0.1)
                caSi = ET.SubElement(tig,'termNote',type='usageNote').text = orda.getCaseSignificance()
                #print(eu,hiz,orda.getTermType())
                if orda.getTermType() != 'Unknown':
                    teTy = ET.SubElement(tig,'termNote',type='termType').text = orda.getTermType()
                self.termIdAlt += 1
                # if erd == "evening":
                #     print("tig",ET.tounicode(tig,pretty_print=True))
            trans = self.transakzioInfoGehitu(termEntry)
            self.entryIdAlt += 1
        return body

    def xmltanElkartu(self,hasha):
        erroa = ET.Element('martif',type='TBX')
        erroa.set('{http://www.w3.org/XML/1998/namespace}lang','eu')
        erroa.append(self.burukoaXMLItzulDB())
        text = ET.SubElement(erroa,'text')
        text.append(self.hash2tbx(hasha))
        dok = self.path+'/baliabideak/ItzulDB'+self.hizkuntza+'Has.xml'
        tree = ET.ElementTree(erroa)
        tree.write(dok,encoding='utf-8',xml_declaration=True)
       
    def kargatu(self,fitxategia=''):
        if fitxategia:
            dok = fitxategia

        else:
            dok = self.path+'/baliabideak/ItzulDB'+self.hizkuntza+'Has.xml'
        print(dok)
        parser = ET.XMLParser(encoding='utf-8')
        tree = ET.parse(dok,parser)
        self.erroa = tree.getroot()
        self.entryIdAlt = len(self.erroa.findall('text/body/termEntry'))
        self.termIdAlt = len(self.erroa.findall('text/body/termEntry/langSet/tig'))
        #print(self.hizkuntza,self.entryIdAlt,self.termIdAlt)
    
    def jaso(self,terminoa):
        namespace={'xml':'http://www.w3.org/XML/1998/namespace'}
        for termEntry in self.erroa.findall('text/body/termEntry'):
            lag = termEntry.findtext('langSet[@{http://www.w3.org/XML/1998/namespace}lang="'+self.hizkuntza+'"]/tig/term',namespaces=namespace)
            if lag and lag.lower() == terminoa.lower():
                return termEntry.findall('langSet[@{http://www.w3.org/XML/1998/namespace}lang="eu"]/tig',namespaces=namespace)
                
    def gehituParea(self,term,ordList,entrySource,caseSig,pOS,tT,rC,orPat):
        termEntry = ET.SubElement(self.erroa.find('text/body'),'termEntry',id='p'+str(self.entryIdAlt))
        langSetErd = ET.SubElement(termEntry,'langSet')
        langSetErd.set('{http://www.w3.org/XML/1998/namespace}lang',self.hizkuntza)
        tigErd = ET.SubElement(langSetErd,'tig',id='t'+str(self.termIdAlt))
        termErd = ET.SubElement(tigErd,'term').text = term
        sKeyEn = ET.SubElement(tigErd,'admin',type='sortKey').text = unidecode.unidecode(term)
        self.termIdAlt += 1
        langSet = ET.SubElement(termEntry,'langSet')
        langSet.set('{http://www.w3.org/XML/1998/namespace}lang','eu')
        for eu in ordList:
            if eu:
                #print(1,1,eu,pOS)
                if not pOS:
                    if eu in self.adj_hiz:
                        #print("adjektiboetan")
                        if "\tIZLK" in self.adj_hiz[eu]:
                            pOS.add("Izenlagun")
                        else:
                            pOS.add("Izenondo")
                    if eu in self.kat_hiz:
                        #print("edbln-ko kategorian")
                        kat = self.kat_hiz[eu].split("\t")[0]
                        #print("kat",term)
                        azpKat = self.kat_hiz[eu].split("\t")[1]
                        #print("azpKat",term)
                        edKat = self.edbl2enum(kat,azpKat)
                        #print('edKat',edKat)
                        pOS.add(edKat)
                        #print("pos.add",term,pOS)
                    if eu.endswith("iko") and term.endswith(b"ic") and not pOS:
                        #print("iko bukaera")
                        pOS = set(["Izenlagun"])
                    if not pOS and " " in eu:
                        #print("gainerakoak")
                        eu_lag = eu.split(" ")[-1]
                        if eu_lag in self.kat_hiz:
                            kat = self.kat_hiz[eu_lag].split("\t")[0]
                            azpKat = self.kat_hiz[eu_lag].split("\t")[1]
                            pOS.add(self.edbl2enum(kat,azpKat))
                        if eu_lag in self.adj_hiz:
                            if "IZLK" in self.adj_hiz[eu_lag]:
                                pOS.add("Izenlagun")
                            else:
                                pOS.add("Izenondo")
                    #print("kurrukukuk")
                #print(1,2,eu,pOS)
                tig = ET.SubElement(langSet,'tig',id='t'+str(self.termIdAlt))
                term = ET.SubElement(tig,'term').text = eu
                sKey = ET.SubElement(tig,'admin',type='sortKey').text = unidecode.unidecode(eu)
                ews = ET.SubElement(tig,'admin',type='elementWorkingStatus').text = 'starterElement'
                enSo = ET.SubElement(tig,'admin',type='entrySource').text = entrySource
                if orPat:
                    #print("orPat",orPat)
                    for orP in orPat:
                        orDa = ET.SubElement(tig,"admin",type="originatingDatabase").text = orP
                for p in pOS:
                    ePOS = ET.SubElement(tig,'termNote',type='partOfSpeech').text = p
                rel = ET.SubElement(tig,'descrip',type='reliabilityCode').text = str(rC)
                caSi = ET.SubElement(tig,'termNote',type='usageNote').text = caseSig
                #print(eu,hiz,orda.getTermType())
                if tT != 'Unknown':
                    teTy = ET.SubElement(tig,'termNote',type='termType').text = tT
                self.termIdAlt += 1
            trans = self.transakzioInfoGehitu(termEntry)
        self.entryIdAlt += 1
        return langSet.findall('tig')


    def fitxategianGorde(self):
        dok = self.path+'/baliabideak/ItzulDB'+self.hizkuntza+'.xml'
        tree = ET.ElementTree(self.erroa)
        tree.write(dok,encoding='utf-8',xml_declaration=True)
        print(dok,'fitxategia sortua')

    def denakJaso(self):
        namespace={'xml':'http://www.w3.org/XML/1998/namespace'}
        denak = {}
        for termEntry in self.erroa.findall('text/body/termEntry'):
            kodea = termEntry.get('id')
            jatTerm = termEntry.findtext('langSet[@{http://www.w3.org/XML/1998/namespace}lang="'+self.hizkuntza+'"]/tig/term',namespaces=namespace)
            if jatTerm:
                jatTerm += '\t'+kodea
                ordainak = termEntry.findall('langSet[@{http://www.w3.org/XML/1998/namespace}lang="eu"]/tig',namespaces=namespace)
                for ordain in ordainak:
                    lag = denak.get(jatTerm,[])
                    ordT = ordain.findtext('term')
                    if jatTerm[-1] != '.' and ordT and ordT[-1] == '.':
                        ordT = ordT[:-1]
                    lag.append(ordT)
                    denak[jatTerm] = lag
        return denak
    
    def terminoaJaso(self,terminoa,hizkuntza):
        namespace={'xml':'http://www.w3.org/XML/1998/namespace'}
        irtLag = []
        for tig in self.erroa.findall('text/body/termEntry/langSet[@{http://www.w3.org/XML/1998/namespace}lang="'+hizkuntza+'"]/tig'):
            lag = tig.findtext('term')
            if lag and lag.lower() == terminoa.lower():
                if hizkuntza == self.hizkuntza: 
                    return tig
                # else:
                #     irtLag.append(tig)

    def pareaJaso(self,terminoa):
        #emandako terminoari dagokion termEntry osoa itzultzen du (ordain guztiak hizkuntza guztietan)
        namespace={'xml':'http://www.w3.org/XML/1998/namespace'}
        for termEntry in self.erroa.findall('text/body/termEntry'):
            lag = termEntry.findtext('langSet[@{http://www.w3.org/XML/1998/namespace}lang="'+self.hizkuntza+'"]/tig/term',namespaces=namespace)
            if lag and lag.lower() == terminoa.lower():
                return termEntry
    
        
    def toHash(self):
        denak = {}
        for termEntry in self.erroa.findall('text/body/termEntry'):
            jatTerm = termEntry.findtext('langSet[@{http://www.w3.org/XML/1998/namespace}lang="'+self.hizkuntza+'"]/tig/term')
            if jatTerm:
                ordainak = termEntry.findall('langSet[@{http://www.w3.org/XML/1998/namespace}lang="eu"]/tig')
                denak[jatTerm] = ordainak
        return denak


    def fromPattern(self,pat):
        """
        pat patroi bat emanda, patroi hori erabiliz sortutako pareak itzultzen ditu.
        """
        pareak = []
        for termEntry in self.erroa.findall('text/body/termEntry'):
            if termEntry.findtext("langSet[@{http://www.w3.org/XML/1998/namespace}lang='eu']/tig/admin[@type='originatingDatabase']") == "|"+pat:
                pareak.append(termEntry)
        return pareak

