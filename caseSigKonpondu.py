#!/usr/bin/python3
# -*- coding: utf-8 -*-

from util.snomedTBX import SnomedTBX
#from util.enumeratuak import Hierarkia
from util.enumeratuak import CaseSignificance

Hierarkia = ["ORGANISM","QUALIFIER","SITUATION","SPECIAL"]

for hie in Hierarkia:
    i = 1
    cli = ['','']
    if hie == 'CLINICAL':
        i = 2
        cli = ['_FIN','_DIS']
    for j in range(0,i):
        path = '/home/olatz/Dropbox/Doktoretza/euSnomed/'
        sno = SnomedTBX(path,hie,cli[j]+'_ald')
        print(hie,cli[j])
        caseak = {}
        presyn = ['_pre_','_syn_']
        for y in range(0,2):
            with open(path+'snomed/hierarkiak/'+hie+cli[j]+presyn[y]+'eng.txt') as eng:
                print(hie+presyn[y]+'eng.txt')
                for line in eng:
                    line = line.strip()
                    linelag = line.split('\t')
                    caseak['en'+linelag[0]] = linelag[8]
        for y in range(0,2):
            with open(path+'snomed/hierarkiak/'+hie+cli[j]+presyn[y]+'spa.txt') as spa:
                print(hie+presyn[y]+'spa.txt')
                for line in spa:
                    line = line.strip()
                    linelag = line.split('\t')
                    caseak['es'+linelag[0]] = linelag[8]
        for tId,caseSig in caseak.items():
            term = sno.getTermino(tId)
            for name,code in CaseSignificance.items():
                if code == caseSig:
                    term.setCaseSignificance(name)
        sno.gorde()
