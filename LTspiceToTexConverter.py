import numpy as np
import os


def ConvertForAllLTspiceFilesFormFolderToTEX(path='.', lt_spice_directory=r'C:\Program Files\LTC\LTspiceXVII\lib\sym', fullExample=0):
    for filename in os.listdir(path):
        if os.path.isfile(os.path.join(path, filename)):
            if filename.endswith('.asc'):
                print('Convert: ' + filename)
                LtSpiceToLatex(
                    filenameLTspice=filename, lt_spice_directory=lt_spice_directory, fullExample=fullExample)


count_bauelemente = 0
BauteileAddSpeicher = []


def LtSpiceToLatex(saveFile='', filenameLTspice='Draft.asc', lt_spice_directory=r'C:\Program Files\LTC\LTspiceXVII\lib\sym', fullExample=0):

    global count_bauelemente
    global BauteileAddSpeicher

    if saveFile == '':
        saveFile = os.path.splitext(filenameLTspice)[0] + r'.tex'

    print('saveFile: ', saveFile)

    def first_item(list_or_none):
        if list_or_none:
            return list_or_none[0]

    def findPinsInLib(name):
        if not os.path.isdir(lt_spice_directory):
            print('error! lt_spice_directory not exist: ', lt_spice_directory)
            return []

        with open(os.path.join(lt_spice_directory, name + ".asy"), "r") as f:
            sym = f.readlines()

        pin = []
        words = []
        for line in sym:
            words = line.split()
            if words[0] == 'PIN':
                pin.append((int(words[1]), -int(words[2])))
        return pin

    def KnotenSuche(koordinate):
        Knoten = [idx for idx, x1 in enumerate(
            KnotenListe) if x1[0] == koordinate]
        if Knoten == []:
            Knoten = [len(KnotenListe)]
            KnotenListe.append([koordinate, [], [], []])
        return Knoten[0]

    def drahtADD(befehl):
        x1 = (int(befehl[1]), -int(befehl[2]))
        x2 = (int(befehl[3]), -int(befehl[4]))
        anzahlDrat = len(DrahtListe)

        Knoten1 = KnotenSuche(x1)
        Knoten2 = KnotenSuche(x2)
        KnotenListe[Knoten1][1].append(anzahlDrat)
        KnotenListe[Knoten2][1].append(anzahlDrat)

        DrahtListe.append([Knoten1, Knoten2])

    def gndTxtADD(befehl):
        x1 = (int(befehl[1]), -int(befehl[2]))
        anzahlBauteil = len(Bauteilliste)
        Knoten = KnotenSuche(x1)
        KnotenListe[Knoten][2].append(anzahlBauteil)
        if befehl[0] == 'FLAG' and befehl[3] == '0':
            Bauteilliste.append([Knoten, 'FLAG', '', []])
        elif befehl[0] == 'FLAG':
            text = ' '.join(befehl[3:])
            Bauteilliste.append([Knoten, 'TEXT', text, []])
        else:
            text = ' '.join(befehl[5:]).replace(';', '')
            Bauteilliste.append([Knoten, 'TEXT', text, []])

    def bauteilADD(idx, befehl):

        x = np.array([int(befehl[2]), -int(befehl[3])])
        pin = findPinsInLib(befehl[1])
        anzahlBauteil = len(Bauteilliste)

        Rotation = {
            'R0': [[1, 0], [0, 1]],
            'R90': [[0, -1], [1, 0]],
            'R180': [[-1, 0], [0, -1]],
            'R270': [[0, 1], [-1, 0]],
            'M0': [[-1, 0], [0, 1]],
            'M90': [[0, -1], [-1, 0]],
            'M180': [[1, 0], [0, -1]],
            'M270': [[0, 1], [1, 0]], }

        pin = np.dot(pin, Rotation[befehl[4]])

        KnotenSpeicher = []
        for pinn in pin:
            Knoten = KnotenSuche(tuple(pinn+x))
            KnotenSpeicher.append(Knoten)
            KnotenListe[Knoten][2].append(anzahlBauteil)

        bauteilbezeichnung = ''
        for i in range(idx+1, idx+4):
            if words[i][0] == 'SYMATTR':
                bauteilbezeichnung = words[i][2]
                if bauteilbezeichnung.count('_') > 0 and bauteilbezeichnung.count('$') < 2:
                    bauteilbezeichnung = r'$'+bauteilbezeichnung+r'$'
                break

        global count_bauelemente
        global BauteileAddSpeicher
        knotenbez = []
        if not befehl[1] in bauteilmoeglich and not befehl[1] in SpezialBauteilName:
            if not befehl[1] in BauteileAddSpeicher:
                print('The following component is new: ' + befehl[1])
                BauteileAddSpeicher.append(befehl[1])

            knotenbez = []
            for ind, t in enumerate(pin):
                knotenbez.append('B'+str(count_bauelemente) + ' X' + str(ind))

            count_bauelemente = count_bauelemente + 1
            befehl[1] = befehl[1] + ' ' + (befehl[4]+'  ')[0:4]
            for t,  name in enumerate(knotenbez):
                KnotenListe[KnotenSpeicher[t]][3] = name

        if not befehl[1] in bauteilmoeglich and befehl[1] in SpezialBauteilName:
            knotenbez = SpezialBauteilName[befehl[1]]  # []
            knotenbez = ['B'+str(count_bauelemente)+'.'+t for t in knotenbez]
            count_bauelemente = count_bauelemente + 1
            if befehl[4].count('M'):
                if bauteilmoeglichSpezial[befehl[1]].count('yscale=-1'):
                    befehl[1] = befehl[1] + r',yscale=-1' + ',xscale=-1' + \
                        ',rotate='+'-'+befehl[4][1:] + \
                        r',yscale=-1'  # +'\b'+'\b'+'1'
                else:
                    befehl[1] = befehl[1] + ',xscale=-1' + \
                        ',rotate='+'-'+befehl[4][1:]
            else:
                if bauteilmoeglichSpezial[befehl[1]].count('yscale=-1'):
                    befehl[1] = befehl[1] + r',yscale=-1' + \
                        ',rotate='+'-'+befehl[4][1:] + r',yscale=-1'
                else:
                    befehl[1] = befehl[1]+',rotate='+'-'+befehl[4][1:]
            for t,  name in enumerate(knotenbez):
                KnotenListe[KnotenSpeicher[t]][3] = name

        Bauteilliste.append(
            [KnotenSpeicher, befehl[1], bauteilbezeichnung, knotenbez])

    def KoordinatenKnotenSkalieren(scale):
        for idx, x in enumerate(KnotenListe):
            KnotenListe[idx][0] = np.array(KnotenListe[idx][0])*scale

    def getKnotenname(knoten):
        if KnotenListe[knoten][3]:
            return '(' + str(KnotenListe[knoten][3]) + ')'
        else:
            return printXY(KnotenListe[knoten][0])

    SpezialBauteilName = {
        'mesfet': ['D', 'G', 'S'],
        'njf': ['D', 'G', 'S'],
        'nmos': ['D', 'G', 'S'],
        'nmos4': ['D', 'G', 'S', 'bulk'],
        'npn': ['C', 'B', 'E'],
        'npn2': ['C', 'B', 'E'],
        'npn3': ['C', 'B', 'E'],
        'pjf': ['C', 'B', 'E'],
        'pmos': ['D', 'G', 'S'],
        'pmos4': ['D', 'G', 'S', 'bulk'],
        'pnp': ['C', 'B', 'E'],
        'pnp2': ['C', 'B', 'E'],
    }

    bauteilmoeglichSpezial = {
        'mesfet': 'njfet,anchor=D',
        'njf': 'njfet,anchor=D',
        'nmos': 'nigfete,anchor=D',
        'nmos4': 'nfet,anchor=D',
        'npn': 'npn,anchor=D',
        'npn2': 'npn,anchor=D',
        'npn3': 'npn,anchor=D',
        'njf': 'njfet,anchor=D',
        'pmos': 'pigfete,anchor=D,yscale=-1',
        'pmos4': 'pfet,anchor=D,yscale=-1',
        'pnp': 'pnp,anchor=D,yscale=-1',
        'pnp2': 'pnp,anchor=D,yscale=-1',
    }

    bauteilmoeglich = {
        'bi': 'controlled current source,i=\ ',
        'bi2': 'controlled current source,i_=\ ',
        'bv': 'controlled voltage source,v_=\ ',
        'cap': 'C',
        'csw': 'switch',
        'current': 'current source,i=\ ',
        'diode': 'D',
        'f': 'controlled current source,i=\ ',
        # 'FerriteBead': 'twoport',
        'h': 'voltage source,v_=\ ',
        'ind': 'L',
        # 'ind2': 'L',
        'LED': 'led',
        'load': 'vR',
        'load2': 'controlled current source,i=\ ',
        'polcap': 'eC',
        'res': 'R',
        'res2': 'R',
        'schottky': 'sDo',
                    'TVSdiode': 'zDo',
                    'varactor': 'VCo',
                    'voltage': 'voltage source,v_=\ ',
                    'zener': 'zDo', }

    def printXY(xy, offset=[0, 0]):
        return '(' + str(xy[0]-offset[0]) + ',' + str(xy[1]-offset[1]) + ')'

    def convertNeuName(name):
        ones = ["", "one", "two", "three", "four", "five",
                "six", "seven", "eight", "nine", "ten"]
        result = ''.join(ones[int(i)] if i.isdigit() else str(i) for i in name)
        result = result.replace("-", "")
        return result.replace("\\", "")

    def CreateDevFromLib(name, scale=1/64):

        if not os.path.isdir(lt_spice_directory):
            print('error! lt_spice_directory not exist: ', lt_spice_directory)
            return ''

        with open(os.path.join(lt_spice_directory, name + ".asy"), "r") as f:
            sym = f.readlines()

        pin = []
        pinName = []
        line = []
        rect = []
        circ = []
        arc = []
        text = []
        window = []
        for l in sym:
            words = l.split()
            if words[0] == 'PIN':      # Das wird nicht gezeichnet
                pin.append([int(words[1])*scale, -int(words[2])*scale])
            if words[0] == 'LINE':  # \draw (-1.5,0) -- (1.5,0);
                line.append([int(words[2])*scale, -int(words[3]) *
                            scale, int(words[4])*scale, -int(words[5])*scale])
            if words[0] == 'RECTANGLE':  # \draw (0,0) rectangle (1,1)
                rect.append([int(words[2])*scale, -int(words[3]) *
                            scale, int(words[4])*scale, -int(words[5])*scale])
            # \draw[x radius=2, y radius=1] (0,0) ellipse [];
            if words[0] == 'CIRCLE':
                circ.append([int(words[2])*scale, -int(words[3]) *
                            scale, int(words[4])*scale, -int(words[5])*scale])
            if words[0] == 'ARC':  # \draw (3mm,0mm) arc (0:30:3mm);
                arc.append([int(words[2])*scale, -int(words[3])*scale, int(words[4])*scale, -int(words[5]) *
                           scale, int(words[6])*scale, -int(words[7])*scale, int(words[8])*scale, -int(words[9])*scale])
            if words[0] == 'TEXT':  # \node[right] at (0,1) {bla} ;
                text.append([int(words[1])*scale, -int(words[2])
                            * scale, words[3], ' '.join(words[5:])])
            if words[0] == 'WINDOW':      # Das wird nicht gezeichnet
                window.append([int(words[2])*scale, -int(words[3])*scale])

        offset = pin[0] if pin else [0, 0]

        newLib = '\\def\\' + \
            convertNeuName(str(
                name)) + r'(#1)#2#3{%' + '\n' + r'  \begin{scope}[#1,transform canvas={scale=1}]' + '\n'

        for t in line:
            newLib = newLib + r'  \draw ' + \
                printXY(t[0:], offset) + ' -- ' + \
                printXY(t[2:], offset) + ';' + '\n'
        if window:  # \draw  (2,0.5) node[left] {$x$};
            t = window[0]
            newLib = newLib + r'  \draw ' + \
                printXY(t[0:], offset) + ' coordinate (#2 text);'+'\n'
            # newLib = newLib + r'  \draw ' + printXY(t[0:],offset) + ' node[right] {#3};\n'
        for t in circ:
            newLib = newLib + \
                r'  \draw[x radius=' + str((t[2]-t[0])/2) + \
                ', y radius=' + str((t[3]-t[1])/2) + ']'
            newLib = newLib + \
                printXY([(t[0]+t[2])/2, (t[1]+t[3])/2],
                        offset) + ' ellipse [];' + '\n'
        for t in arc:  # \draw (0,4)++(49: 1 and 2)  arc (49:360: 1 and 2);
            center = [(t[0]+t[2])/2, (t[1]+t[3])/2]
            Rx = (t[2]-t[0])/2
            Ry = (t[3]-t[1])/2
            StartWinkel = np.angle(
                (t[4]-center[0])+1j*(t[5]-center[1]))*180/np.pi
            EndWinkel = np.angle((t[6]-center[0])+1j *
                                 (t[7]-center[1]))*180/np.pi
            # if Rx < 0 or Ry < 0:
            #    t = StartWinkel
            #    StartWinkel = EndWinkel
            #    EndWinkel = t
            strR = str(abs(Rx)) + ' and ' + str(abs(Ry))
            newLib = newLib + r'  \draw ' + \
                printXY(center, offset) + '++( ' + \
                str(StartWinkel) + ': ' + strR
            newLib = newLib + ')  arc (' + str(StartWinkel) + \
                ':' + str(EndWinkel) + ': ' + strR + ');' + '\n'
        for t in rect:
            newLib = newLib + r'  \draw ' + \
                printXY(t[0:], offset) + ' rectangle ' + \
                printXY(t[2:], offset) + ';' + '\n'
        for t in text:
            newLib = newLib + \
                r'  \node[right] at ' + \
                printXY(t[0:], offset) + r'{' + t[3] + r'};' + '\n'
        for ind, t in enumerate(pin):
            newLib = newLib + r'  \draw ' + \
                printXY(t[0:], offset) + \
                ' coordinate (#2 X' + str(ind) + ');' + '\n'
            pinName.append('  X' + str(ind))

        newLib = newLib + r'  \end{scope}' + '\n'

        if window:
            newLib = newLib + r'  \draw (#2 text) node[right] {#3};'+'\n'

        newLib = newLib + r'}' + '\n'

        return newLib

    with open(filenameLTspice, "r") as f:
        data = f.readlines()

    words = []
    for line in data:
        words.append(line.split())

    BauteileAddSpeicher = []
    KnotenListe = []
    Bauteilliste = []
    DrahtListe = []
    count_bauelemente = 0

    for idx in enumerate(words):
        if(idx[1][0] == 'WIRE'):
            drahtADD(idx[1])

        if(idx[1][0] == 'FLAG' or idx[1][0] == 'TEXT'):
            gndTxtADD(idx[1])

        if(idx[1][0] == 'SYMBOL'):
            bauteilADD(idx[0], idx[1])

    KoordinatenKnotenSkalieren(1/64)

    for K1, K2 in DrahtListe:  # Draht, der zwei Bauelemente dierekt verbindet wird in zwei Teile geteilt
        if (len(KnotenListe[K1][2]) == 1 and len(KnotenListe[K2][2]) == 1
                and len(KnotenListe[K1][1]) == 1 and len(KnotenListe[K2][1]) == 1):

            DrahtAlt = KnotenListe[K1][1][0]

            neuerDraht = len(DrahtListe)  # Index für neuen Draht
            KnotenListe[K2][1] = [neuerDraht]  # neuen Draht mit K2 verbinden

            # Knoten zwischen den beiden alten Knoten hinzufügen
            K3 = len(KnotenListe)
            xyK3 = (KnotenListe[K1][0]+KnotenListe[K2][0])/2
            KnotenListe.append([xyK3, [neuerDraht, DrahtAlt], [], []])

            DrahtListe.append([K3, K2])  # neuen Draht hinzufügen
            # Alten Draht mit neuem Knoten verbinden
            DrahtListe[DrahtAlt][1] = K3

    knotenLaufIndex = 0
    KnotenKoordinaten = ''
    for ind, t in enumerate(KnotenListe):
        if not KnotenListe[ind][3] and (len(KnotenListe[ind][1])+len(KnotenListe[ind][2])) > 2:
            KnotenListe[ind][3] = 'X' + str(knotenLaufIndex)
            xy = printXY(KnotenListe[ind][0])
            KnotenKoordinaten = KnotenKoordinaten + '\draw ' + xy + \
                ' to[short,-*] ' + xy + \
                ' coordinate (' + KnotenListe[ind][3] + ');\n'
            knotenLaufIndex = knotenLaufIndex + 1

    # print('DrahtListe:')
    # print('       [Index Knoten1]  [Index Knoten2]')
    # print(DrahtListe)
    # print('Bauteilliste:')
    # print('        [Index Knoten]      Bauelement            Name      Knotenname')
    # print(Bauteilliste)
    # print('KnotenListe:')
    # print('                 [x,y]         Leitung      Bauelement      Knotenname')
    # print(KnotenListe)

    f = open(saveFile, "w")

    if fullExample:
        f.write(
            '\\documentclass[a4paper,12pt]{article} \n\\pagestyle{empty} \n\\usepackage{amsmath} \n\\usepackage{tikz} \n\\usepackage[siunitx,european]{circuitikz}')
        f.write('\n \n\\begin{document} \n\\centering \n')

    f.write(
        '\\ctikzset{tripoles/mos style/arrows} \n\\begin{circuitikz}[transform shape,scale=1] \n \n')

    f.write(KnotenKoordinaten)

    for t in BauteileAddSpeicher:
        f.write(CreateDevFromLib(t, scale=1/64))

    for Knoten, Bauteil, Name, Knotenname in Bauteilliste:
        if Bauteil in bauteilmoeglich:
            xy = [[], []]
            for idx, K1 in enumerate(Knoten):
                DrahtNum = first_item(KnotenListe[K1][1])
                # Am Bauelement ist keine Leitung angeschlossen
                if not isinstance(DrahtNum, int) or KnotenListe[K1][3]:
                    xy[idx] = K1
                else:
                    # Bauelement zwischen IndexK1-IndexK2 oder IndexK2-IndexK1
                    if DrahtListe[DrahtNum][0] == K1:
                        K2 = DrahtListe[DrahtNum][1]
                    else:
                        K2 = DrahtListe[DrahtNum][0]

                    xy[idx] = K2
                    DrahtListe[DrahtNum] = []
            f.write('\\draw %s to[%s,l=%s] %s ;\n' % (getKnotenname(
                xy[0]), bauteilmoeglich[Bauteil], Name, getKnotenname(xy[1])))

        if Bauteil == 'FLAG':
            f.write('\\draw %s node[ground] {} ;\n' % (getKnotenname(Knoten),))

        if Bauteil == 'TEXT':
            f.write('\\node[right] at %s {%s} ;\n' %
                    (getKnotenname(Knoten), Name))

        temp = Bauteil.split(',')[0]
        if temp in SpezialBauteilName:
            rot = Bauteil[len(temp):]
            rotation = rot.split('rotate=')[1].split(',')[0]
            Bauteil = Bauteil.split(',')[0]
            tKnotenname = Knotenname[0].partition(".")[0]
            if not rot.count('xscale=-1'):
                if bauteilmoeglichSpezial[Bauteil].count('yscale=-1'):
                    f.write('\\draw %s node[%s](%s){\\rotatebox{%s}{\\reflectbox{%s}}} ;\n' % (printXY(
                        KnotenListe[Knoten[0]][0]), bauteilmoeglichSpezial[Bauteil]+rot, tKnotenname, str(180+int(rotation)), Name))
                else:
                    f.write('\\draw %s node[%s](%s){\\rotatebox{%s}{%s}} ;\n' % (printXY(
                        KnotenListe[Knoten[0]][0]), bauteilmoeglichSpezial[Bauteil]+rot, tKnotenname, str(-int(rotation)), Name))
            else:
                if bauteilmoeglichSpezial[Bauteil].count('yscale=-1'):
                    f.write('\\draw %s node[%s](%s){\\rotatebox{%s}{%s}} ;\n' % (printXY(
                        KnotenListe[Knoten[0]][0]), bauteilmoeglichSpezial[Bauteil]+rot, tKnotenname, str(180+int(rotation)), Name))
                else:
                    f.write('\\draw %s node[%s](%s){\\rotatebox{%s}{\\reflectbox{%s}}} ;\n' % (printXY(
                        KnotenListe[Knoten[0]][0]), bauteilmoeglichSpezial[Bauteil]+rot, tKnotenname, str(-int(rotation)), Name))

        if Bauteil[:-5] in BauteileAddSpeicher:
            rot = Bauteil[-4:]
            if rot[0] == 'M':
                rot = 'rotate=' + rot[1:] + ',xscale=-1'
            else:
                rot = 'rotate=' + rot[1:]

            Bauteil = Bauteil[:-5]
            tKnotenname = Knotenname[0].partition(" ")[0]
            f.write('\\%s (shift={%s},%s) {%s} {%s};\n' % (convertNeuName(
                Bauteil), printXY(KnotenListe[Knoten[0]][0]), rot, tKnotenname, Name))
    for x in DrahtListe:
        if len(x) != 0:
            f.write('\\draw %s to[short,-] %s ;\n' %
                    (getKnotenname(x[0]), getKnotenname(x[1])))

    f.write('\n\\end{circuitikz}')
    if fullExample:
        f.write('\n\\end{document}')

    f.close()

    print('Congratulations. The run was successful.')
