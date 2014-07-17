#!/usr/bin/python3
# -*- coding: utf-8 -*-
import subprocess,codecs
from util.snomedtbx import SnomedTBX
from util.enumeratuak import Hierarkia,SemanticTag

class Snomed:


    def isaKargatu(self,path):
        #SNOMED CT-ren IS-a erlazioak kargatu egiten ditu eta hash batean sartuta itzultzen ditu, 
	# hau da, hierarkia bakoitzean aurkitzen diren kontzeptuen identifikadoreak itzultzen ditu 
        lagisaRel = {}
        with codecs.open(path+'/snomed/is_a_active.txt',encoding='utf-8') as isaRelFitx:
            for lerro in isaRelFitx:
                lag = lerro.split('\t')
                desti = lag[5]
                source = lagisaRel.get(desti,set())
                source.add(lag[4])
                #source = [lag[4]]+[source]
                lagisaRel[desti]=source
            return lagisaRel

    def jasoErrek(self,setOna,hie,isaRel,hierarkiak):
        if not setOna:
            return ''
        else:
            irte = ''
            for lag in setOna:
                if lag in hierarkiak:
                    if hierarkiak[lag] != hie:
                        print("Kontzeptu berdina bi hierarkiatan aurkitzen da "+lag+" "+hierarkiak[lag]+" vs "+name)
                else:
                    irte += lag + '\n'
                    hierarkiak[lag] = hie
                    hur = isaRel.get(lag,None)
                    irte += self.jasoErrek(hur,hie,isaRel,hierarkiak)
            return irte
                    
    def fsnBanatu(self,path):
        with codecs.open(path+'/snomed/fsn_eng_active.txt_iso') as fsnFitx:
            fsnak = {}
            for lerroa in fsnFitx:
                lerroa = lerroa.decode('utf-8').strip()
                cId = lerroa.split('\t')[4]
                fsnak[cId]=lerroa
            for hie in Hierarkia:
                with codecs.open(path+'/snomed/hierarkiak/'+hie+'_cId.txt') as cIdFitx:
                    if hie == 'CLINICAL':
                        dis = ''
                        fin = ''
                        for lerroa in cIdFitx:
                            lerroa = lerroa.decode('utf-8').strip()
                            if lerroa:
                                ida = fsnak[lerroa]
                                st = SnomedTBX.semanticTagLortu(ida.split('\t')[7])
                                if st == 'Disorder':
                                    dis += ida+'\n'
                                elif st == 'Finding':
                                    fin += ida+'\n'
                                else:
                                    print("Ez da ez Disorder ez Finding....\t"+ida)
                        with codecs.open(path+'/snomed/hierarkiak/'+hie+'_DIS_fsn.txt','w',encoding='utf-8') as fdis:
                            fdis.write(dis)
                        print(hie+"_DIS_fsn.txt sortua\t"+str(dis.count('\n')+1))
                        with codecs.open(path+'/snomed/hierarkiak/'+hie+'_FIN_fsn.txt','w',encoding='utf-8') as ffin:
                            ffin.write(fin)
                        print(hie+"_FIN_fsn.txt sortua\t"+str(fin.count('\n')+1))
                    else:
                        fsn = ''
                        for lerroa in cIdFitx:
                            lerroa = lerroa.decode('utf-8').strip()
                            if lerroa:
                                fsn += fsnak[lerroa]+'\n'
                        with codecs.open(path+'/snomed/hierarkiak/'+hie+'_fsn.txt','w',encoding='utf-8') as ffsn:
                            ffsn.write(fsn)
                        print(hie+"_fsn.txt sortua\t"+str(fsn.count('\n')+1))
                              
    def presynBanatu(self,path,presyn):
        preEnak = {}
        if presyn == 'pre':
            enfitx = path+'/snomed/pre_eng_active.txt_iso'
            esfitx = path+'/snomed/pre_spa_active.txt_iso'
            disEnfitx = '_DIS_pre_eng.txt'
            finEnfitx = '_FIN_pre_eng.txt'
            irtEnfitx = '_pre_eng.txt'
            disEsfitx ='_DIS_pre_spa.txt'
            finEsfitx = '_FIN_pre_spa.txt'
            irtEsfitx = '_pre_spa.txt'
        else:
            enfitx = path+'/snomed/syn_eng_active.txt_iso'
            esfitx = path+'/snomed/syn_spa_active.txt_iso'
            disEnfitx = '_DIS_syn_eng.txt'
            finEnfitx = '_FIN_syn_eng.txt'
            irtEnfitx = '_syn_eng.txt'
            disEsfitx ='_DIS_syn_spa.txt'
            finEsfitx = '_FIN_syn_spa.txt'
            irtEsfitx = '_syn_spa.txt'
            
        with codecs.open(enfitx,encoding='utf-8') as enPreFitx:
            for lerroa in enPreFitx:
                lerroa = lerroa.strip()
                if lerroa:
                    cId = lerroa.split('\t')[4]
                    if cId in preEnak:
                        lag = preEnak.get(cId)+'\n'+lerroa
                    else:
                        lag = lerroa
                    preEnak[cId] = lag
        preEsak = {}
        with codecs.open(esfitx,encoding='utf-8') as esPreFitx:
            for lerroa in esPreFitx:
                lerroa = lerroa.strip()
                if lerroa:
                    cId = lerroa.split('\t')[4]
                    if cId in preEsak:
                        lag = preEsak.get(cId)+'\n'+lerroa
                    else:
                        lag = lerroa
                    preEsak[cId] = lag
        for hie in Hierarkia:
            preEn = ''
            preEs = ''
            if hie == 'CLINICAL':
                with codecs.open(path+'/snomed/hierarkiak/'+hie+'_DIS_fsn.txt',encoding='utf-8') as fitx:
                    for lerroa in fitx:
                        lerroa = lerroa.strip()
                        if lerroa:
                            cId = lerroa.split('\t')[4]
                            if cId in preEnak:
                                preEn += preEnak[cId]+'\n'
                            if cId in preEsak:
                                preEs += preEsak[cId]+'\n'
                with codecs.open(path+'/snomed/hierarkiak/'+hie+disEnfitx,'w',encoding='utf-8') as fitx:
                    fitx.write(preEn)
                print(hie+disEnfitx+' sortua\t'+str(preEn.count('\n')+1))
                with codecs.open(path+'/snomed/hierarkiak/'+hie+disEsfitx,'w',encoding='utf-8') as fitx:
                    fitx.write(preEs)
                print(hie+disEsfitx+' sortua\t'+str(preEs.count('\n')+1))
                preEn = ''
                preEs = ''
                with codecs.open(path+'/snomed/hierarkiak/'+hie+'_FIN_fsn.txt',encoding='utf-8') as fitx:
                    for lerroa in fitx:
                        lerroa = lerroa.strip()
                        if lerroa:
                            cId = lerroa.split('\t')[4]
                            if cId in preEnak:
                                preEn += preEnak[cId]+'\n'
                            if cId in preEsak:
                                preEs += preEsak[cId]+'\n'
                with codecs.open(path+'/snomed/hierarkiak/'+hie+finEnfitx,'w',encoding='utf-8') as fitx:
                    fitx.write(preEn)
                print(hie+finEsfitx+' sortua\t'+str(preEn.count('\n')+1))
                with codecs.open(path+'/snomed/hierarkiak/'+hie+finEsfitx,'w',encoding='utf-8') as fitx:
                    fitx.write(preEs)
                print(hie+finEsfitx+' sortua\t'+str(preEs.count('\n')+1))
            else:
                with codecs.open(path+'/snomed/hierarkiak/'+hie+'_fsn.txt',encoding='utf-8') as fitx:
                    for lerroa in fitx:
                        lerroa = lerroa.strip()
                        if lerroa:
                            if len(lerroa.split('\t')) < 4:
                                print(lerroa)
                            cId = lerroa.split('\t')[4]
                            if cId in preEnak:
                                preEn += preEnak[cId]+'\n'
                            if cId in preEsak:
                                preEs += preEsak[cId]+'\n'
                with codecs.open(path+'/snomed/hierarkiak/'+hie+irtEnfitx,'w',encoding='utf-8') as fitx:
                    fitx.write(preEn)
                print(hie+irtEnfitx+' sortua\t'+str(preEn.count('\n')+1))
                with codecs.open(path+'/snomed/hierarkiak/'+hie+irtEsfitx,'w',encoding='utf-8') as fitx:
                    fitx.write(preEs)
                print(hie+irtEsfitx+' sortua\t'+str(preEs.count('\n')+1))
    def hierarkiakBanatu(self,path):
        isaRel = self.isaKargatu(path)
        hierarkiak = {}
        for hie in Hierarkia:
            if hie == 'METADATA':
                set1 = isaRel["900000000000454005"]
                set2 = isaRel["900000000000442005"]
                setOna = set1.union(set2)
                irteera = self.jasoErrek(setOna,hie,isaRel,hierarkiak)
                irteera += "900000000000454005\n900000000000442005"
            elif hie == 'SPECIAL':
                setOna = isaRel[Hierarkia[hie][1]]
                setOna.add("370136006")
                irteera = self.jasoErrek(setOna,hie,isaRel,hierarkiak)
                irteera += "370136006"
            else:
                setOna = isaRel[Hierarkia[hie][1]]
                irteera = self.jasoErrek(setOna,hie,isaRel,hierarkiak)
            irteera += '\n'+Hierarkia[hie][1]
            with codecs.open(path+'/snomed/hierarkiak/'+hie+'_cId.txt','w',encoding='utf-8') as fitxcId:
                fitxcId.write(irteera)
            print(hie+"_cId.txt sortua\t"+str(irteera.count('\n')+1))
        self.fsnBanatu(path)
        self.presynBanatu(path,'pre')
        self.presynBanatu(path,'syn')
        
        
    def __init__(self,berria,path):
        if berria:
            engPath = '/home/olatz/Dropbox/Doktoretza/SNOMED/SNOMED/SnomedCT_Release_INT_20140131/RF2Release/Snapshot'
            spaPath = '/home/olatz/Dropbox/Doktoretza/SNOMED/SNOMED/SnomedCT_Release-es_INT_20131031/RF2Release/Snapshot'
            #p1 = subprocess.call(['perl '+path+'defTypeBanatu.pl '+engPath+' '+spaPath],shell=True)
            print('defTypeBanatu eginda!')
            self.hierarkiakBanatu(path)
            #p2 = subprocess.call(['java -jar '+path+'hierarkiakBanatu4.3.jar '+path],shell=True)
            snoTBX = SnomedTBX(path)
            snoTBX.xmltanBanatu()
            print('Snomed XMLtan banatua!')
        self.path = path
    
    def kargatu(self,hie,cli):
        self.hierarkia = hie
        self.snoTBX = SnomedTBX(self.path,hie,cli)

    def getHierarkia(self):
        return self.hierarkia

    def mapGNS(self,ema):
        with codecs.open(self.path+'/baliabideak/gns10parekatzea.txt',encoding='utf-8') as fitxPar:
            eusk = {}
            for ler in fitxPar:
                ban = ler.split('\t')
                if len(ban) >= 4 and ban[3] != '':
                    eusk[ban[0]] = ban[3]
        with codecs.open(self.path+'/baliabideak/gns10map.txt',encoding='utf-8') as fitx:
            for ler in fitx:
                ban = ler.split('\t')
                gnsID = ban[11]
                if gnsID in eusk:
                    kon = self.snoTBX.getKontzeptu(ban[5])
                    if kon:
                        ema.gehiAlgoritmoa('mapaketa','ordain')
                        kon.eguneratuGNS(eusk[gnsID],gnsID)

    def getKontzeptuak(self):
        return self.snoTBX.getKontzeptuak()

    def gorde(self):
        self.snoTBX.gorde()

    def getItzulitakoKontzeptuKop(self):
        return self.snoTBX.getItzulitakoKontzeptuKop()

    def getItzulitakoOrdainKop(self):
        return self.snoTBX.getItzulitakoOrdainKop()
    
    def getItzulitakoTerminoKop(self):
        return self.snoTBX.getItzulitakTerminoKop()

    def getSemanticTagKop(self):
        return self.snoTBX.getSemanticTagKop()

    def getKontzeptuIdak(self):
        return self.snoTBX.getKontzeptuIdak()

