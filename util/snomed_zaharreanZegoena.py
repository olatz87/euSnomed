    def defTypeBanatu(self,engPath,spaPath):
        if "RF2Release" in engPath:
            engLan = glob.glob(engPath+'/Refset/Language/*Language*.txt')[0]
            engDef = glob.glob(engPath+'/Terminology/*Description*.txt')[0]
            engRel = glob.glob(engPath+'/Terminology/*Relationship*.txt')[0]

            engPreSet = set()
            with codecs.open(engLan,encoding='utf-8') as fin:
                for line in fin:
                    lerroa = line.strip().split('\t')
                    if lerroa[2] == '1' and lerroa[6] == "900000000000548007":
                        engPreSet.add(lerroa[5])
            #print(len(engPreSet))
            engSyn = ''
            engPre = ''
            engFsn = ''
            with codecs.open(engDef,encoding='utf-8') as fin:
                for line in fin:
                    line = line.strip()
                    lerroa = line.split('\t')
                    if lerroa[2] == '1' and lerroa[6] == "900000000000003001":
                        engFsn += line+'\n'
                    elif lerroa[2] == '1':
                        if lerroa[0] in engPreSet:
                            engPre += line+'\n'
                        else:
                            engSyn += line+'\n'
            # with codecs.open(path+'/snomed/fsn_eng_active.txt','w',encoding='utf-8') as fout:
            #     fout.write(engFsn)
            # print("fsn_eng_active.txt sortua\t"+str(engFsn.count('\n')+1))
            # with codecs.open(path+'/snomed/pre_eng_active.txt','w',encoding='utf-8') as fout:
            #     fout.write(engPre)
            # print("pre_eng_active.txt sortua\t"+str(engPre.count('\n')+1))
            # with codecs.open(path+'/snomed/syn_eng_active.txt','w',encoding='utf-8') as fout:
            #     fout.write(engSyn)
            # print("syn_eng_active.txt sortua\t"+str(engSyn.count('\n')+1))
        else:
            #engLan = glob.glob(engPath+'/Terminology/Content/*Language*.txt')[0]
            engDef = glob.glob(engPath+'/Terminology/Content/*Description*.txt')[0]
            engRel = glob.glob(engPath+'/Terminology/Content/*Relationship*.txt')[0]
        if "RF2Release" in spaPath:
            spaLan = glob.glob(spaPath+'/Refset/Language/*Language*.txt')[0]
            spaDef = glob.glob(spaPath+'/Terminology/*Description*.txt')[0]
        else:
            #spaLan = glob.glob(spaPath+'/Refset/Language/*Language*.txt')[0]
            spaDef = glob.glob(spaPath+'/Terminology/*Description*.txt')[0]

        spaPreSet = set()
        with codecs.open(spaLan,encoding='utf-8') as fin:
            for line in fin:
                lerroa = line.strip().split('\t')
                if lerroa[2] == '1' and lerroa[6] == "900000000000548007":
                    spaPreSet.add(lerroa[5])
        spaSyn = ''
        spaPre = ''
        spaFsn = ''
        with codecs.open(spaDef,encoding='utf-8') as fin:
            for line in fin:
                line = line.strip()
                lerroa = line.split('\t')
                if lerroa[2] == '1' and lerroa[6] == "900000000000003001":
                    spaFsn += line+'\n'
                elif lerroa[2] == '1':
                    if lerroa[0] in spaPreSet:
                        spaPre += line+'\n'
                    else:
                        spaSyn += line+'\n'

        with codecs.open(self.path+'/snomed/fsn_spa_active.txt','w',encoding='utf-8') as fout:
            fout.write(spaFsn)
            print("fsn_spa_active.txt sortua\t"+str(spaFsn.count('\n')+1))
        with codecs.open(self.path+'/snomed/pre_spa_active.txt','w',encoding='utf-8') as fout:
            fout.write(spaPre)
            print("pre_spa_active.txt sortua\t"+str(spaPre.count('\n')+1))
        with codecs.open(self.path+'/snomed/syn_spa_active.txt','w',encoding='utf-8') as fout:
            fout.write(spaSyn)
            print("syn_spa_active.txt sortua\t"+str(spaSyn.count('\n')+1))
        isa = ''
        with codecs.open(engRel,encoding='utf-8') as fin:
            for line in fin:
                line = line.strip()
                lerroa = line.split('\t')
                if lerroa[2] == '1' and lerroa[7] == "116680003":
                    isa += line+'\n'

    def isaKargatu(self):
        #SNOMED CT-ren IS-a erlazioak kargatu egiten ditu eta hash batean sartuta itzultzen ditu, 
	# hau da, hierarkia bakoitzean aurkitzen diren kontzeptuen identifikadoreak itzultzen ditu 
        lagisaRel = {}
        with codecs.open(self.path+'/snomed/is_a_active.txt',encoding='utf-8') as isaRelFitx:
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
                        print("Kontzeptu berdina bi hierarkiatan aurkitzen da "+lag+" "+hierarkiak[lag]+" vs "+hie)
                else:
                    irte += lag + '\n'
                    hierarkiak[lag] = hie
                    hur = isaRel.get(lag,None)
                    irte += self.jasoErrek(hur,hie,isaRel,hierarkiak)
            return irte
                    
    def fsnBanatu(self):
        with codecs.open(self.path+'/snomed/fsn_eng_active.txt') as fsnFitx:
            fsnak = {}
            for lerroa in fsnFitx:
                lerroa = lerroa.decode('utf-8').strip()
                cId = lerroa.split('\t')[4]
                fsnak[cId]=lerroa
            for hie in Hierarkia:
                with codecs.open(self.path+'/snomed/hierarkiak/'+hie+'_cId.txt') as cIdFitx:
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
                        with codecs.open(self.path+'/snomed/hierarkiak/'+hie+'_DIS_fsn.txt','w',encoding='utf-8') as fdis:
                            fdis.write(dis)
                        print(hie+"_DIS_fsn.txt sortua\t"+str(dis.count('\n')+1))
                        with codecs.open(self.path+'/snomed/hierarkiak/'+hie+'_FIN_fsn.txt','w',encoding='utf-8') as ffin:
                            ffin.write(fin)
                        print(hie+"_FIN_fsn.txt sortua\t"+str(fin.count('\n')+1))
                    else:
                        fsn = ''
                        for lerroa in cIdFitx:
                            lerroa = lerroa.decode('utf-8').strip()
                            if lerroa:
                                fsn += fsnak[lerroa]+'\n'
                        with codecs.open(self.path+'/snomed/hierarkiak/'+hie+'_fsn.txt','w',encoding='utf-8') as ffsn:
                            ffsn.write(fsn)
                        print(hie+"_fsn.txt sortua\t"+str(fsn.count('\n')+1))
                              
    def presynBanatu(self,presyn):
        preEnak = {}
        if presyn == 'pre':
            enfitx = self.path+'/snomed/pre_eng_active.txt'
            esfitx = self.path+'/snomed/pre_spa_active.txt'
            disEnfitx = '_DIS_pre_eng.txt'
            finEnfitx = '_FIN_pre_eng.txt'
            irtEnfitx = '_pre_eng.txt'
            disEsfitx ='_DIS_pre_spa.txt'
            finEsfitx = '_FIN_pre_spa.txt'
            irtEsfitx = '_pre_spa.txt'
        else:
            enfitx = self.path+'/snomed/syn_eng_active.txt'
            esfitx = self.path+'/snomed/syn_spa_active.txt'
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
                    if len(lerroa.split('\t')) < 4:
                        print(lerroa)
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
                with codecs.open(self.path+'/snomed/hierarkiak/'+hie+'_DIS_fsn.txt',encoding='utf-8') as fitx:
                    for lerroa in fitx:
                        lerroa = lerroa.strip()
                        if lerroa:
                            cId = lerroa.split('\t')[4]
                            if cId in preEnak:
                                preEn += preEnak[cId]+'\n'
                            if cId in preEsak:
                                preEs += preEsak[cId]+'\n'
                with codecs.open(self.path+'/snomed/hierarkiak/'+hie+disEnfitx,'w',encoding='utf-8') as fitx:
                    fitx.write(preEn)
                print(hie+disEnfitx+' sortua\t'+str(preEn.count('\n')+1))
                with codecs.open(self.path+'/snomed/hierarkiak/'+hie+disEsfitx,'w',encoding='utf-8') as fitx:
                    fitx.write(preEs)
                print(hie+disEsfitx+' sortua\t'+str(preEs.count('\n')+1))
                preEn = ''
                preEs = ''
                with codecs.open(self.path+'/snomed/hierarkiak/'+hie+'_FIN_fsn.txt',encoding='utf-8') as fitx:
                    for lerroa in fitx:
                        lerroa = lerroa.strip()
                        if lerroa:
                            cId = lerroa.split('\t')[4]
                            if cId in preEnak:
                                preEn += preEnak[cId]+'\n'
                            if cId in preEsak:
                                preEs += preEsak[cId]+'\n'
                with codecs.open(self.path+'/snomed/hierarkiak/'+hie+finEnfitx,'w',encoding='utf-8') as fitx:
                    fitx.write(preEn)
                print(hie+finEsfitx+' sortua\t'+str(preEn.count('\n')+1))
                with codecs.open(self.path+'/snomed/hierarkiak/'+hie+finEsfitx,'w',encoding='utf-8') as fitx:
                    fitx.write(preEs)
                print(hie+finEsfitx+' sortua\t'+str(preEs.count('\n')+1))
            else:
                with codecs.open(self.path+'/snomed/hierarkiak/'+hie+'_fsn.txt',encoding='utf-8') as fitx:
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
                with codecs.open(self.path+'/snomed/hierarkiak/'+hie+irtEnfitx,'w',encoding='utf-8') as fitx:
                    fitx.write(preEn)
                print(hie+irtEnfitx+' sortua\t'+str(preEn.count('\n')+1))
                with codecs.open(self.path+'/snomed/hierarkiak/'+hie+irtEsfitx,'w',encoding='utf-8') as fitx:
                    fitx.write(preEs)
                print(hie+irtEsfitx+' sortua\t'+str(preEs.count('\n')+1))

    def hierarkiakBanatu(self):
        #Errepasatu algoritmoa, fsn_eng_active.txt fitxategiak 417209 kontzeptu ditu, eta banaketa egin ostean 312996 gelditzen dira. Hau da, 100000 galtzen dira!!!
        isaRel = self.isaKargatu()
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
            with codecs.open(self.path+'/snomed/hierarkiak/'+hie+'_cId.txt','w',encoding='utf-8') as fitxcId:
                fitxcId.write(irteera)
            print(hie+"_cId.txt sortua\t"+str(irteera.count('\n')+1))
        self.fsnBanatu()
        self.presynBanatu('pre')
        self.presynBanatu('syn')
