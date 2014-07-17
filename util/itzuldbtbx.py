#!/usr/bin/python3
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import unidecode

class ItzulDBTBX:

    def __init__(self,hizkuntza,path):
        self.hizkuntza = hizkuntza
        if hizkuntza == 0:
            hiz = 'en'
        elif hizkuntza == 1:
            hiz = 'es'
        self.hizkuntza = hiz;
        self.path = path;
        self.entryIdAlt=0;
        self.termIdAlt=0;
        
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
            langSetErd.set('xml:lang',self.hizkuntza)
            tigErd = ET.SubElement(langSetErd,'tig',id='t'+str(self.termIdAlt))
            termErd = ET.SubElement(tigErd,'term').text = erd
            sKeyEn = ET.SubElement(tigErd,'admin',type='sortKey').text = unidecode.unidecode(erd)
            self.termIdAlt += 1
            langSet = ET.SubElement(termEntry,'langSet')
            langSet.set('xml:lang','eu')
            for eu,orda in hz.items():
                eu = eu.decode('utf-8')
                tig = ET.SubElement(langSet,'tig',id='t'+str(self.termIdAlt))
                term = ET.SubElement(tig,'term').text = eu
                sKey = ET.SubElement(tig,'admin',type='sortKey').text = unidecode.unidecode(eu)
                ews = ET.SubElement(tig,'admin',type='elementWorkingStatus').text = 'starterElement'
                for hiz in orda.getHiztegiZerrenda():
                    enSo = ET.SubElement(tig,'admin',type='entrySource').text = hiz
                if not orda.getPOS():
                    orda.setPOS('Izen')
                for pos in orda.getPOS():
                    ePOS = ET.SubElement(tig,'termNote',type='partOfSpeech').text =pos
                rel = ET.SubElement(tig,'descrip',type='reliabilityCode').text = str(orda.getReliabilityCode())
                caSi = ET.SubElement(tig,'termNote',type='usageNote').text = orda.getCaseSignificance()
                #print(eu,hiz,orda.getTermType())
                if orda.getTermType() != 'Unknown':
                    teTy = ET.SubElement(tig,'termNote',type='termType').text = orda.getTermType()
                self.termIdAlt += 1
            self.entryIdAlt += 1
        return body

    def xmltanElkartu(self,hasha):
        erroa = ET.Element('martif',type='TBX')
        erroa.set('xml:lang','eu')
        erroa.append(self.burukoaXMLItzulDB())
        text = ET.SubElement(erroa,'text')
        text.append(self.hash2tbx(hasha))
        dok = self.path+'/baliabideak/ItzulDB'+self.hizkuntza+'Has.xml'
        tree = ET.ElementTree(erroa)
        tree.write(dok,encoding='utf-8',xml_declaration=True)
       
    def kargatu(self):
        dok = self.path+'/baliabideak/ItzulDB'+self.hizkuntza+'Has.xml'
        tree = ET.parse(dok)
        self.erroa = tree.getroot()
        self.entryIdAlt = len(self.erroa.findall('text/body/termEntry'))
        self.termIdAlt = len(self.erroa.findall('text/body/termEntry/langSet/tig'))
        #print(self.hizkuntza,self.entryIdAlt,self.termIdAlt)
    
    def jaso(self,terminoa):
        namespace={'xml':'http://www.w3.org/XML/1998/namespace'}
        for termEntry in self.erroa.findall('text/body/termEntry'):
            lag = termEntry.findtext('langSet[@xml:lang="'+self.hizkuntza+'"]/tig/term',namespaces=namespace)
            if lag and lag.lower() == terminoa.lower():
                return termEntry.findall('langSet[@xml:lang="eu"]/tig',namespaces=namespace)
                
    def gehituParea(self,term,ordList,entrySource,caseSig,pOS,tT,rC):
        termEntry = ET.SubElement(self.erroa.find('text/body'),'termEntry',id='p'+str(self.entryIdAlt))
        langSetErd = ET.SubElement(termEntry,'langSet')
        langSetErd.set('xml:lang',self.hizkuntza)
        tigErd = ET.SubElement(langSetErd,'tig',id='t'+str(self.termIdAlt))
        termErd = ET.SubElement(tigErd,'term').text = term
        sKeyEn = ET.SubElement(tigErd,'admin',type='sortKey').text = unidecode.unidecode(term)
        self.termIdAlt += 1
        langSet = ET.SubElement(termEntry,'langSet')
        langSet.set('xml:lang','eu')
        for eu in ordList:
            if eu:
                tig = ET.SubElement(langSet,'tig',id='t'+str(self.termIdAlt))
                term = ET.SubElement(tig,'term').text = eu
                sKey = ET.SubElement(tig,'admin',type='sortKey').text = unidecode.unidecode(eu)
                ews = ET.SubElement(tig,'admin',type='elementWorkingStatus').text = 'starterElement'
                enSo = ET.SubElement(tig,'admin',type='entrySource').text = entrySource
                ePOS = ET.SubElement(tig,'termNote',type='partOfSpeech').text =pOS
                rel = ET.SubElement(tig,'descrip',type='reliabilityCode').text = str(rC)
                caSi = ET.SubElement(tig,'termNote',type='usageNote').text = caseSig
                #print(eu,hiz,orda.getTermType())
                if tT != 'Unknown':
                    teTy = ET.SubElement(tig,'termNote',type='termType').text = tT
                self.termIdAlt += 1
        self.entryIdAlt += 1
        return langSet.findall('tig')


    def fitxategianGorde(self):
        dok = self.path+'/baliabideak/ItzulDB'+self.hizkuntza+'.xml'
        tree = ET.ElementTree(self.erroa)
        tree.write(dok,encoding='utf-8',xml_declaration=True)
