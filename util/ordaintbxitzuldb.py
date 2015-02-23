#!/usr/bin/python3
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
from util.ordaintbx import OrdainTBX

class OrdainTBXItzulDB(OrdainTBX):

    def __init__(self,elTig):
        super().__init__(elTig)

    def getKarKatea(self):
        return self.ordain.findtext('term')

    def setUsageNote(self,cs):
        self.ordain.find('termNote[@type="usageNote"]').text = cs

    def getUsageNote(self):
        return self.ordain.findtext('termNote[@type="usageNote"]')
