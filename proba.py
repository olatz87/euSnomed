import codecs,re
path = "../../euSnomed/"
with codecs.open(path+'baliabideak/HN_N_bakuna_opentrad_utf8.txt',encoding='utf-8') as fitx:
    for sarrera in fitx:

        sarrera = sarrera.strip()
        sar = sarrera.split('\t')
        if len(sar) == 3:

            engLag = sar[0]
            if " {to}" in engLag:
                engLag = engLag.replace(' {to}','')
            engak = engLag.split(';')
            for eng in engak:
                eng = eng.strip()
                lag = sar[2][:-1].split(". (joan)")[0]
                print(eng,lag)
                if '<I>' in lag:
                    regex1 = re.compile('\[<I>[a-z ,]+<I>\]')
                    regex2 = re.compile('\(<I>[a-z ,]+<I>\)')
                    lag = regex1.sub('',lag)
                    lag = regex2.sub('',lag)
                if '(' in lag:
                    regex = re.compile('\([^)]+?\)')
                    lag = regex.sub('',lag)

                eusak = re.split(',|;',lag)
                for eus in eusak:
                    if '/' in eus or '...' in eus or eus[-1] == '-' or eus[0] == '-':
                        continue
                    if '[' in eus:
                        regex = re.compile('\[[^]]+?\]')
                        eus = regex.sub('',eus)
                    if '{' in eus:
                        regex = re.compile('\{[^}]+?\}')
                        eus = regex.sub('',eus)
                    # if '(' in eus:
                    #     regex = re.compile('\([^)]+?\)')
                    #     eus = regex.sub('',eus)
                    if '(joan)' in eus:
                        print(sarrera)
                    pos = set()
                    if eus[0].isupper():
                        cS ='Sensitive'
                        pos.add('IzenBerezi')
                        if eus.isupper():
                            tT = 'Acronym'
                        else:
                            tT = 'Unknown'
                    else:
                        cS = 'InitialInsensitive'
                        tT = 'Unknown'
                    if len(eus.split())>2:
                        tT = 'SetPhase'
                    if sar[1] and sar[1][0] == 'v':
                        pos.add('Aditz')
                    if 'adj.' in sar[1]:
                        pos.add('Adjektibo')
                    if 'n.' in sar[1] and 'IzenBerezi' not in pos:
                        pos.add('Izen')
                    if 'adv.' in sar[1]:
                        pos.add('Aditzondo')
                    if not pos:
                        pos.add('Besterik')
#                    print(eng,eus)
