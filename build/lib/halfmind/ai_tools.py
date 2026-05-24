import os
import json
import hashlib
from pathlib import Path
from collections import Counter


class AITools:
    """Tools for AI/ML operations and text processing"""
    
    def __init__(self):
        self.models = {}
        self.cache = {}
    
    def tokenize_text(self, text, method='simple'):
        """Tokenizes text using various methods"""
        if method == 'simple':
            return text.split()
        elif method == 'word':
            import re
            return re.findall(r'\b\w+\b', text.lower())
        elif method == 'character':
            return list(text)
        elif method == 'sentence':
            import re
            return re.split(r'[.!?]+', text)
        else:
            return text.split()
    
    def calculate_tf(self, document):
        """Calculates term frequency for a document"""
        tokens = self.tokenize_text(document.lower())
        total = len(tokens)
        tf = Counter(tokens)
        return {term: count / total for term, count in tf.items()}
    
    def calculate_idf(self, documents):
        """Calculates inverse document frequency"""
        import math
        n = len(documents)
        doc_freq = Counter()
        for doc in documents:
            unique_terms = set(self.tokenize_text(doc.lower()))
            for term in unique_terms:
                doc_freq[term] += 1
        return {term: math.log(n / (freq + 1)) for term, freq in doc_freq.items()}
    
    def calculate_tfidf(self, document, documents):
        """Calculates TF-IDF scores"""
        tf = self.calculate_tf(document)
        idf = self.calculate_idf(documents)
        return {term: tf_val * idf.get(term, 0) for term, tf_val in tf.items()}
    
    def cosine_similarity(self, vec1, vec2):
        """Calculates cosine similarity between two vectors"""
        all_keys = set(vec1.keys()) | set(vec2.keys())
        dot_product = sum(vec1.get(k, 0) * vec2.get(k, 0) for k in all_keys)
        mag1 = sum(v**2 for v in vec1.values()) ** 0.5
        mag2 = sum(v**2 for v in vec2.values()) ** 0.5
        if mag1 == 0 or mag2 == 0:
            return 0.0
        return dot_product / (mag1 * mag2)
    
    def find_similar_documents(self, query, documents, top_k=5):
        """Finds most similar documents to a query using TF-IDF"""
        query_vec = self.calculate_tfidf(query, documents)
        similarities = []
        for i, doc in enumerate(documents):
            doc_vec = self.calculate_tfidf(doc, documents)
            sim = self.cosine_similarity(query_vec, doc_vec)
            similarities.append({'index': i, 'document': doc, 'similarity': sim})
        return sorted(similarities, key=lambda x: x['similarity'], reverse=True)[:top_k]
    
    def extract_keywords(self, text, top_n=10):
        """Extracts keywords from text using TF scores"""
        tf = self.calculate_tf(text)
        sorted_terms = sorted(tf.items(), key=lambda x: x[1], reverse=True)
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                    'should', 'may', 'might', 'can', 'shall', 'to', 'of', 'in', 'for',
                    'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during',
                    'before', 'after', 'above', 'below', 'between', 'under', 'again',
                    'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
                    'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other',
                    'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
                    'than', 'too', 'very', 's', 't', 'just', 'don', 'now', 'and', 'but',
                    'or', 'if', 'it', 'its', 'this', 'that', 'these', 'those', 'i', 'me',
                    'my', 'we', 'our', 'you', 'your', 'he', 'him', 'his', 'she', 'her',
                    'they', 'them', 'their', 'what', 'which', 'who', 'whom'}
        keywords = [(term, score) for term, score in sorted_terms if term not in stopwords and len(term) > 2]
        return keywords[:top_n]
    
    def summarize_text(self, text, num_sentences=3):
        """Summarizes text by extracting key sentences"""
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        if len(sentences) <= num_sentences:
            return text
        sentence_scores = {}
        words = self.tokenize_text(text.lower())
        word_freq = Counter(words)
        for sentence in sentences:
            score = sum(word_freq.get(word.lower(), 0) for word in sentence.split())
            sentence_scores[sentence] = score / len(sentence.split())
        top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:num_sentences]
        return ' '.join([s[0] for s in top_sentences])
    
    def text_classification(self, text, categories):
        """Classifies text into categories based on keyword matching"""
        text_lower = text.lower()
        scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword.lower() in text_lower)
            scores[category] = score
        if max(scores.values()) == 0:
            return {'category': 'unknown', 'confidence': 0}
        best = max(scores.items(), key=lambda x: x[1])
        total = sum(scores.values())
        return {
            'category': best[0],
            'confidence': best[1] / total if total > 0 else 0,
            'scores': scores
        }
    
    def sentiment_analysis(self, text):
        """Performs basic sentiment analysis"""
        positive_words = {'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
                         'love', 'like', 'enjoy', 'happy', 'joy', 'pleased', 'satisfied',
                         'best', 'awesome', 'brilliant', 'perfect', 'beautiful', 'nice'}
        negative_words = {'bad', 'terrible', 'awful', 'horrible', 'poor', 'worst', 'hate',
                         'dislike', 'angry', 'sad', 'disappointed', 'frustrating', 'annoying',
                         'ugly', 'broken', 'failed', 'wrong', 'problem', 'issue'}
        words = set(self.tokenize_text(text.lower()))
        pos_count = len(words & positive_words)
        neg_count = len(words & negative_words)
        total = pos_count + neg_count
        if total == 0:
            return {'sentiment': 'neutral', 'score': 0.5}
        score = pos_count / total
        if score > 0.6:
            sentiment = 'positive'
        elif score < 0.4:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        return {
            'sentiment': sentiment,
            'score': score,
            'positive_count': pos_count,
            'negative_count': neg_count
        }
    
    def detect_language(self, text):
        """Detects language based on character patterns"""
        from collections import Counter
        char_freq = Counter(text.lower())
        total = sum(char_freq.values())
        ascii_letters = sum(char_freq.get(chr(i), 0) for i in range(97, 123))
        ascii_ratio = ascii_letters / total if total > 0 else 0
        if ascii_ratio > 0.8:
            return {'language': 'english', 'confidence': ascii_ratio}
        elif ascii_ratio > 0.5:
            return {'language': 'mixed', 'confidence': ascii_ratio}
        else:
            return {'language': 'non-english', 'confidence': 1 - ascii_ratio}
    
    def text_to_vector(self, text, vocab=None):
        """Converts text to a bag-of-words vector"""
        tokens = self.tokenize_text(text.lower())
        if vocab is None:
            vocab = list(set(tokens))
        vector = {word: 0 for word in vocab}
        for token in tokens:
            if token in vector:
                vector[token] += 1
        return vector
    
    def generate_ngrams(self, text, n=2):
        """Generates n-grams from text"""
        tokens = self.tokenize_text(text.lower())
        ngrams = []
        for i in range(len(tokens) - n + 1):
            ngrams.append(tuple(tokens[i:i+n]))
        return ngrams
    
    def calculate_bleu(self, reference, hypothesis, max_n=4):
        """Calculates BLEU score between reference and hypothesis"""
        import math
        ref_tokens = self.tokenize_text(reference.lower())
        hyp_tokens = self.tokenize_text(hypothesis.lower())
        if not hyp_tokens:
            return 0.0
        precisions = []
        for n in range(1, max_n + 1):
            ref_ngrams = Counter(self.generate_ngrams(reference.lower(), n))
            hyp_ngrams = Counter(self.generate_ngrams(hypothesis.lower(), n))
            matches = sum(min(count, ref_ngrams.get(ngram, 0)) for ngram, count in hyp_ngrams.items())
            total = sum(hyp_ngrams.values())
            if total == 0:
                precisions.append(0)
            else:
                precisions.append(matches / total)
        if any(p == 0 for p in precisions):
            return 0.0
        log_avg = sum(math.log(p) for p in precisions) / len(precisions)
        bp = min(1, len(hyp_tokens) / len(ref_tokens)) if ref_tokens else 0
        return bp * math.exp(log_avg)
    
    def generate_text_hash(self, text):
        """Generates a hash for text deduplication"""
        normalized = ' '.join(self.tokenize_text(text.lower()))
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def detect_duplicates(self, texts, threshold=0.9):
        """Detects duplicate or near-duplicate texts"""
        duplicates = []
        hashes = {}
        for i, text in enumerate(texts):
            h = self.generate_text_hash(text)
            if h in hashes:
                duplicates.append({
                    'index1': hashes[h],
                    'index2': i,
                    'similarity': 1.0
                })
            else:
                hashes[h] = i
        return duplicates
    
    def text_clustering(self, texts, num_clusters=3):
        """Clusters texts using simple k-means"""
        vectors = [self.text_to_vector(text) for text in texts]
        all_terms = set()
        for vec in vectors:
            all_terms.update(vec.keys())
        import random
        centroids = random.sample(vectors, min(num_clusters, len(vectors)))
        for _ in range(10):
            clusters = [[] for _ in range(len(centroids))]
            for i, vec in enumerate(vectors):
                sims = [self.cosine_similarity(vec, c) for c in centroids]
                best = sims.index(max(sims))
                clusters[best].append(i)
            for j in range(len(centroids)):
                if clusters[j]:
                    new_centroid = {}
                    for term in all_terms:
                        vals = [vectors[i].get(term, 0) for i in clusters[j]]
                        new_centroid[term] = sum(vals) / len(vals)
                    centroids[j] = new_centroid
        return {
            'clusters': clusters,
            'centroids': centroids,
            'sizes': [len(c) for c in clusters]
        }
    
    def extract_entities(self, text):
        """Extracts named entities using pattern matching"""
        import re
        entities = {
            'emails': re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text),
            'urls': re.findall(r'https?://[^\s]+', text),
            'phones': re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text),
            'dates': re.findall(r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b', text),
            'times': re.findall(r'\b\d{1,2}:\d{2}(?::\d{2})?\s?(?:AM|PM|am|pm)?\b', text),
            'numbers': re.findall(r'\b\d+\.?\d*\b', text),
            'uppercase_words': re.findall(r'\b[A-Z]{2,}\b', text)
        }
        return entities
    
    def spell_check(self, word, dictionary=None):
        """Basic spell checking using edit distance"""
        if dictionary is None:
            dictionary = {'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
                         'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at'}
        if word.lower() in dictionary:
            return {'correct': True, 'suggestions': []}
        suggestions = []
        for dict_word in dictionary:
            if abs(len(word) - len(dict_word)) <= 2:
                if self._edit_distance(word.lower(), dict_word) <= 2:
                    suggestions.append(dict_word)
        return {'correct': False, 'suggestions': suggestions[:5]}
    
    def _edit_distance(self, s1, s2):
        """Calculates edit distance between two strings"""
        if len(s1) < len(s2):
            return self._edit_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        prev_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            curr_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = prev_row[j + 1] + 1
                deletions = curr_row[j] + 1
                substitutions = prev_row[j] + (c1 != c2)
                curr_row.append(min(insertions, deletions, substitutions))
            prev_row = curr_row
        return prev_row[-1]
    
    def generate_embeddings(self, texts):
        """Generates simple embeddings using TF-IDF"""
        idf = self.calculate_idf(texts)
        embeddings = []
        for text in texts:
            tf = self.calculate_tf(text)
            embedding = {term: tf.get(term, 0) * idf.get(term, 0) for term in idf}
            embeddings.append(embedding)
        return embeddings
    
    def find_anomalies(self, texts, threshold=2.0):
        """Finds anomalous texts based on length"""
        lengths = [len(text) for text in texts]
        mean_len = sum(lengths) / len(lengths)
        std_len = (sum((l - mean_len)**2 for l in lengths) / len(lengths)) ** 0.5
        anomalies = []
        for i, length in enumerate(lengths):
            if std_len > 0:
                z_score = abs(length - mean_len) / std_len
                if z_score > threshold:
                    anomalies.append({
                        'index': i,
                        'length': length,
                        'z_score': z_score,
                        'text_preview': texts[i][:100]
                    })
        return anomalies
    
    def extract_patterns(self, text, pattern_type='all'):
        """Extracts various patterns from text"""
        import re
        patterns = {}
        if pattern_type in ['all', 'email']:
            patterns['emails'] = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        if pattern_type in ['all', 'url']:
            patterns['urls'] = re.findall(r'https?://[^\s]+', text)
        if pattern_type in ['all', 'hashtag']:
            patterns['hashtags'] = re.findall(r'#[a-zA-Z0-9_]+', text)
        if pattern_type in ['all', 'mention']:
            patterns['mentions'] = re.findall(r'@[a-zA-Z0-9_]+', text)
        if pattern_type in ['all', 'ip']:
            patterns['ips'] = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text)
        if pattern_type in ['all', 'hashtag']:
            patterns['hashtags'] = re.findall(r'#[a-zA-Z0-9_]+', text)
        return patterns
    
    def batch_process(self, items, operation):
        """Processes items in batch"""
        results = []
        for item in items:
            try:
                result = operation(item)
                results.append({'success': True, 'result': result})
            except Exception as e:
                results.append({'success': False, 'error': str(e)})
        return results