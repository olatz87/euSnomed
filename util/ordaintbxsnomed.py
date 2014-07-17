#!/usr/bin/python3
# -*- coding: utf-8 -*-
import  xml.etree.ElementTree as ET
from util.ordaintbx import OrdainTBX

class OrdainTBXSnomed(OrdainTBX):
    def __init__(self,ntig):
        super().__init__(ntig)
  
    def getKarKatea(self):
        return self.ordain.findtext('termGrp/term')
    
