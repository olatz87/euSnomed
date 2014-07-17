#!/usr/bin/python3
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
from util.terminotbx import TerminoTBX

class TerminoTBXSnomed(TerminoTBX):
    def __init__(self,term):
        super().__init__(term)
    
    def getTerminoa(self):
        return self.term.findtext('termGrp/term')
        
    def getAdmnStatus(self):
        return self.term.findtext('termGrp/termNote[@type="administrativeStatus"]')

    
