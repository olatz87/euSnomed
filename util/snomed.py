#!/usr/bin/python3
# -*- coding: utf-8 -*-
import subprocess,codecs,glob
from util.snomedtbx import SnomedTBX
from util.enumeratuak import Hierarkia,SemanticTag
from util.klaseak import *

class Snomed:

        
        
    def hierarkiakKargatu(self,engPath,spaPath):
        print("Ingelesezko SNOMED CT kargatzen")
        self.lanZer_en = {}
        if "RF1Release" in engPath:
            path = "Terminology/Content/"
        else:
            dist = "Snapshot"
            path = dist+"/Terminology/"
            pathL = dist+"/Refset/Language/"
            fitxL = glob.glob(engPath+pathL+'*Language*.txt')[0]
            self.lanZer_en = LanguageList(fitxL)
            print("Language kargatuta",len(self.lanZer_en.zerrenda))
        fitxD = glob.glob(engPath+path+'*Description*.txt')[0]
        fitxR = glob.glob(engPath+path+'*Relationship*.txt')[0]
        fitxC = glob.glob(engPath+path+'*Concept*.txt')[0]
        self.konZer_en = ConceptList(fitxC)
        print("Kontzeptuak kargatuta",len(self.konZer_en.zerrenda))
        self.desZer_en = DescriptionList(fitxD,self.konZer_en,self.lanZer_en)
        print("Deskribapenak kargatuta",len(self.desZer_en.zerrenda))
        self.erlZer_en = RelationshipList(fitxR,self.konZer_en,True)
        print("Erlazioak kargatuta",len(self.erlZer_en.umeZerrenda))
        self.erlZer_en.hierarkiakEsleitu()
        print("Hierarkiak kargatuta",len(self.erlZer_en.hierarkiak))


        print("Gaztelaniazko SNOMED CT kargatzen")
        self.lanZer_es = {}
        if "RF1Release" in spaPath:
            path_es = "Terminology/Content/"
        else:
            dist_es = "Snapshot"
            path_es = dist_es+"/Terminology/"
            pathL_es = dist_es+"/Refset/Language/"
            fitxL_es = glob.glob(spaPath+pathL_es+'*Language*.txt')[0]
            self.lanZer_es = LanguageList(fitxL_es)
            print("Language kargatuta",len(self.lanZer_es.zerrenda))
        fitxD = glob.glob(spaPath+path_es+'*Description*.txt')[0]
        self.konZer_es = ConceptList(fitxC)
        print("Kontzeptuak kargatuta",len(self.konZer_es.zerrenda))
        self.desZer_es = DescriptionList(fitxD,self.konZer_es,self.lanZer_es)
        print("Deskribapenak kargatuta",len(self.desZer_es.zerrenda))

        

    def __init__(self,berria,path):
        self.path = path
        if berria:
            engPath = '/sc01a7/users/ixamed/BaliabideSemantikoak/SnomedCT_RF2Release_INT_20150731/'
            spaPath = '/sc01a7/users/ixamed/BaliabideSemantikoak/SnomedCT_SpanishRelease-es_INT_20151031/RF2Release/'
            # self.defTypeBanatu(engPath,spaPath,path)
            # #p1 = subprocess.call(['perl '+path+'defTypeBanatu.pl '+engPath+' '+spaPath],shell=True)
            # print('defTypeBanatu eginda!')
            # self.hierarkiakBanatu()
            self.hierarkiakKargatu(engPath,spaPath)
            snoTBX = SnomedTBX(self.path)
            snoTBX.xmltanBanatu(self.konZer_en,self.konZer_es)
            print('Snomed XMLtan banatua!')

    
    def kargatu(self,hie,cli=""):
        self.hierarkia = hie
        self.snoTBX = SnomedTBX(self.path,hie,cli)

    def getHierarkia(self):
        return self.hierarkia

    def mapGNS(self,ema):
        with codecs.open(self.path+'/baliabideak/gns10parekatzea.txt',encoding='utf-8') as fitxPar:
            eusk = {}
            for ler in fitxPar:
                ban = ler.split('\t')
                if len(ban) >= 4 and ban[3] != '':
                    eusk[ban[0]] = ban[3]
        with codecs.open(self.path+'/baliabideak/gns10map.txt',encoding='utf-8') as fitx:
            for ler in fitx:
                ban = ler.split('\t')
                gnsID = ban[11]
                if gnsID in eusk:
                    kon = self.snoTBX.getKontzeptu(ban[5])
                    if kon:
                        ema.gehiAlgoritmoa('mapaketa','ordain')
                        kon.eguneratuGNS(eusk[gnsID],gnsID)

    def getKontzeptuak(self):
        return self.snoTBX.getKontzeptuak()

    def gorde(self):
        self.snoTBX.gorde()

    def getItzulitakoKontzeptuKop(self):
        return self.snoTBX.getItzulitakoKontzeptuKop()

    def getItzulitakoOrdainKop(self):
        return self.snoTBX.getItzulitakoOrdainKop()
    
    def getItzulitakoTerminoKop(self):
        return self.snoTBX.getItzulitakTerminoKop()

    def getSemanticTagKop(self):
        return self.snoTBX.getSemanticTagKop()

    def getKontzeptuIdak(self):
        return self.snoTBX.getKontzeptuIdak()
        
    def getTerminoak(self,hizkuntza):
        return self.snoTBX.getTerminoak(hizkuntza)

    def pareaJaso(self,terminoa):
        return self.snoTBX.pareaJaso(terminoa)

    def getItzuliGabeak(self,hizkuntza):
        return self.snoTBX.getItzuliGabeak(hizkuntza)

    def getItzuliakSinonimoak(self,hizkuntza):
        return self.snoTBX.getItzuliak(hizkuntza)

    def getItzuliak(self,hizkuntza,jatorria):
        """
        
        """
        return self.snoTBX.getItzuliak(hizkuntza,jatorria)

    def getMorfologiakBakarrik(self):
        return self.snoTBX.getMorfologiakBakarrik()

    def getIturburuKop(self):
        return self.snoTBX.getIturburuKop()

    def getIturburutik(self):
        return self.snoTBX.getIturburutik()

    def getTerminoTBX(self,dId):
        """
        terminoaren identifikadorea emanda (dId), terminoa bera itzultzen du TerminoTBXSnomed klasekoa
        """
        return self.snoTBX.getTerminoTBX(dId)

    def kontzeptuaJaso(self,cId):
        """
        ElementTree bat itzultzen du: kontzeptua
        """
        return self.snoTBX.getKontzeptua(cId) #ElementTree bat itzultzen du

    def getKontzeptu(self,cId):
        """
        KontzeptuTBX bat itzultze du: kontzeptua
        """
        return self.snoTBX.getKontzeptu(cId) #KontzeptuTBX itzultzen du
