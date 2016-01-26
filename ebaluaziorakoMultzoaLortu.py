#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys,os,getopt,datetime,codecs
from util.itzuldb import ItzulDB
from util.enumeratuak import Hierarkia
from util.emaitzak import Emaitzak
from util.snomed import Snomed
from util.terminotbxsnomed import TerminoTBXSnomed
from util.ordaintbxsnomed import OrdainTBXSnomed
from util.kontzeptutbx import KontzeptuTBX
from util.snomedtbx import SnomedTBX
import scriptak.morfosemantika as MS
import scriptak.pharma_itzuli as PI
import random

def kontzeptuakBanatu(path,simple):

    Iturburua = {
        '000' : 'MapGNS',
        '001' : 'Elhuyar',
        '002' : 'ZT',
        '003' : 'Erizaintza',
        '004' : 'AdminSan',
        '005' : 'Anatomia',
        '006' : 'GNS10',
        '007' : 'EuskalTerm',
        '008' : 'Drogak',
        '009' : 'Sexologia',
        '101' : 'Morfologia',
        '102' : 'Sintaxia',
        '200' : 'Matxin',
        '300' : 'Medikuak'}

    out = path+'itzulpenak/kontzeptuId'
    HieLau = ['CLINICAL_DIS','CLINICAL_FIN','BODYSTRUCTURE','PROCEDURE']
    snomed = Snomed(False,path)
    if simple:
        out += 'Sinpleak'
    with codecs.open(out+'_bai.txt','w',encoding='utf-8') as fitx:
        fitx.write('')
    with codecs.open(out+'_ez.txt','w',encoding='utf-8') as fitx:
        fitx.write('')
    for hie in HieLau:
        cli = '_ald'
        print(hie+cli,end='\t')
        snomed.kargatu(hie,cli)
        print('Snomed kargatuta')
        for kontzeptu in snomed.getKontzeptuak():
            konTBX = KontzeptuTBX(kontzeptu)
            irtStr = konTBX.getKontzeptuId()+'%%%'+konTBX.getFSN()+'%%%'
            irtEz = konTBX.getKontzeptuId()+'%%%'+konTBX.getFSN()+'\n'
            eusak = konTBX.getTerminoak('eu')
            engak = konTBX.getTerminoak('en')
            spaak = konTBX.getTerminoak('es')
            simp = False
            desId = {}
            simpId = set()
            for eng in engak:
                engO = TerminoTBXSnomed(eng)
                term = engO.getTerminoa()
                if " " not in term:
                    simpId.add(engO.getId())
                irtStr += term+'&&&'
                desId[engO.getId()] = term
            irtStr = irtStr[:-3] + '%%%'
            if not spaak:
                irtStr += '&&&'
            for spa in spaak:
                spaO = TerminoTBXSnomed(spa)
                term = spaO.getTerminoa()
                irtStr += term+'&&&'
                desId[spaO.getId()] = term
            irtStr = irtStr[:-3] + '%%%'
            itLag = ''
            coLag = ''
            if eusak:
                for eus in eusak:
                    eusO = OrdainTBXSnomed(eus)
                    term = eusO.getKarKatea()
                    itak = eusO.getIturburua()
                    coak = eusO.getConceptOrigin()
                    irtStr += term+'&&&'
                    for it in itak:
                        itLag += Iturburua[it]+','
                    itLag = itLag[:-1]+'&&&'
                    for co in coak:
                        if co in simpId:
                            simp = True
                        if co in desId:
                            coLag += desId[co]+','
                        elif co[:3] == 'gns':
                            coLag += 'GNS,'
                    coLag = coLag[:-1]+'&&&'
            irtStr = irtStr[:-3] + '%%%'+itLag[:-3]+'%%%'+coLag[:-3]+'\n'
            if not simple:
                if eusak:
                    with codecs.open(out+'_bai.txt','a',encoding='utf-8') as fitx:
                        fitx.write(irtStr)
                else:
                    with codecs.open(out+'_ez.txt','a',encoding='utf-8') as fitx:
                        fitx.write(irtEz)
            else:
                if simp:
                    if eusak:
                        with codecs.open(out+'_bai.txt','a',encoding='utf-8') as fitx:
                            fitx.write(irtStr)
                    else:
                        with codecs.open(out+'_ez.txt','a',encoding='utf-8') as fitx:
                            fitx.write(irtEz)
    return out
def auzazAukeratu(out):
    print("auzaz aukeratzen")
    irt = '../../../public_html/eusnomed/baliabideak/'
    with codecs.open(out+'_bai.txt','r',encoding='utf-8') as fitx:
        kontzeptuak = fitx.readlines()
    random.shuffle(kontzeptuak)
    am = 170
    z1 = 100
    z2 = 100
    am_arr = []
    z1_arr = []
    z2_arr = []
    mor = 0
    hiz = 0
    for kon in kontzeptuak:
        kon = kon.strip()
        
        if len(am_arr) < am:
            am_arr.append(kon)
        elif len(z1_arr) < z1:
            z1_arr.append(kon)
        elif len(z2_arr) < z2:
            z2_arr.append(kon)
        else:
            break
        if "Morfologia" in kon:
            mor += 1
        if ("Elhuyar" in kon) or ("ZT" in kon) or ("Erizaintza" in kon) or ("AdminSan" in kon) or ("Anatomia" in kon) or ("GNS10" in kon) or ("EuskalTerm" in kon) or ("Sexologia" in kon) or ("Drogak" in kon):
            hiz += 1
    print(len(am_arr),len(z1_arr),len(z2_arr))
    print(mor,hiz)
    if mor < 200 or hiz < 100:
        print("Berriro saiatzen:",mor)
        auzazAukeratu(out)
    else:
        with codecs.open(irt+'zuz1.txt','w',encoding='utf-8') as fitx:
            fitx.write('\n'.join(am_arr)+'\n'.join(z1_arr))
        with codecs.open(irt+'zuz2.txt','w',encoding='utf-8') as fitx:
            fitx.write('\n'.join(am_arr)+'\n'.join(z2_arr))

def main(argv):
    path = '../../euSnomed/'
    simple = False
    try:
        opts, args = getopt.getopt(argv,"hp:o:s",["path=","output=","simple"])
    except getopt.GetoptError:
        print('python3 euSnomed.py -p <path> -s <snomedBool> -i <itzulDBBool>')
        sys.exit(2)
    for opt, arg in opts:
        if opt =='-h':
            print('python3 euSnomed.py -p <path> -s <snomedBool> -i <itzulDBBool>')
            sys.exit()
        elif opt in ("-p","--path"):
            path = arg
        elif opt in ("-o","--output"):
            itzulBool = arg
        elif opt in ('-s','--simple'):
            simple = True
    out = kontzeptuakBanatu(path,simple)
    auzazAukeratu(out)
                  

if __name__ == "__main__":
    main(sys.argv[1:])

