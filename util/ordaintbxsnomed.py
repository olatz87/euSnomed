#!/usr/bin/python3
# -*- coding: utf-8 -*-
import  xml.etree.ElementTree as ET
from util.ordaintbx import OrdainTBX

class OrdainTBXSnomed(OrdainTBX):
    def __init__(self,ntig):
        super().__init__(ntig)
  
    def getKarKatea(self):
        if self.getUsageNote() != "Sensitive":
            return self.ordain.findtext('termGrp/term').lower()
        else:
            return self.ordain.findtext('termGrp/term')
    
    def setUsageNote(self,cs):
        self.ordain.find('termGrp/termNote[@type="usageNote"]').text = cs

    def getUsageNote(self):
        return self.ordain.findtext('termGrp/termNote[@type="usageNote"]')

    def getPOS(self):
        return self.ordain.findall('termGrp/termNote[@type="partOfSpeech"]')
