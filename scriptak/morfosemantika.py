#!/usr/bin/python
import sys,os,getopt,subprocess
from subprocess import PIPE,Popen

def main(argv):
    bertsioa = '2'
    term =''
    inprimatu = False
    try:
        opts, args = getopt.getopt(argv,"hv:t:p",["bertsioa="])
    except getopt.GetoptError:
        print('python morfosemantika.py -v <bertsiozenbakia> -t <terminoa>')
        sys.exit(2)
    for opt, arg in opts:
        if opt =='-h':
            print('python morfosemantika.py -v <bertsiozenbakia> -t <terminoa>')
            sys.exit()
        elif opt in ("-v","--bertsioa"):
            bertsioa = arg
        elif opt in ("-t","--terminoa"):
            term = arg
        elif opt in ("-p"):
            inprimatu = True
    if not term:
        print('Sarrera terminoa beharrezkoa da')
        print('python morfosemantika.py -v <bertsiozenbakia> -t <terminoa>')
        sys.exit(2)
    path = os.path.dirname(os.path.realpath(__file__))+'/'
    term = term.strip()
    larria = False
    if term[0].isupper():
        larria = True
    p = subprocess.Popen(['flookup -i -x -b '+path+'idenBateratuaOsatua.fst'],stdin=PIPE,stdout=PIPE,shell=True,close_fds=True)
    returnword = p.communicate(input=term.lower().encode('utf8'))
    idenOnak = []
    trans = returnword[0].decode('utf8').strip()
    if trans == '+?':
        return "+?"
    else:
        hashZ = {}
        minLength = 1000
        identifikatuak = trans.strip().split('\n')
        if "#+" in identifikatuak[0]:
            for itzul in identifikatuak:
                zat = itzul.split('+')
                count = len(zat)
                for z in zat:
                    if '#' in z:
                        count += len(z)-1
                if count <=minLength:
                    hashZ[itzul]=count
                    minLength = count
            for key,value in hashZ.items():
                if value <= minLength:
                    idenOnak.append(key)
        else:
            for itzul in identifikatuak:
                zat = itzul.split('+')
                count = len(zat)
                if count <= minLength:
                    hashZ[itzul]=count
                    minLength = count
            for key,value in hashZ.items():
                if value <= minLength:
                    idenOnak.append(key)
    if '' in idenOnak:
        idenOnak.remove('')
    lag = set()
    if inprimatu:
        print(idenOnak)
    idatz = ''
    for s in idenOnak:
        p1 = subprocess.Popen(['flookup -i -x -b '+path+'itzultzaileaOsatua.fst'],stdin=PIPE,stdout=PIPE,shell=True)
        returnwords = p1.communicate(input=s.encode('utf8'))
        for itzul in returnwords[0].decode('utf8').split('\n'):
            if not itzul:
                continue
            if larria:
                itzul = itzul[0].upper()+itzul[1:]
            if itzul not in lag:
                lag.add(itzul)
                if idatz == '':
                    idatz = itzul
                else:
                    idatz += '\t'+itzul
    return idatz
# my %lag;
# my $idatz = "";
# foreach my $s (@idenOnak){
#     my $pidFOMAid = open2(*Reader, *Writer, "flookup -i -x -b $FindBin::Bin/itzultzaileaOsatua.fst");
#     print Writer "^$s\n";
#     while ((my $itzul = <Reader>) ne "\n") {
# 	chomp($itzul);
# 	if (!exists($lag{$itzul})){
# 	    $lag{$itzul}="kuku";
# 	    $idatz.="$itzul\t";
# 	}
#     }
#     close(Reader); close(Writer);
# }
# print "$idatz";


if __name__ == "__main__":
    print(main(sys.argv[1:]))

