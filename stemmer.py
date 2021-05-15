import unittest, re

regexp = re.compile(r"[^aeiouy]*[aeiouy]+[^aeiouy](\w*)")
def get_r1(word):
    # exceptional forms
    if word.startswith('gener') or word.startswith('arsen'):
        return 5
    if word.startswith('commun'):
        return 6

    # normal form
    match = regexp.match(word)
    if match:
        return match.start(1)
    return len(word)

def get_r2(word):
    match = regexp.match(word, get_r1(word))
    if match:
        return match.start(1)
    return len(word)

def ends_with_short_syllable(word):
    if len(word) == 2:
        if re.match(r"^[aeiouy][^aeiouy]$", word):
            return True
    if re.match(r".*[^aeiouy][aeiouy][^aeiouywxY]$", word):
        return True
    return False

def is_short_word(word):
    if ends_with_short_syllable(word):
        if get_r1(word) == len(word):
            return True
    return False

def remove_initial_apostrophe(word):
    if word.startswith("'"):
        return word[1:]
    return word

def capitalize_consonant_ys(word):
    if word.startswith('y'):
        word = 'Y' + word[1:]
    return re.sub(r"([aeiouy])y", '\g<1>Y', word)

def step_0(word):
    if word.endswith("'s'"):
        return word[:-3]
    if word.endswith("'s"):
        return word[:-2]
    if word.endswith("'"):
        return word[:-1]
    return word

def step_1a(word):
    if word.endswith('sses'):
        return word[:-4] + 'ss'
    if word.endswith('ied') or word.endswith('ies'):
        if len(word) > 4:
            return word[:-3] + 'i'
        else:
            return word[:-3] + 'ie'
    if word.endswith('us') or word.endswith('ss'):
        return word
    if word.endswith('s'):
        preceding = word[:-1]
        if re.search(r"[aeiouy].", preceding):
            return preceding
        return word
    return word

def step_1b(word, r1):
    if word.endswith('eedly'):
        if len(word) - 5 >= r1:
            return word[:-3]
        return word
    if word.endswith('eed'):
        if len(word) - 3 >= r1:
            return word[:-1]
        return word

    def ends_with_double(word):
        doubles = ['bb', 'dd', 'ff', 'gg', 'mm', 'nn', 'pp', 'rr', 'tt']
        for double in doubles:
            if word.endswith(double):
                return True
        return False

    def step_1b_helper(word):
        if word.endswith('at') or word.endswith('bl') or word.endswith('iz'):
            return word + 'e'
        if ends_with_double(word):
            return word[:-1]
        if is_short_word(word):
            return word + 'e'
        return word

    suffixes = ['ed', 'edly', 'ing', 'ingly']
    for suffix in suffixes:
        if word.endswith(suffix):
            preceding = word[:-len(suffix)]
            if re.search(r"[aeiouy]", preceding):
                return step_1b_helper(preceding)
            return word

    return word

def step_1c(word):
    if word.endswith('y') or word.endswith('Y'):
        if word[-2] not in 'aeiouy':
            if len(word) > 2:
                return word[:-1] + 'i'
    return word

def step_2(word, r1):
    def step_2_helper(end, repl, prev):
        if word.endswith(end):
            if len(word) - len(end) >= r1:
                if prev == []:
                    return word[:-len(end)] + repl
                for p in prev:
                    if word[:-len(end)].endswith(p):
                        return word[:-len(end)] + repl
            return word
        return None

    triples = [('ization', 'ize', []),
               ('ational', 'ate', []),
               ('fulness', 'ful', []),
               ('ousness', 'ous', []),
               ('iveness', 'ive', []),
               ('tional', 'tion', []),
               ('biliti', 'ble', []),
               ('lessli', 'less', []),
               ('entli', 'ent', []),
               ('ation', 'ate', []),
               ('alism', 'al', []),
               ('aliti', 'al', []),
               ('ousli', 'ous', []),
               ('iviti', 'ive', []),
               ('fulli', 'ful', []),
               ('enci', 'ence', []),
               ('anci', 'ance', []),
               ('abli', 'able', []),
               ('izer', 'ize', []),
               ('ator', 'ate', []),
               ('alli', 'al', []),
               ('bli', 'ble', []),
               ('ogi', 'og', ['l']),
               ('li', '', ['c', 'd', 'e', 'g', 'h', 'k', 'm', 'n', 'r', 't'])]

    for trip in triples:
        attempt = step_2_helper(trip[0], trip[1], trip[2])
        if attempt:
            return attempt

    return word

def step_3(word, r1, r2):
    def step_3_helper(end, repl, r2_necessary):
        if word.endswith(end):
            if len(word) - len(end) >= r1:
                if not r2_necessary:
                    return word[:-len(end)] + repl
                else:
                    if len(word) - len(end) >= r2:
                        return word[:-len(end)] + repl
            return word
        return None

    triples = [('ational', 'ate', False),
               ('tional', 'tion', False),
               ('alize', 'al', False),
               ('icate', 'ic', False),
               ('iciti', 'ic', False),
               ('ative', '', True),
               ('ical', 'ic', False),
               ('ness', '', False),
               ('ful', '', False)]

    for trip in triples:
        attempt = step_3_helper(trip[0], trip[1], trip[2])
        if attempt:
            return attempt

    return word

def step_4(word, r2):
    delete_list = ['al', 'ance', 'ence', 'er', 'ic', 'able', 'ible', 'ant', 'ement', 'ment', 'ent', 'ism', 'ate', 'iti', 'ous', 'ive', 'ize']

    for end in delete_list:
        if word.endswith(end):
            if len(word) - len(end) >= r2:
                return word[:-len(end)]
            return word

    if word.endswith('sion') or word.endswith('tion'):
        if len(word) - 3 >= r2:
            return word[:-3]

    return word

def step_5(word, r1, r2):
    if word.endswith('l'):
        if len(word) - 1 >= r2 and word[-2] == 'l':
            return word[:-1]
        return word

    if word.endswith('e'):
        if len(word) - 1 >= r2:
            return word[:-1]
        if len(word) - 1 >= r1 and not ends_with_short_syllable(word[:-1]):
            return word[:-1]

    return word

def normalize_ys(word):
    return word.replace('Y', 'y')

# Handling exceptional words and their forms
exceptional_forms = {'skis': 'ski',
                    'skies': 'sky',
                    'dying': 'die',
                    'lying': 'lie',
                    'tying': 'tie',
                    'idly': 'idl',
                    'gently': 'gentl',
                    'ugly': 'ugli',
                    'early': 'earli',
                    'only': 'onli',
                    'singly': 'singl',
                    'sky': 'sky',
                    'news': 'news',
                    'howe': 'howe',
                    'atlas': 'atlas',
                    'cosmos': 'cosmos',
                    'bias': 'bias',
                    'andes': 'andes'}

exceptional_early_exit_post_1a = ['inning', 'outing', 'canning', 'herring', 'earring', 'proceed', 'exceed', 'succeed']


class Stemmer:
    max_cache_size = 10000

    def __init__ (self, algorithm, cache_size=None):
        if algorithm not in ['english', 'eng', 'en']:
            raise KeyError("Stemming algorithm '%s' not found" % algorithm)
        if cache_size:
            self.max_cache_size = cache_size

    def stemWord(self, word):
        return Stemmer._stem(word)

    @classmethod
    def _stem(cls, word):
        was_unicode = False

        if isinstance(word, bytes):
            was_unicode = True
            try:
                word = word.encode('ascii')
            except:
                return word

        if len(word) <= 2:
            return word
        word = remove_initial_apostrophe(word)

        # handle some exceptional forms
        if word in exceptional_forms:
            return exceptional_forms[word]

        word = capitalize_consonant_ys(word)
        r1 = get_r1(word)
        r2 = get_r2(word)
        word = step_0(word)
        word = step_1a(word)

        # handle some more exceptional forms
        if word in exceptional_early_exit_post_1a:
            return word

        word = step_1b(word, r1)
        word = step_1c(word)
        word = step_2(word, r1)
        word = step_3(word, r1, r2)
        word = step_4(word, r2)
        word = step_5(word, r1, r2)
        word = normalize_ys(word)

        if was_unicode:
            return word.decode('utf-8')
        return word

stopWords = ['"', "'", '.','a', 'is', 'the', 'of', 'all', 'and', 'to', 'can', 'be', 'as', 'once', 'for', 'at', 'am', 'are', 'has', 'have', 'had', 'up', 'his', 'her', 'in', 'on', 'no', 'we', 'do']

if __name__ == '__main__':
    obj = Stemmer('english')
    msg = " ' Tchirikov’s HORSES horses not empty-headed is a what's its . . . ' "
    list = msg.split()
    for word in list:
        if word not in stopWords:
            answer = obj.stemWord(word)
            print(answer)