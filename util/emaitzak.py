#!/usr/bin/python3
# -*- coding: utf-8 -*-
from util.enumeratuak import Iturburua
class Emaitzak:

    def __init__(self,hie,cli):
        self.hierarkia = hie
        self.cli = cli
        
        self.algoritmoa = [[0], #mapeoa
                           [0,0,0,0],#hiztegia [ingOrdainak,ingParekatzeak,spaOrdainak,spaParekatzeak]
                           [0,0],#morfosemantika [ordainak,parekatzeak]
                           [0,0],#sintaxia [ingelesez,gaztelaniaz]
                           [0,0]]#denera [ingelesez,gaztelaniaz]
        self.hiztegiak = [[0,0,0,0],#zt[ingOrdainak,ingParekatzeak,spaOrdainak,spaParekatzeak]
                          [0,0,0,0],#anatomia[ingOrdainak,ingParekatzeak,spaOrdainak,spaParekatzeak]
                          [0,0,0,0],#erizaintza[ingOrdainak,ingParekatzeak,spaOrdainak,spaParekatzeak]
                          [0,0,0,0],#gns10[ingOrdainak,ingParekatzeak,spaOrdainak,spaParekatzeak]
                          [0,0,0,0],#elhuyar[ingOrdainak,ingParekatzeak,spaOrdainak,spaParekatzeak]
                          [0,0,0,0],#euskalterm[ingOrdainak,ingParekatzeak,spaOrdainak,spaParekatzeak]
                          [0,0,0,0],#administrazioa[ingOrdainak,ingParekatzeak,spaOrdainak,spaParekatzeak]
                          [0,0,0,0],#sexologia[ingOrdainak,ingParekatzeak,spaOrdainak,spaParekatzeak]
                          [0,0,0,0]]#drogak[ingOrdainak,ingParekatzeak,spaOrdainak,spaParekatzeak]
        self.tokenak = [[0,0,0,0],#bat[ingDen,ingBai,gazDen,gazBai]
                        [0,0,0,0],#bi[ingDen,ingBai,gazDen,gazBai]
                        [0,0,0,0],#hiru[ingDen,ingBai,gazDen,gazBai]
                        [0,0,0,0],#lau[ingDen,ingBai,gazDen,gazBai]
                        [0,0,0,0]]#anitz[ingDen,ingBai,gazDen,gazBai]
        self.itzuliak = ['','','','']#baiEng,ezEng,baiSpa,ezSpa
        self.ezItzuliak = ['','']
        self.kontzeptuakItzuliak = 0
        self.ordainakItzuliak = 0
        self.terminoakItzuliak = 0

    def idatzi(self):
        burukoa = self.hierarkia+self.cli#+"\tIngelesez "+denera[0]+"\t||\tGaztelaniaz "+denera[1]+"\n\t\tIngelesez\t\tGaztelaniaz"
        mapG = "\nGNS10 Mapaketan\t"+str(self.algoritmoa[0][0])
        hiztegi ="\nHiztegietan\tTer: "+str(self.algoritmoa[1][1])+"\tOrd: "+str(self.algoritmoa[1][0])+"\t||\tTer: "+str(self.algoritmoa[1][3])+"\tOrd: "+str(self.algoritmoa[1][2])
        morfo = "\nMorfologia\tTer: "+str(self.algoritmoa[2][1])+"\tOrd: "+str(self.algoritmoa[2][0])
        
        zt = "\n\nZT\t\tTer: "+str(self.hiztegiak[0][1])+"\tOrd: "+str(self.hiztegiak[0][0])+"\t||\tTer: "+str(self.hiztegiak[0][3])+"\tOrd: "+str(self.hiztegiak[0][2])
        anatomia = "\nAnatomia\tTer: "+str(self.hiztegiak[1][1])+"\tOrd: "+str(self.hiztegiak[1][0])+"\t||\tTer: "+str(self.hiztegiak[1][3])+"\tOrd: "+str(self.hiztegiak[1][2])
        erizaintza = "\nErizaintza\tTer: "+str(self.hiztegiak[2][1])+"\tOrd: "+str(self.hiztegiak[2][0])+"\t||\tTer: "+str(self.hiztegiak[2][3])+"\tOrd: "+str(self.hiztegiak[2][2])
        et = "\nEuskalTerm\tTer: "+str(self.hiztegiak[5][1])+"\tOrd: "+str(self.hiztegiak[5][0])+"\t||\tTer: "+str(self.hiztegiak[5][3])+"\tOrd: "+str(self.hiztegiak[5][2])
        elh = "\nElhuyar\t\tTer: "+str(self.hiztegiak[4][1])+"\tOrd: "+str(self.hiztegiak[4][0])+"\t||\tTer: "+str(self.hiztegiak[4][3])+"\tOrd: "+str(self.hiztegiak[4][2])
        gns = "\nGNS10\t\tTer: "+str(self.hiztegiak[3][1])+"\tOrd: "+str(self.hiztegiak[3][0])+"\t||\tTer: "+str(self.hiztegiak[3][3])+"\tOrd: "+str(self.hiztegiak[3][2])
        adm = "\nAdminSan\tTer: "+str(self.hiztegiak[6][1])+"\tOrd: "+str(self.hiztegiak[6][0])+"\t||\tTer: "+str(self.hiztegiak[6][3])+"\tOrd: "+str(self.hiztegiak[6][2])

        portzentaiak = "\n\n\t\tPortzentaiak"
        bat = "\nHitz bakarrekoak\tIngelesez "+str(((self.tokenak[0][1]/self.tokenak[0][0])*100))+" ("+str(self.tokenak[0][1])+"/"+str(self.tokenak[0][0])+")\t||\tGaztelaniaz "+str(((self.tokenak[0][3]/self.tokenak[0][2])*100))+" ("+str(self.tokenak[0][3])+"/"+str(self.tokenak[0][2])+")"
        bi = "\nBi hitzetakoak\t\tIngelesez "+str((self.tokenak[1][1]/self.tokenak[1][0])*100)+" ("+str(self.tokenak[1][1])+"/"+str(self.tokenak[1][0])+")\t||\tGaztelaniaz "+str((self.tokenak[1][3]/self.tokenak[1][2])*100)+" ("+str(self.tokenak[1][3])+"/"+str(self.tokenak[1][2])+")"
        hiru = "\nHiru hitzetakoak\tIngelesez "+str((self.tokenak[2][1]/self.tokenak[2][0])*100)+" ("+str(self.tokenak[2][1])+"/"+str(self.tokenak[2][0])+")\t||\tGaztelaniaz "+str((self.tokenak[2][3]/self.tokenak[2][2])*100)+" ("+str(self.tokenak[2][3])+"/"+str(self.tokenak[2][2])+")"
        lau = "\nLau hitzetakoak\t\tIngelesez "+str((self.tokenak[3][1]/self.tokenak[3][0])*100)+" ("+str(self.tokenak[3][1])+"/"+str(self.tokenak[3][0])+")\t||\tGaztelaniaz "+str((self.tokenak[3][3]/self.tokenak[3][2])*100)+" ("+str(self.tokenak[3][3])+"/"+str(self.tokenak[3][2])+")"
        gehi = "\nHitz gehiagotakoak\tIngelesez "+str((self.tokenak[4][1]/self.tokenak[4][0])*100)+" ("+str(self.tokenak[4][1])+"/"+str(self.tokenak[4][0])+")\t||\tGaztelaniaz "+str((self.tokenak[4][3]/self.tokenak[4][2])*100)+" ("+str(self.tokenak[4][3])+"/"+str(self.tokenak[4][2])+")"
        
        denK = "\nDENERA ITZULITAKO KONTZEPTUAK\t"+str(self.kontzeptuakItzuliak)
        denTSpa = str(self.tokenak[0][3]+self.tokenak[1][3]+self.tokenak[2][3]+self.tokenak[3][3]+self.tokenak[4][3])
        denTEng = str(self.tokenak[0][1]+self.tokenak[1][1]+self.tokenak[2][1]+self.tokenak[3][1]+self.tokenak[4][1])
        denT = "\nDENERA ITZULITAKO TERMINOAK\t"+str(self.terminoakItzuliak)+" (Eng: "+denTEng+", Spa: "+denTSpa+")";
        ordI = "\nDENERA LORTUTAKO ORDAINAK\t"+str(self.ordainakItzuliak)
        print(str(self.algoritmoa))
        print(str(self.tokenak))
        return burukoa+hiztegi+morfo+zt+anatomia+erizaintza+gns+et+elh+mapG+portzentaiak+bat+bi+hiru+lau+gehi+denK+denT+ordI+"\n\n\n"

    def getTerminoak(self,hizkuntza,mota):
        if mota == 'bai':
            i = 0
        elif mota == 'ez':
            i = 1
        if hizkuntza == 'es':
            i += 2
        return self.itzuliak[i]

    
    def gehiToken(self,kopurua,mota,hizkuntza):
        if mota == 'denera':
            i = 0
        elif mota == 'itzulia':
            i = 1
        if hizkuntza == 'es':
            i += 2
        kop = kopurua-1
        if kop > 4:
            kop = 4
        self.tokenak[kop][i] += 1

    def getDenera(self,mota,hizkuntza):
        if mota == 'denera':
            i = 1
        elif mota == 'itzulia':
            i = 0
        if hizkuntza == 'es':
            i += 2
        kop = 0
        for kopuruak in self.tokenak:
            kop += kopuruak[i]
        return kop
    
    def setTerminoa(self,term,hizkuntza,mota):
        if mota == 'bai':
            i = 0
        elif mota == 'ez':
            i = 1
        if hizkuntza == 'es':
            i += 2
        self.itzuliak[i] += term+'\n'

    def gehiHiztegia(self,hiztegia,mota,hizkuntza):
        if mota == 'ordain':
            i = 0
        elif mota == 'pare':
            i = 1
        if hizkuntza == 'es':
            i += 2
        if type(hiztegia)==str:
            self.hiztegiak[Iturburua[hiztegia][1]-1][i] += 1
        elif type(hiztegia)==int:
            self.hiztegiak[hiztegia][i] += 1

            
    def gehiAlgoritmoa(self,urratsa,mota,hizkuntza='en'):
        if mota == 'ordain':
            i = 0
        elif mota == 'pare':
            i = 1
        if urratsa == 'hiztegia':
            if hizkuntza == 'es':
                i += 2
            j = 1
        elif urratsa == 'morfo':
            j = 2
        elif urratsa == 'sintaxia':
            j = 3
        elif urratsa == 'mapaketa':
            j = 0
        self.algoritmoa[j][i] += 1
        
    def setKontzeptuakItzulita(self,kopurua):
        self.kontzeptuakItzuliak = kopurua

    def setOrdainakItzulita(self,kopurua):
        self.ordainakItzuliak = kopurua

    def setTerminoakItzulita(self,kopurua):
        self.terminoakItzuliak = kopurua
    
