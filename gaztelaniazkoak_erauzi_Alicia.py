from util.snomed import Snomed
from util.terminotbxsnomed import TerminoTBXSnomed
import codecs


Hierarkiak = ["DISORDER","PHARMPRODUCT"]

out_f = "dis-prod_es.txt"


out_str = "" 
snomed = Snomed(False,"../../euSnomed/")
for hie in Hierarkiak:
    snomed.kargatu(hie,"")
    terminoak = snomed.getTerminoak("es")
    for term in terminoak:
        terminoa = TerminoTBXSnomed(term)
        out_str += terminoa.getTerminoa()+"\t"+hie.lower()+"\n"


with codecs.open(out_f,"w",encoding="utf-8") as fout:
    fout.write(out_str)
