import numpy as np
import os


def ConvertForAllLTspiceFilesFormFolderToTEX(path='.', lt_spice_directory=r'C:\Program Files\LTC\LTspiceXVII\lib\sym', fullExample=0):
    for filename in os.listdir(path):
        if os.path.isfile(os.path.join(path, filename)):
            if filename.endswith('.asc'):
                print('Convert: ' + filename)
                LtSpiceToLatex(
                    filenameLTspice=filename, lt_spice_directory=lt_spice_directory, fullExample=fullExample)


componentsCount = 0
componentsAddMemory = []


def LtSpiceToLatex(saveFile='', filenameLTspice='Draft.asc', lt_spice_directory=r'C:\Program Files\LTC\LTspiceXVII\lib\sym', fullExample=0):

    global componentsCount
    global componentsAddMemory

    if saveFile == '':
        saveFile = os.path.splitext(filenameLTspice)[0] + r'.tex'

    print('saveFile: ', saveFile)

    def firstItem(listOrEmpty):
        if listOrEmpty:
            return listOrEmpty[0]

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

    def nodeSearch(coordinate):
        node = [idx for idx, x1 in enumerate(
            nodeList) if x1[0] == coordinate]
        if node == []:
            node = [len(nodeList)]
            nodeList.append([coordinate, [], [], []])
        return node[0]

    def wireAddition(order):
        x1 = (int(order[1]), -int(order[2]))
        x2 = (int(order[3]), -int(order[4]))
        wireQuantity = len(wireList)

        node1 = nodeSearch(x1)
        node2 = nodeSearch(x2)
        nodeList[node1][1].append(wireQuantity)
        nodeList[node2][1].append(wireQuantity)

        wireList.append([node1, node2])

    def groundTextAddition(order):
        x1 = (int(order[1]), -int(order[2]))
        componentQuantity = len(componentList)
        node = nodeSearch(x1)
        nodeList[node][2].append(componentQuantity)
        if order[0] == 'FLAG' and order[3] == '0':
            componentList.append([node, 'FLAG', '', []])
        elif order[0] == 'FLAG':
            text = ' '.join(order[3:])
            componentList.append([node, 'TEXT', text, []])
        else:
            text = ' '.join(order[5:]).replace(';', '')
            componentList.append([node, 'TEXT', text, []])

    def componentAddition(idx, order):

        x = np.array([int(order[2]), -int(order[3])])
        pin = findPinsInLib(order[1])
        componentQuantity = len(componentList)

        Rotation = {
            'R0': [[1, 0], [0, 1]],
            'R90': [[0, -1], [1, 0]],
            'R180': [[-1, 0], [0, -1]],
            'R270': [[0, 1], [-1, 0]],
            'M0': [[-1, 0], [0, 1]],
            'M90': [[0, -1], [-1, 0]],
            'M180': [[1, 0], [0, -1]],
            'M270': [[0, 1], [1, 0]], }

        pin = np.dot(pin, Rotation[order[4]])

        nodeMemory = []
        for pinn in pin:
            node = nodeSearch(tuple(pinn+x))
            nodeMemory.append(node)
            nodeList[node][2].append(componentQuantity)

        componentDesignation = ''
        for i in range(idx+1, idx+4):
            if words[i][0] == 'SYMATTR':
                componentDesignation = words[i][2]
                if componentDesignation.count('_') > 0 and componentDesignation.count('$') < 2:
                    componentDesignation = r'$'+componentDesignation+r'$'
                break

        global componentsCount
        global componentsAddMemory
        nodeRelated = []
        if not order[1] in possibleComponent and not order[1] in specialComponentName:
            if not order[1] in componentsAddMemory:
                print('The following component is new: ' + order[1])
                componentsAddMemory.append(order[1])

            nodeRelated = []
            for ind, t in enumerate(pin):
                nodeRelated.append('B'+str(componentsCount) + ' X' + str(ind))

            componentsCount = componentsCount + 1
            order[1] = order[1] + ' ' + (order[4]+'  ')[0:4]
            for t,  name in enumerate(nodeRelated):
                nodeList[nodeMemory[t]][3] = name

        if not order[1] in possibleComponent and order[1] in specialComponentName:
            nodeRelated = specialComponentName[order[1]]  # []
            nodeRelated = ['B'+str(componentsCount)+'.'+t for t in nodeRelated]
            componentsCount = componentsCount + 1
            if order[4].count('M'):
                if isSpecialComponent[order[1]].count('yscale=-1'):
                    order[1] = order[1] + r',yscale=-1' + ',xscale=-1' + \
                        ',rotate='+'-'+order[4][1:] + \
                        r',yscale=-1'  # +'\b'+'\b'+'1'
                else:
                    order[1] = order[1] + ',xscale=-1' + \
                        ',rotate='+'-'+order[4][1:]
            else:
                if isSpecialComponent[order[1]].count('yscale=-1'):
                    order[1] = order[1] + r',yscale=-1' + \
                        ',rotate='+'-'+order[4][1:] + r',yscale=-1'
                else:
                    order[1] = order[1]+',rotate='+'-'+order[4][1:]
            for t,  name in enumerate(nodeRelated):
                nodeList[nodeMemory[t]][3] = name

        componentList.append(
            [nodeMemory, order[1], componentDesignation, nodeRelated])

    def coordinateNodeScale(scale):
        for idx, x in enumerate(nodeList):
            nodeList[idx][0] = np.array(nodeList[idx][0])*scale

    def getNodeName(node):
        if nodeList[node][3]:
            return '(' + str(nodeList[node][3]) + ')'
        else:
            return printXY(nodeList[node][0])

    specialComponentName = {
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

    isSpecialComponent = {
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

    possibleComponent = {
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

    def convertNewName(name):
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
            convertNewName(str(
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
            startAngle = np.angle(
                (t[4]-center[0])+1j*(t[5]-center[1]))*180/np.pi
            endAngle = np.angle((t[6]-center[0])+1j *
                                (t[7]-center[1]))*180/np.pi
            # if Rx < 0 or Ry < 0:
            #    t = startAngle
            #    startAngle = endAngle
            #    endAngle = t
            strR = str(abs(Rx)) + ' and ' + str(abs(Ry))
            newLib = newLib + r'  \draw ' + \
                printXY(center, offset) + '++( ' + \
                str(startAngle) + ': ' + strR
            newLib = newLib + ')  arc (' + str(startAngle) + \
                ':' + str(endAngle) + ': ' + strR + ');' + '\n'
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

    componentsAddMemory = []
    nodeList = []
    componentList = []
    wireList = []
    componentsCount = 0

    for idx in enumerate(words):
        if(idx[1][0] == 'WIRE'):
            wireAddition(idx[1])

        if(idx[1][0] == 'FLAG' or idx[1][0] == 'TEXT'):
            groundTextAddition(idx[1])

        if(idx[1][0] == 'SYMBOL'):
            componentAddition(idx[0], idx[1])

    coordinateNodeScale(1/64)

    for K1, K2 in wireList:  # Draht, der zwei Bauelemente dierekt verbindet wird in zwei Teile geteilt
        if (len(nodeList[K1][2]) == 1 and len(nodeList[K2][2]) == 1
                and len(nodeList[K1][1]) == 1 and len(nodeList[K2][1]) == 1):

            oldWire = nodeList[K1][1][0]

            newWire = len(wireList)  # Index für neuen Draht
            nodeList[K2][1] = [newWire]  # neuen Draht mit K2 verbinden

            # node zwischen den beiden alten node hinzufügen
            K3 = len(nodeList)
            xyK3 = (nodeList[K1][0]+nodeList[K2][0])/2
            nodeList.append([xyK3, [newWire, oldWire], [], []])

            wireList.append([K3, K2])  # neuen Draht hinzufügen
            # Alten Draht mit neuem node verbinden
            wireList[oldWire][1] = K3

    currentNodeIndex = 0
    nodeCoordinates = ''
    for ind, t in enumerate(nodeList):
        if not nodeList[ind][3] and (len(nodeList[ind][1])+len(nodeList[ind][2])) > 2:
            nodeList[ind][3] = 'X' + str(currentNodeIndex)
            xy = printXY(nodeList[ind][0])
            nodeCoordinates = nodeCoordinates + '\draw ' + xy + \
                ' to[short,-*] ' + xy + \
                ' coordinate (' + nodeList[ind][3] + ');\n'
            currentNodeIndex = currentNodeIndex + 1

    # print('wireList:')
    # print('       [Index node1]  [Index node2]')
    # print(wireList)
    # print('componentList:')
    # print('        [Index node]      component            name      nodename')
    # print(componentList)
    # print('nodeList:')
    # print('                 [x,y]         wire      component      nodename')
    # print(nodeList)

    f = open(saveFile, "w")

    if fullExample:
        f.write(
            '\\documentclass[a4paper,12pt]{article} \n\\pagestyle{empty} \n\\usepackage{amsmath} \n\\usepackage{tikz} \n\\usepackage[siunitx,european]{circuitikz}')
        f.write('\n \n\\begin{document} \n\\centering \n')

    f.write(
        '\\ctikzset{tripoles/mos style/arrows} \n\\begin{circuitikz}[transform shape,scale=1] \n \n')

    f.write(nodeCoordinates)

    for t in componentsAddMemory:
        f.write(CreateDevFromLib(t, scale=1/64))

    for node, component, Name, nodename in componentList:
        if component in possibleComponent:
            xy = [[], []]
            for idx, K1 in enumerate(node):
                wireNumber = firstItem(nodeList[K1][1])
                # Am Bauelement ist keine Leitung angeschlossen
                if not isinstance(wireNumber, int) or nodeList[K1][3]:
                    xy[idx] = K1
                else:
                    # Bauelement zwischen IndexK1-IndexK2 oder IndexK2-IndexK1
                    if wireList[wireNumber][0] == K1:
                        K2 = wireList[wireNumber][1]
                    else:
                        K2 = wireList[wireNumber][0]

                    xy[idx] = K2
                    wireList[wireNumber] = []
            f.write('\\draw %s to[%s,l=%s] %s ;\n' % (getNodeName(
                xy[0]), possibleComponent[component], Name, getNodeName(xy[1])))

        if component == 'FLAG':
            f.write('\\draw %s node[ground] {} ;\n' % (getNodeName(node),))

        if component == 'TEXT':
            f.write('\\node[right] at %s {%s} ;\n' %
                    (getNodeName(node), Name))

        temp = component.split(',')[0]
        if temp in specialComponentName:
            rot = component[len(temp):]
            rotation = rot.split('rotate=')[1].split(',')[0]
            component = component.split(',')[0]
            tnodename = nodename[0].partition(".")[0]
            if not rot.count('xscale=-1'):
                if isSpecialComponent[component].count('yscale=-1'):
                    f.write('\\draw %s node[%s](%s){\\rotatebox{%s}{\\reflectbox{%s}}} ;\n' % (printXY(
                        nodeList[node[0]][0]), isSpecialComponent[component]+rot, tnodename, str(180+int(rotation)), Name))
                else:
                    f.write('\\draw %s node[%s](%s){\\rotatebox{%s}{%s}} ;\n' % (printXY(
                        nodeList[node[0]][0]), isSpecialComponent[component]+rot, tnodename, str(-int(rotation)), Name))
            else:
                if isSpecialComponent[component].count('yscale=-1'):
                    f.write('\\draw %s node[%s](%s){\\rotatebox{%s}{%s}} ;\n' % (printXY(
                        nodeList[node[0]][0]), isSpecialComponent[component]+rot, tnodename, str(180+int(rotation)), Name))
                else:
                    f.write('\\draw %s node[%s](%s){\\rotatebox{%s}{\\reflectbox{%s}}} ;\n' % (printXY(
                        nodeList[node[0]][0]), isSpecialComponent[component]+rot, tnodename, str(-int(rotation)), Name))

        if component[:-5] in componentsAddMemory:
            rot = component[-4:]
            if rot[0] == 'M':
                rot = 'rotate=' + rot[1:] + ',xscale=-1'
            else:
                rot = 'rotate=' + rot[1:]

            component = component[:-5]
            tnodename = nodename[0].partition(" ")[0]
            f.write('\\%s (shift={%s},%s) {%s} {%s};\n' % (convertNewName(
                component), printXY(nodeList[node[0]][0]), rot, tnodename, Name))
    for x in wireList:
        if len(x) != 0:
            f.write('\\draw %s to[short,-] %s ;\n' %
                    (getNodeName(x[0]), getNodeName(x[1])))

    f.write('\n\\end{circuitikz}')
    if fullExample:
        f.write('\n\\end{document}')

    f.close()
    f = open(saveFile, "r")
    temp = f.read()
    f.close()

    print('Congratulations. The run was successful.')
    return temp
