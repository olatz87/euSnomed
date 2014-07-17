#!/usr/bin/python3
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
from util.ordaintbx import OrdainTBX

class OrdainTBXItzulDB(OrdainTBX):

    def __init__(self,elTig):
        super().__init__(elTig)

    def getKarKatea(self):
        return self.ordain.findtext('term')
