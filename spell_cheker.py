import re
from collections import Counter
import codecs

table_size = 200003

class Word:
    def __init__(self, word, occ, prob):
        self.valid_hash_pos = False
        self.word = word
        self.occ = occ
        self.prob = prob

    def add_occ(self):
        self.occ += 1
        self.prob = self.occ / N

class Corrected:
    def __init__(self, correction, occ):
        self.correction = correction
        self.occ = occ


class Correction:
    def __init__(self, word, corr):
        self.word = word
        self.corr = corr
        self.correction = []
        if corr != "":
            self.add_correction((Corrected(corr, 1)))

    def add_correction(self, x):
        self.correction.append(x) # adds new object Corrected

    def add_occ(self, correction):
        # method updates occ var in Corrected objects in list, returns sorted list
        for e in self.correction:
            if e.correction == correction:
                e.occ += 1
        self.correction.sort(key=lambda x: x.occ, reverse=True)

def get_N():
    word_set = codecs.open('words_count_clean.txt', encoding='latin1')
    n = 0
    for line in word_set:
        if line:
            line = line.split('\t')
            n += int(line[0]) # get n
    return n


def start_dict_hash_table(table):
    word_set = codecs.open('words_count_clean.txt', encoding='latin1')
    for line in word_set:
        if line:
            line = line.split('\t')
            add_word_hash_table(Word(line[1], int(line[0]), int(line[0])/N), table)

# init hash tables
portuguese_hash_table = [Word("", 0, 0) for n in range(table_size)] # start word hashtable with prime
correction_hash_table = [Correction("","") for n in range(table_size)]
N = get_N()


def get_word_value(word):
    # get word value using division method
    value = 0
    for i in range(len(word)):
        value += ord(word[i]) * (256) ** (len(word) - 1 - i)
    return value


def word_in_hash_table(word, table):
    # Check if word is in the hash table
    code = get_word_value(word) % table_size
    c = 0
    while True:
        code_s = (code + c ** 2) % table_size
        if table[code_s].word == word:
            return True
        elif table[code_s].word != "" and (table[code_s].word != word):
            c += 1
        elif table[code_s].word == "":
            return False


def add_word_hash_table(object, table):
     c = 0
     code = get_word_value(object.word) % table_size
     code_s = code

     if not word_in_hash_table(object.word, table):
         while table[code_s].word != "":
             c += 1
             code_s = (code + c ** 2) % table_size
         table[code_s] = object
     else:
         while table[code_s].word != object.word:
             c += 1
             code_s = (code + c ** 2) % table_size
         table[code_s].add_correction(Corrected(object.corr, 1))


# --------------------------------- Code from https://norvig.com/spell-correct.html

def edits1(word):
    # All edits that are one edit away from `word`.
    letters    = 'abcçdeéèfghijklmnopqrstuvwxyzàáãâêóòêôúìíîõ'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word):
    # All edits that are two edits away from `word`
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))
# ----------------------------------------------------------------------------------


def get_candidates(word, already_cheked):
    # returns list of candidates, gives priority to the candidates originated
    # by the edits1 method, only if (len(edits1) < 5) adds the ones that come from edits2
    o_c = []
    o_c2 = []
    i = 0
    for cand in known(edits1(word)):
        if cand not in o_c and cand not in already_cheked:
            o_c.append(get_object_in_hash_table(cand, portuguese_hash_table))
    if len(o_c) < 5:
        o_c = sorted(o_c, key=lambda x: x.prob, reverse=True)
        for cand in known(edits2(word)):
            if cand not in o_c and cand not in already_cheked:
                o_c2.append(get_object_in_hash_table(cand, portuguese_hash_table))
        o_c2 = sorted(o_c2, key=lambda x: x.prob, reverse=True)
        while len(o_c) < 5 and i < len(o_c2):
            if o_c2[i] not in o_c:
                o_c.append(o_c2[i])
            i += 1
    return o_c[0:5]


def get_object_in_hash_table(word, table):
    # search object in hash table based on the word
    code = get_word_value(word) % table_size
    c = 0
    while True:
        code_s = (code + c ** 2) % table_size
        if table[code_s] != "" and (table[code_s].word != word):
            c += 1
        elif table[code_s].word == word:
            return table[code_s]
        else:
            return False

def known(words):
    # check wich words in array 'words' are in the dictionary and return them
    return [word for word in words if word_in_hash_table(word, portuguese_hash_table)]


def spell_checker():
    while True:
        usr_text = input("Phrase: ")
        if(usr_text[-6:] == "FIMFIM"):
            usr_text = usr_text[0:-6]
            usr_words = re.findall(r'\w+', usr_text.lower()) # word set for analysis
            for word in usr_words:
                n_corrs = 0
                if word_in_hash_table(word, portuguese_hash_table):
                    get_object_in_hash_table(word, portuguese_hash_table).add_occ()
                elif not word_in_hash_table(word, portuguese_hash_table):
                    # word not in dictionary, try to find it's correction
                    rsp = input("Word '"+word+"' not found in dictionary, do you want to add it or find it's correction? (add / corr): ")
                    if rsp == "add":
                        add_word_hash_table(Word(word, 1, 1/N) , portuguese_hash_table)
                    elif rsp == "corr":
                        go = True
                        already_cheked = []
                        if word_in_hash_table(word, correction_hash_table):
                            for corr in get_object_in_hash_table(word, correction_hash_table).correction:
                                rsp = input("Is '" + corr.correction +"' the correction? (yes / no): ")
                                already_cheked.append(corr.correction)
                                if rsp == "yes":
                                    if word_in_hash_table(word, correction_hash_table):
                                        get_object_in_hash_table(word, correction_hash_table).add_occ(corr.correction)
                                        get_object_in_hash_table(corr.correction, portuguese_hash_table).add_occ()
                                    else:
                                        add_word_hash_table(Correction(word, corr.word), correction_hash_table)
                                    go = False
                                    break
                                n_corrs += 1
                                if n_corrs == 5:
                                    break
                        c = get_candidates(word, already_cheked)
                        i = 0
                        while(n_corrs < 5 and i < len(c) and go):
                            r = input("Is '" + c[i].word + "' correct? (yes / no): ")
                            if r == "yes":
                                add_word_hash_table(Correction(word, c[i].word), correction_hash_table)
                                go = False
                                break
                            elif r == "no":
                                i += 1
                                n_corrs += 1
                    if(n_corrs == 5):
                        print("CORRECAO-NAO-ENCONTRADA")


start_dict_hash_table(portuguese_hash_table) # start WORDS dictionary
spell_checker()
