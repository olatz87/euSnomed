#!/usr/bin/python3
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
from util.enumeratuak import CaseSignificance

class TBX:
    
    def __init__(self,term):
        self.term = term

    def getId(self):
        return self.term.get('id')
 

    def getNormalizatua(self):
        return self.term.findtext('admin[@type="sortKey"]')

    def getUsageNote(self):
        return self.term.findtext('termNote[@type="usageNote"]')

