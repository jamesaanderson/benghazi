from collections import defaultdict

class Markov(object):
    def __init__(self, corpus, reverse=False):
        if reverse:
            corpus = ' '.join(reversed(corpus.split()))

        self.words = corpus.split()

    def yield_trigrams(self):
        if len(self.words) < 3:
          return

        for i in range(len(self.words) - 2):
            yield (self.words[i], self.words[i + 1], self.words[i + 2])

    def generate_chain(self):
        chain = defaultdict(list)

        for w1, w2, w3 in self.yield_trigrams():
            chain[(w1, w2)].append(w3)

        return chain
