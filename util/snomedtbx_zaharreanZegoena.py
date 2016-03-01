    def langSetEzarri(self,pre,syn,hizk):
        langSet = ET.Element('langSet')
        langSet.set('{http://www.w3.org/XML/1998/namespace}lang',hizk)
        for pre1 in pre:
            ntig = ET.SubElement(langSet,'ntig',id=hizk+pre1[0])
            termGrp = ET.SubElement(ntig,'termGrp')
            term = ET.SubElement(termGrp,'term').text = pre1[7]
            termNote = ET.SubElement(termGrp,'termNote',type='administrativeStatus').text = 'preferredTerm-adm-sts'
            sortKey = ET.SubElement(ntig,'admin',type='sortKey').text = unidecode.unidecode(pre1[7])
            #workStatus = ET.SubElement(ntig,'admin',type='elementWorkingStatus').text = 'importedElement'
            if 'InitialInsensitive' == pre1[8]:
                cS = 'InitialInsensitive'
            elif 'Sensitive' == pre1[8]:
                cS = 'Sensitive'
            else:
                cS = 'Insensitive'
            usageNote = ET.SubElement(termGrp,'termNote',type='usageNote').text = cS
        for syn1 in syn:
            ntig = ET.SubElement(langSet,'ntig',id=hizk+syn1[0])
            termGrp = ET.SubElement(ntig,'termGrp')
            term = ET.SubElement(termGrp,'term').text = syn1[7]
            termNote = ET.SubElement(termGrp,'termNote',type='administrativeStatus').text = 'admittedTerm-adm-sts'
            sortKey = ET.SubElement(ntig,'admin',type='sortKey').text = unidecode.unidecode(syn1[7])
            #workStatus = ET.SubElement(ntig,'admin',type='elementWorkingStatus').text = 'importedElement'
            if CaseSignificance['InitialInsensitive'] == syn1[8]:
                cS = 'InitialInsensitive'
            elif CaseSignificance['Sensitive'] == syn1[8]:
                cS = 'Sensitive'
            else:
                cS = 'Insensitive'
            usageNote = ET.SubElement(termGrp,'termNote',type='usageNote').text = cS
        return langSet


    def terminoenXML(self,hie,cId,fsn,preEng,preSpa,synEng,synSpa):
        fsnTerm = fsn[0][7]
        semTag = SnomedTBX.semanticTagLortu(fsnTerm)
        termEntry = ET.Element('termEntry',id='c'+cId)
        sfH = Hierarkia[hie][0]
        if semTag != 'Hutsa':
            sfH += '-'+SemanticTag[semTag][0]
        subFieHie = ET.SubElement(termEntry,'descrip',type='subjectField').text = sfH
        defEl = ET.SubElement(termEntry,'descrip',type='definition').text = fsnTerm
        termEntry.append(self.langSetEzarri(preEng,synEng,'en'))
        spa = self.langSetEzarri(preSpa,synSpa,'es')
        if spa.find('ntig'):
            termEntry.append(spa)
        return termEntry
    def xmltanBanatu(self):
        for hie in Hierarkia:
            i = 1
            cli = ['','']
            if hie == 'CLINICAL':
                i = 2
                cli = ['_FIN','_DIS']
            for j in range(0,i):
                fsnak = self.fitx2hash(self.path+'snomed/hierarkiak/'+hie+cli[j]+'_fsn.txt')
                preEngak = self.fitx2hash(self.path+'snomed/hierarkiak/'+hie+cli[j]+'_pre_eng.txt')
                preSpaak = self.fitx2hash(self.path+'snomed/hierarkiak/'+hie+cli[j]+'_pre_spa.txt')
                synEngak = self.fitx2hash(self.path+'snomed/hierarkiak/'+hie+cli[j]+'_syn_eng.txt')
                synSpaak = self.fitx2hash(self.path+'snomed/hierarkiak/'+hie+cli[j]+'_syn_spa.txt')
                self.erroa = ET.Element('martif',type='TBX')
                self.erroa.set('{http://www.w3.org/XML/1998/namespace}lang','eu')
                self.erroa.append(self.burukoaXMLSnomed(hie))
                text = ET.SubElement(self.erroa,'text')
                body = ET.SubElement(text,'body')
                for cId,fsn in fsnak.items():
                    preEng = preEngak.get(cId,[])
                    preSpa = preSpaak.get(cId,[])
                    synEng = synEngak.get(cId,[])
                    synSpa = synSpaak.get(cId,[])
                    body.append(self.terminoenXML(hie,cId,fsn,preEng,preSpa,synEng,synSpa))
                self.ordenatu()
                dok = self.path+'snomed/XMLak/'+hie+cli[j]+'.xml'
                tree = ET.ElementTree(self.erroa)
                tree.write(dok,encoding='utf-8',xml_declaration=True)
                print(hie+cli[j],'hierarkiaren XMLa sortua.')
