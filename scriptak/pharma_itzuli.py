#!/usr/bin/python
import sys,os,getopt,subprocess
from subprocess import PIPE,Popen

def main(argv):
    bertsioa = '2'
    term =''
    try:
        opts, args = getopt.getopt(argv,"hv:t:",["bertsioa="])
    except getopt.GetoptError:
        print('python pharma_itzuli.py -v <bertsiozenbakia> -t <terminoa>')
        sys.exit(2)
    for opt, arg in opts:
        if opt =='-h':
            print('python pharma_itzuli.py -v <bertsiozenbakia> -t <terminoa>')
            sys.exit()
        elif opt in ("-v","--bertsioa"):
            bertsioa = arg
        elif opt in ("-t","--terminoa"):
            term = arg
    if not term:
        print('Sarrera terminoa beharrezkoa da')
        print('python morfosemantika.py -v <bertsiozenbakia> -t <terminoa>')
        sys.exit(2)
    path = os.path.dirname(os.path.realpath(__file__))+'/'
    term = term.strip()
    larria = False
    if term[0].isupper():
        larria = True
        term = term[0].lower()+term[1:]
    p = subprocess.Popen(['flookup -i -x -b '+path+'transli_pharma.fst'],stdin=PIPE,stdout=PIPE,shell=True,close_fds=True)
    returnword = p.communicate(input=term.encode('utf8'))
    idenOnak = []
    trans = returnword[0].decode('utf8').strip()
    idatz = ''
    if trans == '+?':
        return "+?"
    else:
        for itzul in trans.split('\n'):
            if not itzul:
                continue
            if larria:
                itzul = itzul[0].upper()+itzul[1:]
            if idatz == '':
                idatz = itzul
            else:
                idatz += '\t'+itzul
    return idatz


if __name__ == "__main__":
    print(main(sys.argv[1:]))

