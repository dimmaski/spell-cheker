import re
from collections import Counter
import codecs

table_size = 101771

class Word:
    def __init__(self, word, occ, prob):
        self.valid_hash_pos = False
        self.word = word
        self.occ = occ
        self.prob = prob

    def __repr__(self):
        return repr((self.word, self.occ, self.prob))

class Correction:
    def __init__(self, word, correction):
        self.word = word
        self.correction = correction
        self.n_occ = 0

    def add_occ():
        self.n_occ += 1

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
            # get ash code based on string
            add_word_ash_table(line[1], line[0], table)

# init hash tables
portuguese_hash_table = [Word("", 0, 0) for n in range(table_size)] # start word hashtable with prime
correction_hash_table = [Correction("","") for n in range(table_size)]
N = get_N()


def get_word_value(word):
    "Get word value using division method"
    s = len(word) - 1
    value = 0
    for char in word:
        value += ord(char) * (256) ** s
        s -= 1
    return value


def word_in_ash_table(word, table):
    "Check if word is in the hash table"
    code = get_word_value(word) % table_size
    c = 0
    while True:
        code_s = (code + c ** 2) % table_size
        if portuguese_hash_table[code_s].valid_hash_pos == True and (portuguese_hash_table[code_s].word != word):
            c += 1
        elif portuguese_hash_table[code_s].word == word:
            return True
        elif portuguese_hash_table[code_s].valid_hash_pos == False:
            return False

def get_object_in_ash_table(word, table):
    code = get_word_value(word) % table_size
    c = 0
    while True:
        code_s = (code + c ** 2) % table_size
        if portuguese_hash_table[code_s].valid_hash_pos == True and (portuguese_hash_table[code_s].word != word):
            c += 1
        elif portuguese_hash_table[code_s].word == word:
            return portuguese_hash_table[code_s]
        elif portuguese_hash_table[code_s].valid_hash_pos == False:
            return False

def add_word_ash_table(word, occ, table):
    c = 0
    code = get_word_value(word) % table_size
    code_s = code
    while table[code_s].valid_hash_pos == True:  # quadratic probing
        c += 1
        code_s = (code + c ** 2) % table_size
    table[code_s].valid_hash_pos = True
    table[code_s].word = word
    table[code_s].occ = int(occ)
    table[code_s].prob = int(occ) / N

# --------------------------------- Code from https://norvig.com/spell-correct.html

def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyzàáãéâêóòêôúìíîõ'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word):
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))



def candidates(word):
    "Generate possible spelling corrections for word."
    return (known(edits1(word)) or known(edits2(word)))

def get_candidates(word):
    o_c = []
    for cand in candidates(word):
        if word_in_ash_table(cand, portuguese_hash_table):
            o_c.append(get_object_in_ash_table(cand, portuguese_hash_table))
    return sorted(o_c, key=lambda x: x.occ, reverse=True)


def known(words):
    "The subset of `words` that appear in the dictionary of WORDS."
    known_w = []
    for word in words:
        if word_in_ash_table(word, portuguese_hash_table):
            known_w.append(word)
    return known_w

# ---------------------------------------------------------------------


def spell_checker():
    # Main function
    while True:
        usr_text = input("Phrase for analysis: ")
        usr_words = re.findall(r'\w+', usr_text.lower()) # word set for analysis
        for word in usr_words:
            n_corrs = 0
            if not word_in_ash_table(word, portuguese_hash_table):
                rsp = input("Word '"+word+"' not found in dictionary, do you want to add it or find it's correction? (add / corr): ")
                if rsp == "add":
                    add_word_ash_table(word, 1, portuguese_hash_table)
                elif rsp == "corr":
                    if word_in_ash_table(word, correction_hash_table):
                        n_corrs += 1
                        r = input("Is this the correction? (yes / no): ")
                        if r == "yes":
                            print("Correction: " + get_object_in_ash_table(word, correction_hash_table).word)
                            get_object_in_ash_table(word, correction_hash_table).add_occ()
                    else:
                        c = get_candidates(word)
                        # print(c)
                        i = 0
                        while(n_corrs < 5 and i < len(c)):
                            r = input("Is '" + c[i].word + "' correct? (yes / no): ")
                            if r == "yes":
                                # adicionar à correction hash table
                                break
                            elif r == "no":
                                i += 1
                                n_corrs += 1
                        if(n_corrs == 5):
                            print("CORREÇÃO-NÃO-ENCONTRADA")

start_dict_hash_table(portuguese_hash_table) # start WORDS dictionary
spell_checker()
