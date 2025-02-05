from typing import List, Tuple
import numpy as np
from collections import defaultdict
import heapq


class BM25L:
    """
    Implementa el algoritmo BM25L para la recuperación de información.
    """
    def __init__(self, corpus, k1=1.5, b=0.75, delta=0.5):
        self.corpus = corpus
        self.k1 = k1
        self.b = b
        self.delta = delta
        self.avg_doc_len = sum(len(doc.split()) for doc in corpus) / len(corpus)
        self.doc_freqs = []
        self.idf = defaultdict(float)
        self.doc_len = []
        self.corpus_size = len(corpus)
        self._initialize()

    def _initialize(self):
        for document in self.corpus:
            words = document.split()
            self.doc_len.append(len(words))
            freq_dict = defaultdict(int)
            for word in words:
                freq_dict[word] += 1
            self.doc_freqs.append(freq_dict)
            for word in freq_dict:
                self.idf[word] += 1

        for word, freq in self.idf.items():
            self.idf[word] = np.log((self.corpus_size - freq + 0.5) / (freq + 0.5))

    def get_scores(self, query):
        scores = [0] * self.corpus_size
        query_words = query.split()
        q_freqs = defaultdict(int)
        for word in query_words:
            q_freqs[word] += 1

        for i, doc in enumerate(self.corpus):
            for word in query_words:
                if word not in self.doc_freqs[i]:
                    continue
                freq = self.doc_freqs[i][word]
                numerator = self.idf[word] * freq * (self.k1 + 1)
                denominator = freq + self.k1 * (1 - self.b + self.b * self.doc_len[i] / self.avg_doc_len)
                scores[i] += (numerator / denominator) + self.delta

        return scores

class BM25LRetriever:
    """
    Recuperador utilizando el algoritmo BM25L.
    """
    def __init__(self, documents: List[str], k1: float = 1.5, b: float = 0.75, delta: float = 0.5):
        self.documents = documents
        self.bm25 = BM25L(self.documents, k1=k1, b=b, delta=delta)

    def retrieve(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        doc_scores = self.bm25.get_scores(query)
        return heapq.nlargest(top_k, enumerate(doc_scores), key=lambda x: x[1])
