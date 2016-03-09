import codecs,sys,nltk
from pprint import pprint
from nltk.tokenize.stanford import StanfordTokenizer

#SNOMED CT-ko RF1 formatuko hierarkiak
Hierarkia_RF1 = {
    'FORCE' : ("190","78621006"),
    #'METADATA' :("200","900000000000441003"),
    'SPECIAL' : ("170","370115009"),
    'RECORD' : ("180","419891008"),
    'BODYSTRUCTURE' : ("040","123037004"),
    'PROCEDURE' : ("020","71388002"),
    'FINDING' : ("010","404684003"),
    'DISORDER' : ("011","64572001"),
    'EVENT' : ("090","272379006"),
    'SITUATION' : ("100","243796009"),
    'SOCIAL' : ("110","48176007"),
    'OBJECT' : ("120","260787004"),
    'SPECIMEN' : ("130","123038009"),
    'ENVIRONMENT' : ("140","308916002"),
    'LINKAGE' : ("150","106237007"),
    'STAGING' : ("160","254291000"),
    'QUALIFIER' : ("070","362981000"),
    'OBSERVABLE' : ("080","363787002"),
    'SUBSTANCE' : ("050","105590001"),
    'PHARMPRODUCT' : ("060","373873005"),
    'ORGANISM' : ("030","410607006")}

#SNOMED CT-ko RF2 formatuko hierarkiak
Hierarkia_RF2 = {
    'FORCE' : ("190","78621006"),
    'METADATA' :("200","900000000000441003"),
    'SPECIAL' : ("170","370115009"),
    'RECORD' : ("180","419891008"),
    'BODYSTRUCTURE' : ("040","123037004"),
    'PROCEDURE' : ("020","71388002"),
    'FINDING' : ("010","404684003"),
    'DISORDER' : ("011","64572001"),
    'EVENT' : ("090","272379006"),
    'SITUATION' : ("100","243796009"),
    'SOCIAL' : ("110","48176007"),
    'OBJECT' : ("120","260787004"),
    'SPECIMEN' : ("130","123038009"),
    'ENVIRONMENT' : ("140","308916002"),
    #'LINKAGE' : ("150","106237007"),
    'STAGING' : ("160","254291000"),
    'QUALIFIER' : ("070","362981000"),
    'OBSERVABLE' : ("080","363787002"),
    'SUBSTANCE' : ("050","105590001"),
    'PHARMPRODUCT' : ("060","373873005"),
    'ORGANISM' : ("030","410607006")}


#SNOMED CT-ko kontzeptuak kudeatzeko objektua
class ConceptList():
    """
    self.rf -> ReleaseFormat ("1" edo "2")
    self.zerrenda -> kontzeptuen zerrenda
    self.hieBanaketa -> 
    """
    #fitxategitik informazioa jaso eta egituratuta gordetzeko
    def kontzeptuaJaso(self,line):
        eremuak = line.strip().split('\t')
        concept={}
        if self.rf == 1 and eremuak[1] == "0":
            concept["conceptId"] = eremuak[0]
            #concept["conceptStatus"] = eremuak[1]
            concept["fullySpecifiedName"] = eremuak[2]
            #concept["ctv3id"] = eremuak[3]
            concept["snomedId"] = eremuak[4]
            concept["isprimitive"] = eremuak[5]
        elif self.rf == 2 and eremuak[2] == "1":
            concept["conceptId"] = eremuak[0]
            concept["isprimitive"] = eremuak[4]
        return concept
        
    #objektuaren hasieratzailea, fitxategitik
    def __init__(self,fitx):
        self.zerrenda = {}
        #RF mota jasotzeko
        if "RF1Release" in fitx:
            self.rf = 1
        else:
            self.rf = 2
        #fitxategia lerroz lerro irakurtzen du, eta self.zerrenda atributuan gordeko du informazio guztia egituratuta
        with codecs.open(fitx,encoding='utf-8') as fitx:
            lines = fitx.read().split('\n')[1:-1]
            for line in lines:
                c = self.kontzeptuaJaso(line)
                if c:
                    self.zerrenda[c["conceptId"]] = c

    #kontzeptu identifikadorea emanda, honen termino hobetsia itzuliko du
    def sct2term(self,sctId):
        c = self.zerrenda[sctId]
        return c["preferredDesc"]["term"]

    #kontzeptu identifikadorea emanda, honen termino hobetsiaren informazioa jasotzen duen hiztegia itzultzen du
    def sct2desc(self,sctId):
        c = self.zerrenda[sctId]
        return c["preferredDesc"]

    #kontzeptu identifikadorea emanda, honen FSN-a itzultzen du
    def sct2fsn(self,sctId):
        c = self.zerrenda.get(sctId,'')
        if c:
            return c["fullySpecifiedName"]
        else:
            return ""

    #self.zerrenda atributua itzultzen du
    def zerrendaLortu(self):
        return self.zerrenda
    
    #self.hieBanaketa-n hierarkia banaketa gordetzen du 
    def setHieBanaketa(self,banaketa):
        self.hieBanaketa = banaketa

    #hierarkia bat emanda, honen edukia itzultzen du
    def hierarkiakoakJaso(self,hie):
        return self.hieBanaketa[hie]

    #kontzeptu identifikadorea emanda, honen informazioa jasotzen duen hiztegia itzultzen du
    def kontzeptua(self,sctId):
        return self.zerrenda[sctId]


    def sinonimoakJaso(self,sctId):
        itzul = []
        for el in self.zerrenda[sctId]["synonymDesc"]:
            itzul.append(el["term"])
        return itzul




#SNOMED CT-ko deskribapenak (edo terminoak) kudeatzeko objektua
class DescriptionList():
    #fitxategitik informazioa jaso eta egituratuta gordetzeko
    #kontutan izan RF-aren arabera fitxategia ezberdina izango dela
    def deskribapenaJaso(self,line):
        eremuak = line.strip().split('\t')
        description = {}
        if self.rf == 1:
            if eremuak[1] == "0":
                description["descriptionId"] = eremuak[0]
                description["descriptionStatus"] = eremuak[1]
                description["conceptId"] = eremuak[2]
                description["term"] = eremuak[3]
                description["initialCapitalStatus"] = eremuak[4]
                description["descriptionType"] = eremuak[5]
                description["languageCode"] = eremuak[6]
        else:
            if eremuak[2] == "1":
                description["descriptionId"] = eremuak[0]
                description["descriptionStatus"] = eremuak[2]
                description["conceptId"] = eremuak[4]
                description["term"] = eremuak[7]
                description["initialCapitalStatus"] = eremuak[8]
                description["descriptionType"] = eremuak[6]
                description["languageCode"] = eremuak[5]
            
        return description

    #objektuaren hasieratzailea, fitxategitik
    def __init__(self,fitx,konZer,lanZer={}):
        #RF2 bada, language fitxategia behar dugu hemengoa ebazteko!!!
        self.zerrenda = {}#Key: descriptionId, value: {description info}
        self.deskArabera = {} #key: term(tokenized,lower), value: [concepId]
        amaieranEbazteko = {}
        if "RF1Release" in fitx:
            self.rf = 1
        else:
            self.rf = 2
            if "Spanish" in fitx:
                lan = "450828004"
            else:
                lan = "900000000000508004"  #GB English
        #konplikatua da, ze RF2 den kasuan, informazioa ez dago fitxategi bakarrean. Hau da, preferred term edo synonym den (termino hobetsia edo sinonimoa) Language fitxategian dago, eta horregatik horrenbeste konplikazio.
        with codecs.open(fitx,encoding='utf-8') as fitx:
            lines = fitx.read().split('\n')[1:-1]
            for line in lines:
                d = self.deskribapenaJaso(line)
                #RF1 denean, "fullySpecifiedName" kontzeptuen fitxategian dago, baino RF2 denean deskribapenetan dago:
                if d and self.rf == 2 and d["descriptionType"] in ["900000000000003001"] and d["conceptId"] in konZer.zerrenda:
                    c = konZer.zerrenda[d["conceptId"]]
                    c["fullySpecifiedName"] = d["term"]
                    konZer.zerrenda[d["conceptId"]] = c 
                #DescriptionType sinonimoa edo preferred term denean (RF1ean 1 edo 2 gisa agertzen da, RF2-n aldiz, 900000000000013009)
                elif d and d["conceptId"] in konZer.zerrenda and d["descriptionType"] in ["1","2","900000000000013009"]:
                    self.zerrenda[d["descriptionId"]] = d
                    tt = " ".join(nltk.word_tokenize(d["term"].lower()))
                    #tt = " ".join(StanfordTokenizer().tokenize(d["term"].lower()))
                    cId = self.deskArabera.get(tt,[])
                    cId.append(d["conceptId"])
                    self.deskArabera[tt] = cId
                    c = konZer.zerrenda[d["conceptId"]]
                    #RF1 eta termino hobetsia
                    if self.rf == 1 and d["descriptionType"] == "1":
                        c["preferredDesc"] = d
                    #RF1 eta sinonimoa
                    elif self.rf == 1 and d["descriptionType"] == "2":
                        lag = c.get("synonymDesc",[])
                        lag.append(d)
                        c["synonymDesc"] = lag
                    #RF2 den kasuan language direktorioko informazioa begiratu behar da.
                    elif self.rf == 2 and d["descriptionId"] in lanZer.zerrenda:
                        l = lanZer.zerrenda[d["descriptionId"]]
                        if  l["acceptabilityId"] == "900000000000548007": #preferred
                            #aukeratutako hizkuntza bada (GB vs USA)
                            if l["refset"] == lan:
                                #hobetsia badu, hobetsi zaharra sinonimoetara pasa
                                if "preferredDesc" in c:
                                    lag = c.get("synonymDesc",[])
                                    lag.append(c["preferredDesc"])
                                    c["synonymDesc"] = lag
                                c["preferredDesc"] = d
                            #ez bada aukeratutako hizkuntza 
                            else:
                                #hobetsia badu, sinonimo gisa gehitu
                                if "preferredDesc" in c:
                                    lag = c.get("synonymDesc",[])
                                    lag.append(d)
                                    c["synonymDesc"] = lag
                                else:
                                    c["preferredDesc"] = d
                        else:#synonym
                            lag = c.get("synonymDesc",[])
                            lag.append(d)
                            c["synonymDesc"] = lag
                            
                    konZer.zerrenda[d["conceptId"]] = c 
                #hauek kasu bereziak dira, amaieran ebatzi behar direnak hobetsiak ala sinonimoak diren RF1-en kasuan.
                elif self.rf == 1 and d and d["descriptionType"] in ["0"] and d["descriptionStatus"] == "0" and d["conceptId"] in konZer.zerrenda:
                    lag = amaieranEbazteko.get(d["conceptId"],[])
                    lag.append(d)
                    amaieranEbazteko[d["conceptId"]] = lag
                    self.zerrenda[d["descriptionId"]] = d
                    tt = " ".join(nltk.word_tokenize(d["term"].lower()))
                    #tt = " ".join(StanfordTokenizer().tokenize(d["term"].lower()))
                    cId = self.deskArabera.get(tt,[])
                    cId.append(d["conceptId"])
        #amaieran ebazteko gelditu direnak, ez badago hobetsirik hobetsi gisa ipini, eta bestela sinonimo gisa.
        for cId,ds in amaieranEbazteko.items():
            c = konZer.zerrenda[cId]
            fsn = c["fullySpecifiedName"]
            for d in ds:
                if "preferredDesc" not in c and fsn.startswith(d["term"]):
                    c["preferredDesc"] = d
                else:
                    lag = c.get("synonymDesc",[])
                    lag.append(d)
                    c["synonymDesc"] = lag
            konZer.zerrenda[cId] = c

    #self.zerrenda atributua itzultzen du
    def zerrendaLortu(self):
        return self.zerrenda

    #deskribapenaren arabera sailkatutako hiztegia itzultzen du
    def deskribapenArabera(self):
        return self.deskArabera

    #deskribapenen lema eta forma emanda honen identifikadorea itzultzen du
    def kodeaLortu(self,forma,lemma):
        if lemma:
            return self.deskArabera.get(forma,self.deskArabera.get(lemma,''))
        else:
            return self.deskArabera.get(forma,'')

    #deskribapen identifikadorea emanda, honen informazioa jasotzen duen hiztegia  itzultzen du
    def dId2desc(self,dId):
        return self.zerrenda[dId]


#SNOMED CT-ko erlazioak kudeatzeko objektua 
class RelationshipList():
    """
    self.zerrenda
    self.umeZerrenda
    """
    #fitxategitik informazioa jaso eta egituratuta gordetzeko
    def erlazioaJaso(self,line):
        eremuak = line.strip().split('\t')
        relationship = {}
        if self.rf == 1:
            relationship["relationshipId"] = eremuak[0]
            relationship["conceptId1"] = eremuak[1]
            relationship["relationshipType"] = eremuak[2]
            relationship["conceptId2"] = eremuak[3]
            relationship["charasteristicType"] = eremuak[4]
            #relationship["refinability"] = eremuak[5]
            relationship["relationshipGroup"] = eremuak[6]
        else:
            if eremuak[2] == "1":
                relationship["relationshipId"] = eremuak[0]
                relationship["conceptId1"] = eremuak[4]
                relationship["relationshipType"] = eremuak[7]
                relationship["conceptId2"] = eremuak[5]
                relationship["charasteristicType"] = eremuak[8]
                relationship["relationshipGroup"] = eremuak[6]
        return relationship

    #objektuaren hasieratzailea, fitxategitik
    def __init__(self,fitx,konZer,isa=False):
        self.zerrenda = {}
        #self.isaZerrenda = {}
        self.umeZerrenda = {}
        self.konZer = konZer 
        if "RF1Release" in fitx:
            self.rf = 1
        else:
            self.rf = 2
        with codecs.open(fitx,encoding='utf-8') as fitx:
            lines = fitx.read().split('\n')[1:-1]
            for line in lines:
                r = self.erlazioaJaso(line)
                if r and r["conceptId1"] in self.konZer.zerrenda and r["conceptId2"] in self.konZer.zerrenda:
                    self.zerrenda[r["relationshipId"]] = r
                    if isa and r["relationshipType"] == "116680003":
                        #jatorriSet = self.isaZerrenda.get(r["conceptId1"],set())
                        #jatorriSet.add(r["conceptId2"])
                        #self.isaZerrenda[r["conceptId1"]] = jatorriSet
                        helmugaSet = self.umeZerrenda.get(r["conceptId2"],set())
                        helmugaSet.add(r["conceptId1"])
                        self.umeZerrenda[r["conceptId2"]] = helmugaSet

    #kontzeptuak hierarkiaka banatzeko funtzio errekurtsiboa
    def jasoErrek(self,setOna,hie,hiz):
        if setOna:
            if hie == "FINDING" and "64572001" in setOna:
                print("disorder finding-etik kenduta")
                setOna.remove("64572001")
            for lag in setOna:
                if lag in self.hierarkiak:
                    if hie not in self.hierarkiak[lag]:
                        fsn = self.konZer.sct2fsn(lag)
                        hieLag = hie.lower()
                        hieLag_es = hie.lower()
                        hieLagZ = self.hierarkiak[lag].lower()
                        hieLagZ_es = self.hierarkiak[lag].lower()
                        if hieLag == "pharmproduct":
                            if hiz == "es":
                                hieLag = "producto"
                            else:
                                hieLag = "product"
                        elif hieLag == "disorder":
                            if hiz == "es":
                                hieLag = "trastorno"
                        elif hieLag == "finding":
                            if hiz == "es":
                                hieLag = "hallazgo"
                        if hieLagZ == "pharmproduct":
                            if hiz == "es":
                                hieLag = "producto"
                            else:
                                hieLagZ = "product"
                        elif hieLagZ == "disorder":
                            if hiz == "es":
                                hieLagZ = "trastorno"
                        elif hieLagZ == "finding":
                            if hiz == "es":
                                hieLagZ = "hallazgo"

                        if fsn.endswith("("+hieLag+")") :
                            self.hierarkiak[lag] = hie
                            self.banaketa[hie].append(lag)
                            hur = self.umeZerrenda.get(lag,None)
                            self.jasoErrek(hur,hie,hiz)
                        elif fsn.endswith("("+hieLagZ+")") :
                            continue
                        else:
                            print("Kontzeptu berdina bi hierarkiatan aurkitzen da "+fsn+" "+self.hierarkiak[lag]+" vs "+hie)
                            
                else:
                    self.hierarkiak[lag] = hie
                    self.banaketa[hie].append(lag)
                    hur = self.umeZerrenda.get(lag,None)
                    self.jasoErrek(hur,hie,hiz)



    def hierarkiakEsleitu(self,hiz="en"):
        self.hierarkiak = {}
        self.banaketa = {}
        if self.rf == 1:
            Hierarkia = Hierarkia_RF1
        else:
            Hierarkia = Hierarkia_RF2
        for hie in Hierarkia:
            setOna = self.umeZerrenda[Hierarkia[hie][1]]
            self.banaketa[hie] = [Hierarkia[hie][1]]
            self.jasoErrek(setOna,hie,hiz)
            self.hierarkiak[Hierarkia[hie][1]]=hie        
        self.hierarkiak["138875005"] = "SNOMED CT Concept"
        self.konZer.setHieBanaketa(self.banaketa)

    def hierarkiaLortu(self,sctId):
        irt = []
        for sid in sctId:
            lag = self.hierarkiak.get(sid,'') 
            if lag and lag not in irt:
                irt.append(self.hierarkiak[sid])
        return irt

#SNOMED CT-ko language fitxategiko informazioa kudeatzeko objektua 
class LanguageList():
    #fitxategitik informazioa jaso eta egituratuta gordetzeko
    def languageJaso(self,line):#,lan):
        eremuak = line.strip().split('\t')
        language = {}
        if eremuak[2] == "1":# and eremuak[4] == lan: #Aktibo egotea eta GB English refset 
            language["languageId"] = eremuak[0]
            language["referencedComponentId"] = eremuak[5]
            language["acceptabilityId"] = eremuak[6]
            language["refset"] = eremuak[4]
        return language

    #objektuaren hasieratzailea, fitxategitik
    def __init__(self,fitx):
        self.zerrenda = {}
        if "Spanish" in fitx:
            lan = "450828004"
        else:
            lan = "900000000000508004"
                
        with codecs.open(fitx,encoding='utf-8') as fitx:
            lines = fitx.read().split('\n')[1:-1]
            for line in lines:
                l = self.languageJaso(line)#,lan)
                if l and (l["refset"] == lan or l["referencedComponentId"] not in self.zerrenda):
                    self.zerrenda[l["referencedComponentId"]] = l
