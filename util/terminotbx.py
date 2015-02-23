#!/usr/bin/python3
# -*- coding: utf-8 -*-
#import xml.etree.ElementTree as ET
from lxml import etree as ET
from util.tbx import TBX

class TerminoTBX(TBX):
    
    def __init__(self,term):
        super().__init__(term)
    
