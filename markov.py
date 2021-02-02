import random



sentences_dividers = ".?!;"
ponctuation = ".,!?;"



def cleanWord(word):
    while len(word) and not word[0].isalpha():
        word = word[1:]
    while len(word) and not word[-1].isalpha():
        word = word[:-1]
    
    return word



def test_cleanWord():
    inputList = ["hello", "c'hwi", " ah !", "n'imps!", "...lalal", "!"] 
    outputList = ["hello", "c'hwi", "ah", "n'imps", "lalal", ""]
    
    for i in range(len(inputList)):
        print(inputList[i], end=' ')
        if cleanWord(inputList[i]) != outputList[i]:
            print("FAIL", cleanWord(inputList[i]))
        else:
            print("OK")



def splitLine(line):
    return [cleanWord(word.lower()) for word in line.split()]



def tokenize(line):
    for c in '"()#}{[]%\/':
        line = line.replace(c, '')

    tokens = []
    i = 0
    j = 0
    while j < len(line):
        while j < len(line) and (line[j].isalnum() or line[j] in "-'_"):
            j += 1
        
        token = line[i:j].strip().lower()
        if token:
            if token.isdigit():
                token = "{num}"
            tokens.append(token)
        i = j
        j += 1

    # Parse last character
    token = line[i:j].strip().lower()
    if token:
        if token.isdigit():
            token = "{num}"
        tokens.append(token)

    return ['['] + tokens + [']']



def reformat(tokens):
    capitalize = True
    insertSpace = False
    sentence = ""
    for token in tokens:
        if capitalize:
            token = token.capitalize()
            capitalize = False
        if token in ".!?":
            capitalize = True
        if len(sentence) > 0:
            insertSpace = not (token in ".,;" or (token in "!?" and sentence[-1] in "!?"))
        sentence += " " + token if insertSpace else token

    return sentence.strip()


class Markov(object):
    def __init__(self):
        self.markov = dict()
    
    
    def feed(self, tok1, tok2):
        if tok1 in self.markov:
            if tok2 in self.markov[tok1]:
                self.markov[tok1][tok2] += 1
            else:
                self.markov[tok1][tok2] = 1
        else:
           self.markov[tok1] = {tok2 : 1}
    
    
    def next(self, token):
        if token in self.markov:
            k, v = zip(*self.markov[token].items())
            k = list(k)
            v = list(v)
            weights = []
            s = 0
            for i in range(len(v)):
                weights.append(v[i] + s)
                s += v[i]
            r = random.randrange(s)
            
            # Find corresponding index
            for i in range(len(weights)):
                if r < weights[i]:
                    break
            
            return k[i]
    
    def generate(self):
        phrase = []
        l = '['
        while l != ']':
            l = self.next(l)
            phrase.append(l)
        
        return ''.join(phrase[:-1])
    
    def generate2(self):
        phrase = ['[']
        while phrase[-1] != ']':
            phrase.append(self.next(tuple(phrase[-2:])))
        
        return reformat(phrase[1:-1])
    
    def generate3(self):
        phrase = ['[']
        while phrase[-1] != ']':
            phrase.append(self.next(phrase[-1]))
        
        return reformat(phrase[1:-1])



def test_markov(filename):
    with open(filename, "r") as f:
        names = f.readlines()
    
    m = Markov()
    for name in names:
        name = "[{}]".format(name.strip().lower())
        for i in range(len(name)-1): 
            m.feed(name[i], name[i+1])
    
    return m
    


def test_markov2(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
    
    m = Markov()
    for line in lines: 
        line = tokenize(line)
        if len(line) <= 2:
            continue
        for i in range(len(line)-1): 
            m.feed(tuple(line[max(0,i-1): max(1,i+1)]), line[i+1])
    
    return m



def test_markov3(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
    
    m = Markov()
    for line in lines: 
        line = tokenize(line)
        if len(line) <= 2:
            continue
        for i in range(len(line)-1): 
            m.feed(line[i], line[i+1])
    
    return m
