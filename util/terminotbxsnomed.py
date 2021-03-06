#!/usr/bin/python3
# -*- coding: utf-8 -*-
#import xml.etree.ElementTree as ET
from lxml import etree as ET
from util.tbx import TBX

class TerminoTBXSnomed(TBX):
    #ntig elementu bat
    def __init__(self,term):
        super().__init__(term)
    
    def getTerminoa(self):
        return self.term.findtext('termGrp/term')
        
    def getAdmnStatus(self):
        return self.term.findtext('termGrp/termNote[@type="administrativeStatus"]')

    def getUsageNote(self):
        return self.term.findtext('termGrp/termNote[@type="usageNote"]')


    def setCaseSignificance(self,caseSig):
        self.term.find('termGrp/termNote[@type="usageNote"]').text = caseSig

    def getKontzeptua(self):
        return self.term.getparent().getparent()

    def getHizkuntza(self):
        return self.getId()[:2]
