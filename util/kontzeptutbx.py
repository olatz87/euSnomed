#!/usr/bin/python3
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import unidecode
from util.ordaintbxitzuldb import OrdainTBXItzulDB
from util.ordaintbxsnomed import OrdainTBXSnomed
from util.enumeratuak import Iturburua

class KontzeptuTBX:
    
    def __init__(self,kontzep):
        self.kontzeptu = kontzep #termEntry
        
    def getKontzeptu(self):
        return self.kontzeptu

    def setKontzeptu(self,kontzep):
        self.kontzeptu = kontzep

    def getPreferredTerm(self,hizkuntza):
        for terminoa in self.getTerminoak(hizkuntza):
            for child in terminoa: 
                if child.tag == 'termNote' and child.get('type') == 'administrativeStatus' and child.text == 'preferredTerm-adm-sts':
                    return terminoa

    def proba():
        tree = ET.parse('../snomed/XMLak/SOCIAL.xml')
        erroa = tree.getroot()
        te = erroa.find('text/body/termEntry')
        return KontzeptuTBX(te)
        

    def eguneratuGNS(self,term, gnsID):
        term = term.strip()
        euLanSet = ET.SubElement(self.kontzeptu, 'langSet')
        euLanSet.set('xml:lang','eu')
        euId = KontzeptuTBX.sortuId()
        ntig = ET.SubElement(euLanSet,'ntig',id='eu'+euId)
        tG = ET.SubElement(ntig,'termGrp')
        termEl = ET.SubElement(tG,'term').text = term
        sK = ET.SubElement(ntig,'admin',type='sortKey').text = unidecode.unidecode(term)
        #ews = ET.SubElement(ntig,'admin',type='elementWorkingStatus').text = 'workingElement'
        eS = ET.SubElement(ntig,'admin',type='entrySource').text = Iturburua['MapGNS'][0]
        cO = ET.SubElement(ntig,'admin',type='conceptOrigin').text = 'gns'+gnsID
        rC = ET.SubElement(ntig,'descrip',type='reliabilityCode').text = '5'
        termNote = ET.SubElement(ntig,'termNote',type='administrativeStatus').text = 'admittedTerm-adm-sts'
        uN = ET.SubElement(ntig,'termnote',type='usageNote').text = 'Unknown'
        #Transaction informazioa hemen joango litzateke...
        
    def getTerminoak(self,hizkuntza):
        namespace={'xml':'http://www.w3.org/XML/1998/namespace'}
        return self.kontzeptu.findall('langSet[@xml:lang="'+hizkuntza+'"]/ntig',namespaces=namespace)

    def getKontzeptuId(self):
        return self.kontzeptu.get('id')

    def eguneratu(self,ordList,elNtig,ema):
        namespace={'xml':'http://www.w3.org/XML/1998/namespace'}
        euLanSet = self.kontzeptu.find('langSet[@xml:lang="eu"]',namespaces=namespace)
        if euLanSet:
            b = True
        else:
            euLanSet = ET.SubElement(self.kontzeptu,'langSet')
            euLanSet.set('xml:lang','eu')
            b = False
        zahList = {} #key = term.text, value = ntig
        for euntig in euLanSet.findall('ntig'):
            zahList[euntig.findtext('termGrp/term')] = euntig
        #hizPar =[zt,anatomia,erizaintza,gns10,elhuyar,euskalterm,adm,sexologia,drogak]
        hizPar = [False,False,False,False,False,False,False,False,False,False]
        mor = False
        erdId = elNtig.get('id')
        hizkuntza = erdId[:2]
        for elTig in ordList:
            ordainI = OrdainTBXItzulDB(elTig)
            itList = ordainI.getIturburua()
            for it in itList:
                if it != 'Morfologia':
                    ema.gehiHiztegia(it,'ordain',hizkuntza)
                    hizPar[Iturburua[it][1]-1] = True
            if True in hizPar :
                ema.gehiAlgoritmoa('hiztegia','ordain',hizkuntza)
            if 'Morfologia' in itList:
                ema.gehiAlgoritmoa('morfo','ordain')
                mor = True
            elTerm = elTig.findtext('term')
            if b and elTerm in zahList:
                ordainS = OrdainTBXSnomed(zahList[elTerm])
                stList = ordainS.getIturburua()
                for it in itList:
                    if it not in stList:
                        ordainS.gehitu('admin','entrySource',Iturburua[it][0])
                cOList = ordainS.getConceptOrigin()
                if erdId not in cOList:
                    ordainS.gehitu('admin','conceptOrigin',erdId)
                rl = ordainI.getReliabilityCode()
                if int(ordainS.getReliabilityCode()) < int(rl):
                    ordainS.setReliabilityCode(rl)
                cS = ordainI.getUsageNote()
                if cS == 'Sensitive' or ordainS.getUsageNote() == 'Unknown':
                    ordainS.setUsageNote(cS)
            else:
                ntig = ET.SubElement(euLanSet,'ntig',id='eu'+KontzeptuTBX.sortuId())
                tG = ET.SubElement(ntig,'termGrp')
                termEl = ET.SubElement(tG,'term').text = elTerm
                sK = ET.SubElement(ntig,'admin',type='sortKey').text = unidecode.unidecode(elTerm)
                #ews = ET.SubElement(ntig,'admin',type='elementWorkingStatus').text = 'workingElement'
                for it in itList:
                    eS = ET.SubElement(ntig,'admin',type='entrySource').text = Iturburua[it][0]
                cO = ET.SubElement(ntig,'admin',type='conceptOrigin').text = erdId
                rC = ET.SubElement(ntig,'descrip',type='reliabilityCode').text = ordainI.getReliabilityCode()
                termNote = ET.SubElement(ntig,'termNote',type='administrativeStatus').text = 'admittedTerm-adm-sts'
                uN = ET.SubElement(ntig,'termnote',type='usageNote').text = ordainI.getUsageNote()
        for i in range(-1,len(hizPar)-1):
            if hizPar[i+1]:
                ema.gehiHiztegia(i+1,'pare',hizkuntza)
        if True in hizPar :
            ema.gehiAlgoritmoa('hiztegia','pare',hizkuntza)
        if mor:
            ema.gehiAlgoritmoa('morfo','pare')
        
    ns = 100
    @staticmethod
    def sortuId():
        fnF = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
		[1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
		[0,0,0,0,0,0,0,0,0,0],
		[0,0,0,0,0,0,0,0,0,0],
		[0,0,0,0,0,0,0,0,0,0],
		[0,0,0,0,0,0,0,0,0,0],
		[0,0,0,0,0,0,0,0,0,0],
		[0,0,0,0,0,0,0,0,0,0]]
        for i in range(2,8):
            for j in range(0,10):
                fnF[i][j] = fnF[i-1][fnF[1][j]]
        Dihedral = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
		[1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
		[2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
		[3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
		[4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
		[5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
		[6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
		[7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
		[8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
                [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]]
        InverseD5 = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9 ]
        namespace = str(KontzeptuTBX.ns)
        partition = '01'
        KontzeptuTBX.ns += 1
        check = 0
        idPar = namespace+partition
        for i in range(len(idPar),0,-1):
            i2 = i-1
            kk = (len(idPar)-i2)%8
            kkk = int(idPar[i2])
            k = fnF[kk][kkk]
            check = Dihedral[check][k]
            checkDigit = str(InverseD5[check])
        return namespace+partition+checkDigit


    def garbituTBX(self):
        namespace={'xml':'http://www.w3.org/XML/1998/namespace'}
        lanSet = self.kontzeptu.findall('langSet[@xml:lang="eu"]',namespaces=namespace)
        if len(lanSet) > 1:
            lan1 = lanSet[0]
            lan2 = lanSet[1]
            self.kontzeptu.remove(lan2)
            zahList = {} #key = term.text, value = ntig
            for euntig in lan1.findall('ntig'):
                t = euntig.findtext('termGrp/term')
                zahList[t] = euntig
            for euntig in lan2.findall('ntig'):
                elTerm = euntig.findtext('termGrp/term')
                if elTerm in zahList:
                    ordainS = OrdainTBXSnomed(zahList[elTerm])
                    ordainB = OrdainTBXSnomed(euntig)
                    stList = ordainS.getIturburua()
                    itList = ordainB.getIturburua()
                    for it in itList:
                        if it not in stList:
                            ordainS.gehitu('admin','entrySource',it)
                    cOList = ordainS.getConceptOrigin()
                    erdIdList = ordainB.getConceptOrigin()
                    for erdId in erdIdList:
                        if erdId not in cOList:
                            ordainS.gehitu('admin','conceptOrigin',erdId)
                    rl = ordainB.getReliabilityCode()
                    if int(ordainS.getReliabilityCode()) < int(rl):
                        ordainS.setReliabilityCode(rl)
                    cS = ordainB.getUsageNote()
                    if cS == 'Sensitive' or ordainS.getUsageNote() == 'Unknown':
                        ordainS.setUsageNote(cS)
                else:
                    lan1.append(euntig)
                    
            return 1
        else:
            return 0
