import csv,sys,jsonrpclib,json,nltk,re


class Deskribapenak:
    def __init__(self, port_number = 9602):
        self.server = jsonrpclib.Server("http://158.227.106.115:%d" % port_number)

    def deskribapenakJaso(self):
        return json.loads(self.server.deskribapenakJaso(),encoding="utf-8")

    def deskribapenArabera(self):
        return json.loads(self.server.deskribapenArabera(),encoding="utf-8")

    def sct2term(self,sctId):
        return json.loads(self.server.sct2term(sctId),encoding="utf-8")

    def sct2desc(self,sctId):
        return json.loads(self.server.sct2desc(sctId),encoding="utf-8")

    def sct2hierarkiak(self,sctId):
        return json.loads(self.server.sct2hierarkiak(sctId),encoding="utf-8")

    def desc2sct(self,desc,lemma):
        return json.loads(self.server.desc2sct(desc,lemma))

    def kontzeptuakJaso(self):
        return json.loads(self.server.kontzeptuakJaso(),encoding="utf-8")
        
    def kontzeptuaJaso(self,cId):
        return json.loads(self.server.kontzeptuaJaso(cId))

    def dId2desc(self,dId):
        return json.loads(self.server.dId2desc(dId))



def deskribapenakAztertu():
    des = Deskribapenak()
    deskribapenak = des.deskribapenakJaso()
    denera = len(deskribapenak)
    i = 0
    sys.stdout.write("\r%d / %d" %(i,denera))
    sys.stdout.flush()
    with open("deskribapenak.tsv",'w') as fout:
        fieldnames = ["dId","cId","Hierarkia","SemanticTag","TokenKopurua"]
        idazle = csv.DictWriter(fout,fieldnames=fieldnames,delimiter='\t')
        idazle.writeheader() 
        lagSet = set()
        for dId in deskribapenak:
            i += 1
            desk = des.dId2desc(dId)
            cId = desk["conceptId"]
            con = des.kontzeptuaJaso(cId)
            hie = des.sct2hierarkiak([cId])
            term = desk["term"]
            if len(hie)>1:
                print(dId,cId,term,hie)
            else:
                hieL = hie[0]
            tokenak = nltk.word_tokenize(term)
            tok_kop = len(tokenak)
            fsn = con["fullySpecifiedName"]
            fsnST = re.search('\(([^(]+?)\)$',fsn)
            if fsnST:
                semTag = fsnST.group(1)
            else:
                print(dId,cId,term,hie,fsn)
            lagSet.add(semTag)
            idazle.writerow({"dId":dId,"cId":cId,"Hierarkia":hieL,"SemanticTag":semTag,"TokenKopurua":tok_kop})
            sys.stdout.write("\r%d / %d\t" %(i,denera))
            sys.stdout.flush()

    print(lagSet)
def main(argv):
    deskribapenakAztertu()


if __name__ == "__main__":
    main(sys.argv[1:])
