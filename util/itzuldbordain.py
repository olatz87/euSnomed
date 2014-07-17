#!/usr/bin/python3
# -*- coding: utf-8 -*-

class ItzulDBOrdain:

    #hiztegiZerrenda = set()
    #pOS = set()
    #caseSignificance = CaseSignificance.Unknown
    #termType = TermType.Unknown
    #rC = 0
    
    def __init__(self,hiztegia=None,caseSig='Unknown',pOS=None,termTy='Unknown',rC=0):
        self.hiztegiZerrenda = set()
        if hiztegia:
            self.hiztegiZerrenda.add(hiztegia)
        self.pOS = set()       
        if pOS:
            self.pOS.add(pOS)
        self.caseSignificance = caseSig
        self.termType = termTy
        self.reliabilityCode = rC

    def gehituDatuak(self,hiztegia,caseSig,pOS,tT,rC):
        self.hiztegiZerrenda.add(hiztegia)
        self.pOS.update(pOS)
        if self.caseSignificance == 'Unknown':
            self.caseSignificance = caseSig
        elif caseSig == 'Sensitive':
            self.caseSignificance = caseSig
        if self.termType == 'Unknown':    
            self.termType = tT
        if self.reliabilityCode < rC:
            self.reliabilityCode = rC

    def getHiztegiZerrenda(self):
        return self.hiztegiZerrenda

    def getPOS(self):
        return self.pOS

    def getReliabilityCode(self):
        return self.reliabilityCode

    def getCaseSignificance(self):
        return self.caseSignificance

    def getTermType(self):
        return self.termType
        
    def setPOS(self,pos):
        self.pOS.add(pos)
