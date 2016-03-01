#!/usr/bin/python3
# -*- coding: utf-8 -*-
#import xml.etree.ElementTree as ET
from lxml import etree as ET
from util.enumeratuak import Iturburua,CaseSignificance
from util.tbx import TBX
from copy import deepcopy


class OrdainTBX(TBX):

    def __init__(self,elTig):
        super().__init__(elTig)
        self.ordain = elTig

    def getIturburua(self):
        itak = []
        for e in self.ordain.findall('admin[@type="entrySource"]'):
            itak.append(deepcopy(e.text))
        return itak

    def getReliabilityCode(self):
        return self.ordain.findtext('descrip[@type="reliabilityCode"]')

    def getConceptOrigin(self):
        coak = []
        for e in self.ordain.findall('admin[@type="conceptOrigin"]'):
            coak.append(deepcopy(e.text))
        return coak

    def setReliabilityCode(self,rl):
        self.ordain.find('descrip[@type="reliabilityCode"]').text = rl
            

    def gehitu(self,elem,attVal,text):
        if type(elem) == str:
            ET.SubElement(self.ordain,elem,type=attVal).text = text
        elif type(elem) == ET.Element:
            self.ordain.append(deepcopy(elem))

    def getPatroia(self):
        patak = []
        for e in self.ordain.findall('admin[@type="originatingDatabase"]'):
            patak.append(deepcopy(e.text))
        return patak
