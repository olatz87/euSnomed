#!/usr/bin/python3
# -*- coding: utf-8 -*-
from util.enumeratuak import Hierarkia,SemanticTag,CaseSignificance
#import xml.etree.ElementTree as ET
from lxml import etree as ET
from util.kontzeptutbx import KontzeptuTBX
from util.enumeratuak import Iturburua
from util.terminotbxsnomed import TerminoTBXSnomed
from util.ordaintbxsnomed import OrdainTBXSnomed
import re,unidecode,codecs
class SnomedTBX:
    

    def __init__(self,path,hKodea = '',cli=''):
        self.path = path
        self.hierarkia = hKodea
        self.clinical = cli
        if self.hierarkia != '':
            fitx = path+"/snomed/XMLak/"+self.hierarkia+self.clinical+".xml"
            parser = ET.XMLParser(encoding='utf-8')
            tree = ET.parse(fitx,parser)
            self.erroa = tree.getroot()

    def fitx2hash(self,fitxategia):
        hasha = {}
        with codecs.open(fitxategia,encoding='utf-8') as fitx:
            for lerroa in fitx:
                lerroa = lerroa.strip()
                elementuak = lerroa.split('\t')
                if len(elementuak) > 4 and elementuak[4] != '':
                    zer = hasha.get(elementuak[4],[])
                    zer.append(elementuak)
                    hasha[elementuak[4]]=zer
        return hasha
    
    def burukoaXMLSnomed(self,hie):
        header = ET.Element('martifHeader')
        h1 = ET.SubElement(header,'fileDesc')
        h2 = ET.SubElement(h1,'titleStmt')
        title = ET.SubElement(h2,'title').text='SNOMED Itzultzeko - ItzulDB'+hie
        note = ET.SubElement(h2,'note').text ='TZOS-en erabiltzen den TBX erabili dugu, gure beharretara pixka bat moldatuaz.'
        note1 = ET.SubElement(h2,'note').text = hie+' hierarkiaren XML fitxategia'
        sourDes = ET.SubElement(h1,'sourceDesc')
        p1 = ET.SubElement(sourDes,'p').text = 'Snomed CTren ingelesezko 20140131 eta gaztelaniazko 20140430 bertsioa.'
        h3 = ET.SubElement(header,'encodingDesc')
        p = ET.SubElement(h3,"p",type="XCSURI").text = "TBXXCSV02_TZOS.xcs"
        return header

    def ordenatu(self):
        container = self.erroa.findall('./text/body/termEntry')
        # container.sort(key = lambda x: len(x.split())) PROBATU HONEKIN, x beharrean, preferredTerm izango da baina..
        data = []
        for elem in container:
            kontz = KontzeptuTBX(elem)
            key = kontz.getPreferredTerm('en')

    def semanticTagLortu(fsnTerm,hizkuntza='en'):
        if hizkuntza == 'es':
            i = 2
        else:
            i = 1
        fsnST = re.search('\(([^(]+?)\)$',fsnTerm)
        if fsnST:
            for st in SemanticTag:
                if fsnST.group(1) == SemanticTag[st][i]:
                    return st
            return 'Hutsa'
        else:
            return 'Hutsa'

    def langSetEzarri(self,pre,syn,hizk):
        langSet = ET.Element('langSet')
        langSet.set('{http://www.w3.org/XML/1998/namespace}lang',hizk)
        for pre1 in pre:
            ntig = ET.SubElement(langSet,'ntig',id=hizk+pre1[0])
            termGrp = ET.SubElement(ntig,'termGrp')
            term = ET.SubElement(termGrp,'term').text = pre1[7]
            termNote = ET.SubElement(termGrp,'termNote',type='administrativeStatus').text = 'preferredTerm-adm-sts'
            sortKey = ET.SubElement(ntig,'admin',type='sortKey').text = unidecode.unidecode(pre1[7])
            #workStatus = ET.SubElement(ntig,'admin',type='elementWorkingStatus').text = 'importedElement'
            if 'InitialInsensitive' == pre1[8]:
                cS = 'InitialInsensitive'
            elif 'Sensitive' == pre1[8]:
                cS = 'Sensitive'
            else:
                cS = 'Insensitive'
            usageNote = ET.SubElement(termGrp,'termNote',type='usageNote').text = cS
        for syn1 in syn:
            ntig = ET.SubElement(langSet,'ntig',id=hizk+syn1[0])
            termGrp = ET.SubElement(ntig,'termGrp')
            term = ET.SubElement(termGrp,'term').text = syn1[7]
            termNote = ET.SubElement(termGrp,'termNote',type='administrativeStatus').text = 'admittedTerm-adm-sts'
            sortKey = ET.SubElement(ntig,'admin',type='sortKey').text = unidecode.unidecode(syn1[7])
            #workStatus = ET.SubElement(ntig,'admin',type='elementWorkingStatus').text = 'importedElement'
            if CaseSignificance['InitialInsensitive'] == syn1[8]:
                cS = 'InitialInsensitive'
            elif CaseSignificance['Sensitive'] == syn1[8]:
                cS = 'Sensitive'
            else:
                cS = 'Insensitive'
            usageNote = ET.SubElement(termGrp,'termNote',type='usageNote').text = cS
        return langSet

    def terminoenXML(self,hie,cId,fsn,preEng,preSpa,synEng,synSpa):
        fsnTerm = fsn[0][7]
        semTag = SnomedTBX.semanticTagLortu(fsnTerm)
        termEntry = ET.Element('termEntry',id='c'+cId)
        sfH = Hierarkia[hie][0]
        if semTag != 'Hutsa':
            sfH += '-'+SemanticTag[semTag][0]
        subFieHie = ET.SubElement(termEntry,'descrip',type='subjectField').text = sfH
        defEl = ET.SubElement(termEntry,'descrip',type='definition').text = fsnTerm
        termEntry.append(self.langSetEzarri(preEng,synEng,'en'))
        spa = self.langSetEzarri(preSpa,synSpa,'es')
        if spa.find('ntig'):
            termEntry.append(spa)
        return termEntry

    def xmltanBanatu(self):
        for hie in Hierarkia:
            i = 1
            cli = ['','']
            if hie == 'CLINICAL':
                i = 2
                cli = ['_FIN','_DIS']
            for j in range(0,i):
                fsnak = self.fitx2hash(self.path+'snomed/hierarkiak/'+hie+cli[j]+'_fsn.txt')
                preEngak = self.fitx2hash(self.path+'snomed/hierarkiak/'+hie+cli[j]+'_pre_eng.txt')
                preSpaak = self.fitx2hash(self.path+'snomed/hierarkiak/'+hie+cli[j]+'_pre_spa.txt')
                synEngak = self.fitx2hash(self.path+'snomed/hierarkiak/'+hie+cli[j]+'_syn_eng.txt')
                synSpaak = self.fitx2hash(self.path+'snomed/hierarkiak/'+hie+cli[j]+'_syn_spa.txt')
                self.erroa = ET.Element('martif',type='TBX')
                self.erroa.set('{http://www.w3.org/XML/1998/namespace}lang','eu')
                self.erroa.append(self.burukoaXMLSnomed(hie))
                text = ET.SubElement(self.erroa,'text')
                body = ET.SubElement(text,'body')
                for cId,fsn in fsnak.items():
                    preEng = preEngak.get(cId,[])
                    preSpa = preSpaak.get(cId,[])
                    synEng = synEngak.get(cId,[])
                    synSpa = synSpaak.get(cId,[])
                    body.append(self.terminoenXML(hie,cId,fsn,preEng,preSpa,synEng,synSpa))
                #self.ordenatu()
                dok = self.path+'snomed/XMLak/'+hie+cli[j]+'.xml'
                tree = ET.ElementTree(self.erroa)
                tree.write(dok,encoding='utf-8',xml_declaration=True)
                print(hie+cli[j],'hierarkiaren XMLa sortua.')

    def getKontzeptu(self,cId):
        kon = self.erroa.find('text/body/termEntry[@id="c'+cId+'"]')
        if kon:
            return KontzeptuTBX(kon)
        else:
            return None
        
    def getKontzeptuak(self):
        return self.erroa.findall('text/body/termEntry')

    def gorde(self):
        dok = self.path+'snomed/XMLak/'+self.hierarkia+self.clinical+'_ald.xml'
        tree = ET.ElementTree(self.erroa)
        tree.write(dok,encoding='utf-8',xml_declaration=True)

        parser = ET.XMLParser(encoding='utf-8')
        tree = ET.parse(dok,parser)
        self.erroa = tree.getroot()
    
    def getItzulitakoOrdainKop(self):
        namespace={'xml':'http://www.w3.org/XML/1998/namespace'}
        return len(self.erroa.findall('text/body/termEntry/langSet[@{http://www.w3.org/XML/1998/namespace}lang="eu"]/ntig',namespaces=namespace))

    def getItzulitakoKontzeptuKop(self):
        namespace={'xml':'http://www.w3.org/XML/1998/namespace'}
        return len(self.erroa.findall('text/body/termEntry/langSet[@{http://www.w3.org/XML/1998/namespace}lang="eu"]',namespaces=namespace))

    def getItzulitakTerminoKop(self):
        namespace={'xml':'http://www.w3.org/XML/1998/namespace'}
        orig = set()
        for el in self.erroa.findall('text/body/termEntry/langSet[@{http://www.w3.org/XML/1998/namespace}lang="eu"]/ntig/admin[@type="conceptOrigin"]',namespaces=namespace):
            orig.add(el.text)
        return len(orig)

    def getSemanticTagKop(self):
        kopuruak = {}
        for elem in self.erroa.findall('text/body/termEntry/descrip[@type="subjectField"]'):
            kop = kopuruak.get(elem.text,0)
            kopuruak[elem.text] = kop +1
        return kopuruak

    def getKontzeptuIdak(self):
        idak = []
        for kon in self.getKontzeptuak():
            idak.append(KontzeptuTBX(kon).getKontzeptuId()[1:])
        return idak

    def getHiztegietatikKop(self):
        namespace={'xml':'http://www.w3.org/XML/1998/namespace'}
        k = 0
        kI = 0
        kG = 0
        for el in self.erroa.findall('text/body/termEntry/langSet[@{http://www.w3.org/XML/1998/namespace}lang="eu"]/ntig',namespaces=namespace):
            
            eSlist = el.findall('admin[@type="entrySource"]')
            cOlist = el.findall('admin[@type="conceptOrigin"]')
            hizt = False
            ing = False
            spa = False
            for e in eSlist:
                if e.text != "000" and e.text[0] == "0":
                    hizt = True
            for c in cOlist:
                if c.text[:2]== "es":
                    spa = True
                if c.text[:2] == "en":
                    ing = True
            if hizt and ing:
                kI += 1
            if hizt and spa:
                kG += 1
            if hizt:
                k += 1
        print("k",k,"kI",kI,"kG",kG)
           
    def getHiztegietatikKontzeptuak(self):
        namespace={'xml':'http://www.w3.org/XML/1998/namespace'}
        k = 0
        kI = 0
        kG = 0
        for el in self.erroa.findall('text/body/termEntry/langSet[@{http://www.w3.org/XML/1998/namespace}lang="eu"]',namespaces=namespace):
            
            eSlist = el.findall('ntig/admin[@type="entrySource"]')
            cOlist = el.findall('ntig/admin[@type="conceptOrigin"]')
            hizt = False
            ing = False
            spa = False
            for c in cOlist:
                if c.text[:2]== "es":
                    spa = True
                if c.text[:2] == "en":
                    ing = True
            for e in eSlist:
                if e.text != "000" and e.text[0] == "0":
                    hizt = True
            if hizt and ing:
                kI += 1
            if hizt and spa:
                kG += 1
            if hizt:
                k += 1
        print("k",k,"kI",kI,"kG",kG)


    def garbituTBX(self):
        jarraitu = True
        while jarraitu:
            k = 0
            for konL in self.getKontzeptuak():
                k += KontzeptuTBX(konL).garbituTBX()
            print(k)
            if k ==0:
                jarraitu = False
        
        dok = self.path+'snomed/XMLak/'+self.hierarkia+self.clinical+'.xml'
        tree = ET.ElementTree(self.erroa)
        tree.write(dok,encoding='utf-8',xml_declaration=True)
        print('hierarkiaren XMLa sortua.')

    def termNoteKonpondu(self):
        for konL in self.getKontzeptuak():
            KontzeptuTBX(konL).termNoteKonpondu()
        dok = self.path+'snomed/XMLak/'+self.hierarkia+self.clinical+'.xml'
        tree = ET.ElementTree(self.erroa)
        tree.write(dok,encoding='utf-8',xml_declaration=True)
        print('hierarkiaren XMLa sortua.')

    def adminAnitzak(self):
        for konL in self.getKontzeptuak():
            KontzeptuTBX(konL).adminAnitzak()
        dok = self.path+'snomed/XMLak/'+self.hierarkia+self.clinical+'.xml'
        tree = ET.ElementTree(self.erroa)
        tree.write(dok,encoding='utf-8',xml_declaration=True)
        print('hierarkiaren XMLa sortua.')

    def getIturburuKop(self):
        namespace={'xml':'http://www.w3.org/XML/1998/namespace'}
        #ema = Emaitza(self.hierarkia,self.clinical)
        euLanak = self.erroa.findall('text/body/termEntry/langSet[@{http://www.w3.org/XML/1998/namespace}lang="eu"]',namespaces=namespace)
        #ema.setKontzeptuakItzulita(len(euLanak))
        ordaKop = 0 #ordain kopuru totala 
        ordaKopEng = 0 #inglesetik lortutako ordain kopuru totala 
        ordaKopSpa = 0 #gaztelaniatik lortutako ordain kopuru totala 
        iturOrdEng = {}
        iturMatchEng = {}
        iturOrdSpa = {}
        iturMatchSpa = {}
        iturOrd = {}
        iturMatch = {}
        termKopEng = set()
        termKopSpa = set()
        k = 0
        for euLan in euLanak:
            ordainak = euLan.findall('ntig')
            ordaKop += len(ordainak)
            iturTer = set()
            iturTerEng = set()
            iturTerSpa = set()
            for ordain in ordainak:
                hizk = ordain.findall('admin[@type="conceptOrigin"]')
                k += len(hizk)
                eng = False
                spa = False
                for h in hizk:
                    idH = h.text[:2]
                    if idH == 'en':
                        if not eng:
                            for it in ordain.findall('admin[@type="entrySource"]'):
                                kop = iturOrdEng.get(it.text,0)
                                iturOrdEng[it.text] = kop + 1
                                iturTerEng.add(it.text)
                            ordaKopEng += 1
                            eng = True
                        termKopEng.add(h.text)

                    if idH == 'es':
                        if not spa:
                            for it in ordain.findall('admin[@type="entrySource"]'):
                                kop = iturOrdSpa.get(it.text,0)
                                iturOrdSpa[it.text] = kop + 1
                                iturTerSpa.add(it.text)
                            ordaKopSpa += 1
                            spa = True
                        termKopSpa.add(h.text)
                for it in ordain.findall('admin[@type="entrySource"]'):
                    kop = iturOrd.get(it.text,0)
                    iturOrd[it.text] = kop + 1
                    iturTer.add(it.text)
            for it in iturTer:
                kop = iturMatch.get(it,0)
                iturMatch[it] = kop + 1
            for it in iturTerEng:
                kop = iturMatchEng.get(it,0)
                iturMatchEng[it] = kop + 1
            for it in iturTerSpa:
                kop = iturMatchSpa.get(it,0)
                iturMatchSpa[it] = kop + 1
        print('k:',k)
        print('Ordain kopurua danera:',ordaKop,'Eng:',ordaKopEng,'Spa:',ordaKopSpa)
        print('Termino kopurua denera:',len(termKopEng)+len(termKopSpa),'Eng:',len(termKopEng),'Spa:',len(termKopSpa))
        print('Kontzeptu kopurua denera:',len(euLanak))
        print('Ingelesa:')
        for it in Iturburua:
            kodea = Iturburua[it][0]
            ordK = iturOrdEng.get(kodea,0)
            matK = iturMatchEng.get(kodea,0)
            print(it,'ordain:',ordK,'match',matK)
        print('\nGaztelania:')
        for it in Iturburua:
            kodea = Iturburua[it][0]
            ordK = iturOrdSpa.get(kodea,0)
            matK = iturMatchSpa.get(kodea,0)
            print(it,'ordain:',ordK,'match',matK)
        print('\nDenera:')
        for it in Iturburua:
            kodea = Iturburua[it][0]
            ordK = iturOrd.get(kodea,0)
            matK = iturMatch.get(kodea,0)
            print(it,'ordain:',ordK,'match',matK)
    
    def getTermino(self,terminoId):
        #terminoaren ID-a emanda, terminoa bera itzultzen du (TerminoTBXSnomed klasea)
        term = self.erroa.find('text/body/termEntry/langSet/ntig[@id="'+terminoId+'"]')
        if term:
            return TerminoTBXSnomed(term)
        else:
            return None

    def getTerminoak(self,hizkuntza):
        #emandako hizkuntzaren termino guztiak itzultzen ditu
        namespace={'xml':'http://www.w3.org/XML/1998/namespace'}
        return self.erroa.findall('text/body/termEntry/langSet[@{http://www.w3.org/XML/1998/namespace}lang="'+hizkuntza+'"]/ntig',namespaces=namespace)

    def pareaJaso(self,terminoa):
        #emandako terminoari dagokion termEntry osoa itzultzen du (ordain guztiak hizkuntza guztietan)
        namespace={'xml':'http://www.w3.org/XML/1998/namespace'}
        for termEntry in self.erroa.findall('text/body/termEntry'):
            for lagTerm in termEntry.findall('langSet/ntig/termGrp/term',namespaces=namespace):
                lag = lagTerm.text
                if lag and lag.lower() == terminoa.lower():
                    return termEntry

    def getItzuliGabeak(self,hizkuntza):
        #itzuli gabeko terminoen zerrenda itzultzen du (TerminoTBXSnomed-ak)
        itzGab = []
        namespace={'xml':'http://www.w3.org/XML/1998/namespace'}
        for termEntry in self.erroa.findall('text/body/termEntry'):
            engak = termEntry.findall('langSet[@{http://www.w3.org/XML/1998/namespace}lang="'+hizkuntza+'"]/ntig',namespaces=namespace)
            engHash = {}
            for eng in engak:
                tts = TerminoTBXSnomed(eng)
                ida = eng.get('id')
                engHash[ida] = tts
            eusak = termEntry.findall('langSet[@{http://www.w3.org/XML/1998/namespace}lang="eu"]/ntig',namespaces=namespace)
            for eus in eusak:
                for coN in eus.findall('admin[@type="conceptOrigin"]'):
                    co = coN.text
                    if co in engHash:
                        del engHash[co]
            for key,value in engHash.items():
                itzGab.append(value)
        return itzGab

    def getItzuliakSinonimoak(self,hizkuntza):
        itzuliak = {}
        for termEntry in self.erroa.findall('text/body/termEntry'):
            eusak = termEntry.findall('langSet[@{http://www.w3.org/XML/1998/namespace}lang="eu"]/ntig')
            if eusak:
                eusSet = set()
                for eus in eusak:
                    eusText = eus.findtext('termGrp/term')
                    if eus.findtext('termGrp/termNote[@type="usageNote"]') != "Sensitive":
                        eusText = eusText.lower()
                    eusSet.add(eusText)
                engak = termEntry.findall('langSet[@{http://www.w3.org/XML/1998/namespace}lang="'+hizkuntza+'"]/ntig')
                for eng in engak:
                    engText = eng.findtext('termGrp/term')
                    if eng.findtext('termGrp/termNote[@type="usageNote"]') != "Sensitive":
                        engText = engText.lower()
                    lag = itzuliak.get(engText,set())
                    itzuliak[engText] = eusSet.union(lag)
        return itzuliak

    def getItzuliak(self,hizkuntza):
        itzuliak = {}
        for termEntry in self.erroa.findall('text/body/termEntry'):
            eusak = termEntry.findall('langSet[@{http://www.w3.org/XML/1998/namespace}lang="eu"]/ntig')
            if eusak:
                engak = termEntry.findall('langSet[@{http://www.w3.org/XML/1998/namespace}lang="'+hizkuntza+'"]/ntig')
                engIdak = {}
                for eng in engak:
                    eId = eng.get('id')
                    engText = eng.findtext('termGrp/term')
                    if eng.findtext('termGrp/termNote[@type="usageNote"]') != "Sensitive":
                        engText = engText.lower()
                    engIdak[eId] = engText
                for eus in eusak:
                    eusO = OrdainTBXSnomed(eus)
                    for it in eusO.getConceptOrigin():
                        if it[:2] == 'en':
                            lag = itzuliak.get(engIdak[it],set())
                            lag.add(eusO.getKarKatea())
                            itzuliak[engIdak[it]] = lag
        return itzuliak

    def getMorfologiakBakarrik(self):
        kont = 0
        namespace={'xml':'http://www.w3.org/XML/1998/namespace'}
        for termEntry in self.erroa.findall('text/body/termEntry'):
            eusak = termEntry.findall('langSet[@{http://www.w3.org/XML/1998/namespace}lang="eu"]/ntig',namespaces=namespace)
            for eus in eusak:
                eSak = eus.findall('admin[@type="entrySource"]')
                if len(eSak) == 1 and eSak[0].text == '101':
                    kont += 1
        return kont