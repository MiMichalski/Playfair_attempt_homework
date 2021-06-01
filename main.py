# -*- coding: utf-8 -*-
# playfair cipher
from __future__ import unicode_literals
import numpy as np
import random
from math import log10
import time
import queue
import threading


class Ngram_score(object):
    def __init__(self, ngramfile, sep=' '):
        ''' load a file containing ngrams and counts, calculate log probabilities '''
        self.ngrams = {}
        for line in open(ngramfile, encoding='utf-8'):
            key, count = line.split(sep)
            self.ngrams[key] = int(count)
        self.L = len(key)
        self.N = sum(self.ngrams.values())
        # calculate log probabilities
        for key in self.ngrams.keys():
            self.ngrams[key] = log10(float(self.ngrams[key])/self.N)
        self.floor = log10(0.01/self.N)

    def score(self, text):
        ''' compute the score of text '''
        score = 0
        ngrams = self.ngrams.__getitem__
        for i in range(len(text)-self.L+1):
            if text[i:i+self.L] in self.ngrams:
                score += ngrams(text[i:i+self.L])
            else:
                score += self.floor
        return score


ngs = Ngram_score('polish_trigrams.txt')

alfabet = "AĄBCĆDEĘFGHIJKLŁMNŃOÓPQRSŚTUVWXYZŹŻ8"
tj = "Zaprawdę powiadam wam, oto nadchodzi wiek miecza i topora, wiek wilczej zamieci. Nadchodzi Czas Białego Zimna i Białego Światła, Czas Szaleństwa i Czas Pogardy, Tedd Deireadh, Czas Końca. Świat umrze wśród mrozu, a odrodzi się wraz z nowym słońcem. Odrodzi się ze Starszej Krwi, z Hen Ichaer, z zasianego ziarna. Ziarna, które nie wykiełkuje, lecz wybuchnie płomieniem. Ess'tuath esse! Tak będzie! Wypatrujcie znaków! Jakie to będą znaki, rzeknę wam - wprzód spłynie ziemia krwią Aen Seidhe, Krwią Elfów... Aen Ithlinnespeath, przepowiednia Ithlinne Aegli aep Aevenien Rozdział pierwszy Miasto płonęło. Wąskie uliczki, wiodące ku fosie, ku pierwszemu tarasowi, ziały dymem i żarem, płomienie pożerały ciasno skupione strzechy domostw, lizały mury zamku. Od zachodu, od strony bramy portowej, narastał wrzask, odgłosy zajadłej walki, głuche, wstrząsające murem uderzenia taranu. Napastnicy ogarnęli ich niespodziewanie, przełamawszy barykadę bronioną przez nielicznych żołnierzy, mieszczan z halabardami i kuszników z cechu. Okryte czarnymi kropierzami konie przeleciały nad zaporą jak upiory, jasne, rozmigotane brzeszczoty siały śmierć wśród uciekających obrońców. Ciri poczuła, jak wiozący ją na łęku rycerz spina gwałtownie konia. Usłyszała jego krzyk. Trzymaj się, krzyczał. Trzymaj się! Inni rycerze w barwach Cintry wyprzedzili ich, w pędzie ścięli się z Nilfgaardczykami. Ciri widziała to przez moment, kątem oka - szaleńczy wir błękitno - złotych i czarnych płaszczy wśród szczęku stali, łomotu kling o tarcze, rżenia koni... Krzyk. Nie, nie krzyk. Wrzask. Trzymaj się! Strach. Każdy wstrząs, każde szarpnięcie, każdy skok konia rwie do bólu dłonie zaciśnięte na rzemieniu. Nogi w bolesnym przykurczu nie znajdują oparcia, oczy łzawią od dymu. Obejmujące ją ramię dusi, dławi, boleśnie zgniata żebra. Dookoła narasta krzyk, taki, jakiego nie słyszała nigdy dotąd. Co trzeba zrobić człowiekowi, by tak krzyczał? Strach. Obezwładniający, paraliżujący, duszący strach. Znowu szczęk żelaza, chrap koni. Domy dookoła tańczą, buchające ogniem okna są nagle tam, gdzie przed chwilą była błotnista uliczka, zasłana trupami, zawalona porzuconym dobytkiem uciekinierów. Rycerz za jej plecami zanosi się nagle dziwnym, chrapliwym kaszlem. Na wczepione w rzemień ręce bucha krew. Wrzask. Świst strzał. Upadek, wstrząs, bolesne uderzenie o zbroję. Obok łomocą kopyta, nad głową miga koński brzuch i wystrzępiony popręg, drugi koński brzuch, rozwiany czarny kropierz. Stęknięcia, takie, jakie wydaje drwal rąbiący drzewo. Ale to nie drzewo, to żelazo o żelazo. Krzyk, zdławiony i głuchy, tuż przy niej coś wielkiego i czarnego wali się z pluskiem w błoto, bryzga krwią."
tj = ''.join(e for e in tj if e.isalnum()).upper()
tj = tj[:1500]
keyLength = 8
key = ''.join(random.choice(alfabet) for i in range(keyLength))
# print(key)
# print(tj)


def encodeKeyToMatrix(keyToEncode):
    # matrix 6x6
    keyBeforeMatrixConversion = "".join(dict.fromkeys(
        "".join(dict.fromkeys(keyToEncode.upper()))+alfabet))
    keyMatrix = np.array(
        [char for char in keyBeforeMatrixConversion]).reshape(6, 6)
    return keyMatrix


def encodeMessage(text, key):
    text = text.upper()
    encodedText = ""
    for i in range(0, len(text)-1, 2):
        a = np.where(key == text[i])
        b = np.where(key == text[i+1])
        ax, ay = a[0], a[1]
        bx, by = b[0], b[1]
        oa, ob = '', ''
        if ax == bx:
            oa = key[ax, (ay+1) % np.size(key, 1)]
            ob = key[bx, (by+1) % np.size(key, 1)]
        elif ay == by:
            oa = key[(ax+1) % np.size(key, 0), ay]
            ob = key[(bx+1) % np.size(key, 0), by]
        else:
            oa = key[ax, by]
            ob = key[bx, ay]
        encodedText += oa[0]
        encodedText += ob[0]
    return encodedText


def decodeMessage(kt, key):
    #t = time.time()
    decodedText = ""
    dictionary = {}
    for i in range(np.size(key, 0)):
        for j in range(np.size(key, 1)):
            dictionary[key[i, j]] = [i, j]
    xSize = np.size(key, 0)
    ySize = np.size(key, 1)
    oa, ob = '', ''
    for i in range(0, len(kt)-1, 2):
        ax, ay = dictionary[kt[i]][0], dictionary[kt[i]][1]
        bx, by = dictionary[kt[i+1]][0], dictionary[kt[i+1]][1]
        if ax == bx:
            oa = key[ax, (ay-1) % ySize]
            ob = key[bx, (by-1) % ySize]
        elif ay == by:
            oa = key[(ax-1) % xSize, ay]
            ob = key[(bx-1) % xSize, by]
        else:
            oa = key[ax, by]
            ob = key[bx, ay]
        decodedText += oa[0]
        decodedText += ob[0]
    # print(time.time()-t)
    return decodedText


def attackEvo(kt):
    # 2000-4000 domyślnie
    startingPop = 4000
    step = 0
    evaluatedPops = []
    for i in range(startingPop):
        tempKey = newKey(keyLength)
        # evaluatedPops=[[ngs score, key, age ]]
        evaluatedPops.append(
            [ngs.score(decodeMessage(kt, tempKey)), tempKey, 0])
    evaluatedPops = sortTable(evaluatedPops)

    bestScore = -20000
    t0 = time.time()
    while bestScore < len(encoded)*-3.9:
        evaluatedPops = evolutionStep(evaluatedPops, startingPop, step)
        bestScore = evaluatedPops[0][0]
        step += 1
        print("time: ", time.time()-t0)
    print(evaluatedPops[0])
    print(decodeMessage(encoded, evaluatedPops[0][1]))

# od długości 11-12 klucz   potem zwiększyć, jeden sposób to ograniczyć do 5x5, zmieniać kolejność wierszy lub kolumn
# raczej skrócić do 5x5 bo za dużo zajmie, nie wiem, wykonywać bardzo wiele zmian na kluczu na raz, ewolucyjny to złe podejście
# szukać zmian które najmniej pogarszają, dziedziczenie nie może tworzyć zupełnie złych wyników (nasze może)
# szyfr nazywa się playfair nie fairplay, jednak ewolucyjne jest ok, ale dziedziczenie zjebaliśmy
# z jednej pary rodziców mamy tworzyć nie 1 child ale kilkaset-kilka tysięcy
# można też spróbować bruteforcem, będzie szybciej
# angielski 5x5 jest rozwiązywany w kilkanaście minut, masz ma limitu godzinę
# jeśli stracimy wiarę to można spróbować wyżażaniem
# podobno jedną z metod jest odwracanie kolejności wierszy


def evolutionStep(evaluatedPops, populationSize, step):
    # age of to old pops
    ageOfPop = 6
    # new keys to add
    childs = []
    # best keys % of all pops
    better = evaluatedPops[: len(evaluatedPops)//50]

    # remove old pops
    deleted = 0
    if step > ageOfPop:
        for i in range(10, len(evaluatedPops)):
            if evaluatedPops[i-deleted][2] > ageOfPop:
                del evaluatedPops[i-deleted]
                deleted += 1

    # increment age
    for i in range(len(evaluatedPops)):
        evaluatedPops[i][2] += 1

    # 90% chance to inherit and alter from better keys
    if random.uniform(0, 1) > 0.1:
        for x in better:
            childs.append(offspringKey(x))
            for x in inherit(better):
                childs.append(x)
    # 10% chance to inherit and alter from random keys
    else:
        for i in range(0, 50):
            x = evaluatedPops[random.randrange(50, len(evaluatedPops)-1)]
            childs.append(offspringKey(x))
            for x in inherit(evaluatedPops):
                childs.append(x)

    # add new random keys
    if random.uniform(0, 1) > 0.1:
        for i in range(100):
            childs.append(newKey(keyLength))
    else:
        for i in range(800):
            childs.append(newKey(keyLength))

    print("new childs:", len(childs), "deleted old pops: ", deleted)

    # add childs and sort
    evaluatedPops = appendNewChild(evaluatedPops, childs)
    evaluatedPops = sortTable(evaluatedPops)

    # if step % 10 == 0:
    #     print("step: ", step, [x[0] for x in evaluatedPops[0:5]])
    print("step: ", step, [x[0] for x in evaluatedPops[0:5]])

    # return pops and remove worst keys
    return evaluatedPops[0:populationSize]

# 50 generacji inherit = 0.5s


def inherit(arr1):
    # t = time.time()  # zapisuj co
    childs = []    #
    for j in range(0, 100):
        cP1 = np.copy(arr1[random.randint(0, len(arr1)-1)])
        cP2 = np.copy(arr1[random.randint(0, len(arr1)-1)])
        keyP1 = ""
        keyP2 = ""
        for i in range(keyLength):
            keyP1 += cP1[1][i//6, i % 6]
            keyP2 += cP2[1][i//6, i % 6]
        keyP = keyP1 + keyP2
        keyP = list(keyP)
        random.shuffle(keyP)
        keyP = "".join(dict.fromkeys(''.join(keyP)))
        childs.append(encodeKeyToMatrix(keyP[0:keyLength]))

    # print(time.time()-t)

    return childs

# 15s

# todo poprawić wydajność tego czegoś
# https://www.tutorialspoint.com/python3/python_multithreading.htm
#


def appendNewChild(pops, childs):
    unique = {}
    for i in pops:
        unique[round(i[0], 3)] = i
    # 0.003-0.008
    #0.003 * 4000

    # #Multithreading part\
    threadCount = 30
    workPart = [[] for i in range(threadCount)]
    threads = []
    for i in range(len(childs)-1):
        workPart[i % threadCount].append(childs[i])

    for threadID in range(1, threadCount + 1):
        thread = ComputeThread(threadID, workPart[threadID-1])
        thread.setDaemon(True)
        thread.start()
        threads.append(thread)

    threadingResult = []
    for t in threads:
        t.join()
        threadingResult += t.results

    for j in threadingResult:  #
        unique[round(j[0], 3)] = j

    # for child in childs:
    #     childData = addNewToPopulation(child)
    #     unique[round(childData[0], 3)] = childData

    return list(unique.values())


def addNewToPopulation(keyMatrix):
    return [ngs.score(decodeMessage(encoded, keyMatrix)), keyMatrix, 0]


def newKey(leng=10):
    return encodeKeyToMatrix(''.join(random.choice(alfabet) for i in range(leng)))


def sortTable(array):
    array.sort(key=lambda x: x[0])
    table = array
    newTable = []
    for i in range(len(table)):
        newTable.append(table[len(table)-1-i])
    return newTable


def offspringKey(key):
    newKey = np.copy(key)
    a, b, c, d = random.randint(0, 5), random.randint(
        0, 5), random.randint(0, 5), random.randint(0, 5)
    if a == c and b == d:
        b = (b+1) % 6
    tempA = newKey[1][a, b]
    tempB = newKey[1][c, d]
    newKey[1][a, b] = tempB
    newKey[1][c, d] = tempA
    return newKey[1]


#Multithreading
class ComputeThread(threading.Thread):
    def __init__(self, threadID, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.q = q
        self.results = []

    def run(self):
        self.results = process_data(self.q)


def process_data(procesQueue):
    #t = time.time()
    outputArray = []
    for arg in procesQueue:
        outputArray.append((addNewToPopulation(arg)))
    #print("Processed: ", len(outputArray), " in ", time.time()-t, "s")
    return outputArray


#---------------------------------wykonanie programu

keyMatrix = encodeKeyToMatrix(key)
print(keyMatrix)
encoded = encodeMessage(tj, keyMatrix)
decoded = decodeMessage(encoded, keyMatrix)
print(ngs.score(encoded))
print(ngs.score(decoded))
# -3.617869 współczynnik tekstu, celować w -3.65/znak
# print(ngs.score(decoded)/len(decoded))
attackEvo(encoded)
