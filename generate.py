from nltk.corpus import cmudict
import random
import sqlite3

from markov import Markov
from utils import reverse_string

class RhymingMarkovGenerator(object):
    def __init__(self, markov_chain, reverse_markov_chain, corpus, lines=10):
        if lines % 2 == 0:
            self.lines = lines
        else:
            raise Exception('Lines must be even')

        self.markov_chain = markov_chain
        self.reverse_markov_chain = reverse_markov_chain
        self.words = corpus.split()

    def generate(self):
        lines = []

        couplets = self.lines / 2
        for _ in range(couplets):
            l1 = self.generate_line(self.markov_chain)
            last_word = self.clean_word(l1.split()[-1])

            while True:
                try:
                    rhymes = self.get_rhymes(last_word)
                    break
                except:
                    l1 = self.generate_line(self.markov_chain)
                    last_word = self.clean_word(l1.split()[-1])
                    rhymes = self.get_rhymes(last_word)
                    break

            random.shuffle(rhymes)

            for rhyme in rhymes:
                try:
                    l2 = self.generate_line(self.reverse_markov_chain, starts_with=rhyme)
                    break
                except:
                    continue

            lines.append(l1)
            lines.append(reverse_string(l2))

        return '\n'.join(lines)

    def generate_line(self, markov_chain, starts_with=None):
        if starts_with:
            seed = self.words.index(starts_with)
        else:
            seed = random.randint(0, len(self.words) - 3)

        w1, w2 = self.words[seed], self.words[seed + 1]
        line = ''

        while len(line.split()) != 8:
            line += (w1 + ' ')
            w1, w2 = w2, random.choice(markov_chain[(w1, w2)])

        return line.strip()

    def get_rhymes(self, word):
        rhymes = []

        word_pronounciations = cmudict.dict()[word]
        for word_pronounciation in word_pronounciations:
            for rhyme, rhyme_pronounciation in cmudict.entries():
                if rhyme_pronounciation[-1] == word_pronounciation[-1]:
                    rhymes.append(rhyme)

        return rhymes

    def clean_word(self, word):
        return word.strip().strip('.,\'!?"()*;:-').lower()

class EmailFilter(object):
    filters = [':','<','>','@','_',';','[',']','Case No.','Doc No.','BENGHAZI COMM.','REDACTIONS']

    def __init__(self, email):
        self.email = email

    def filter(self):
        filtered = []

        lines = self.email.split('\n')
        for line in lines:
            if any(filter in line for filter in self.filters):
                continue
            else:
                filtered.append(line)

        return '\n'.join(filtered)

if __name__ == '__main__':
    conn = sqlite3.connect('data/database.sqlite')
    c = conn.cursor()
    c.execute("SELECT ExtractedBodyText FROM Emails WHERE ExtractedBodyText != ''")

    emails = [EmailFilter(email[0]).filter() for email in c.fetchall()]
    corpus = '\n'.join(emails)

    markov_chain = Markov(corpus).generate_chain()
    reverse_markov_chain = Markov(corpus, reverse=True).generate_chain()

    print RhymingMarkovGenerator(markov_chain, reverse_markov_chain, corpus).generate()
