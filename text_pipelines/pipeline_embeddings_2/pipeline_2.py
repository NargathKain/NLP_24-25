# Pipeline 2: ανακατασκευή κειμένου με βάση word embeddings
# Αυτόματη ανακατασκευή κειμένου χρησιμοποιώντας word embeddings ως σημασιολογική προσέγγιση NLP

# Το pipeline επιδεικνύει Semantic similarity, Word embeddings (Word2Vec), Content word replacement, POS tagging
# όχι custom κανόνες ή χειροκίνητη παρέμβαση - αυτόματο "μοντέλο" με pretrained embeddings

import nltk
import numpy as np
from typing import List, Tuple, Optional
import gensim.downloader as api
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
import random
import warnings

warnings.filterwarnings('ignore')

# # Ensure NLTK data is available
# try:
#     nltk.data.find('tokenizers/punkt')
# except LookupError:
#     nltk.download('punkt', quiet=True)

# try:
#     nltk.data.find('taggers/averaged_perceptron_tagger') 
# except LookupError:
#     nltk.download('averaged_perceptron_tagger', quiet=True)


def pipeline_embeddings_2_main(text):
    
    try:
        og_text = text
        reconstructed_txt = reconstruct_text_with_embeddings(text)
        
        print("\n" + "="*82)
        print("              PIPELINE 2: Embeddings-based Text Reconstruction                  ")
        print("\n" + "="* 82)
        print("                                  ORIGINAL TEXT:                                  ")
        print("\n" + "-"* 82)
        print(og_text)
        print("\n" + "="* 82)
        print("                     RECONSTRUCTED WITH EMBEDDINGS TEXT:                         ")
        print("\n" + "-"* 82)
        print(reconstructed_txt)
        
    except Exception as e:
        print(f"\n ======= Unexpected error: {e} =======")
        import traceback
        traceback.print_exc()
        raise
    
    return reconstructed_txt


# η συνάρτηση που είναι υπεύθυνη για το reconstruction με τη χρήση embeddings
def reconstruct_text_with_embeddings(text: str, model_name: str = 'glove-wiki-gigaword-100', similarity_threshold: float = 0.65) -> str:
    # Ανακατασκευή κειμένου με word embeddings.
    # Αντικαθιστά content words με σημασιολογικά παρόμοιες λέξεις.

    # Φόρτωση pretrained embeddings
    print(f"Φόρτωση pretrained embeddings: {model_name}...")
    model = api.load(model_name)
    print("✓ Embeddings ")
    
    # Διαχωρισμός σε προτάσεις
    sentences = sent_tokenize(text)
    
    reconstructed_sentences = []
    
    for sentence in sentences:
        # Ανακατασκευή κάθε πρότασης
        reconstructed = _reconstruct_sentence(sentence, model, similarity_threshold)
        if reconstructed:
            reconstructed_sentences.append(reconstructed)
    
    # Ένωσε τις προτάσεις
    return " ".join(reconstructed_sentences)


# Ανακατασκευή της πρότασης με word embeddings
def _reconstruct_sentence(sentence: str, model, similarity_threshold: float) -> str:
    # Βήματα:
    # 1. Tokenization
    # 2. POS tagging
    # 3. Εύρεση semantic neighbors για content words
    # 4. Αντικατάσταση με similarity threshold
    # 5. Ανασύνθεση πρότασης

    # Βήμα 1: Tokenization
    tokens = word_tokenize(sentence)
    
    # Βήμα 2: POS tagging
    pos_tags = pos_tag(tokens)
    
    # Content word POS tags
    content_pos = {'NN', 'NNS', 'NNP', 'NNPS',  # Nouns
                   'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ',  # Verbs
                   'JJ', 'JJR', 'JJS',  # Adjectives
                   'RB', 'RBR', 'RBS'}  # Adverbs
    
    # Βήμα 3 & 4: Αντικατάσταση content words με semantic neighbors
    reconstructed_tokens = []
    
    for token, pos in pos_tags:
        # Αν είναι content word και όχι σημείο στίξης
        if pos in content_pos and token.isalpha():
            similar_word = _get_similar_word(token, model, similarity_threshold)
            
            if similar_word:
                reconstructed_tokens.append(similar_word)
            else:
                reconstructed_tokens.append(token)
        else:
            reconstructed_tokens.append(token)
    
    # Βήμα 5: Ανασύνθεση της πρότασης
    reconstructed = _reassemble_sentence(reconstructed_tokens)
    
    return reconstructed


# Εύρεση σημασιολογικά παρόμοιας λέξης από embeddings
def _get_similar_word(word: str, model, similarity_threshold: float, top_n: int = 10) -> Optional[str]:
    # Βρίσκει μια σημασιολογικά παρόμοια λέξη από τα embeddings.

    word_lower = word.lower()
    
    # Αν η λέξη δεν υπάρχει στο vocabulary, επιστρέφουμε None
    if word_lower not in model:
        return None
    
    try:
        # Παίρνουμε τις πιο παρόμοιες λέξεις
        similar_words = model.most_similar(word_lower, topn=top_n)
        
        # Φιλτράρουμε με βάση το similarity threshold
        candidates = [
            (w, sim) for w, sim in similar_words 
            if sim >= similarity_threshold and w.lower() != word_lower
        ]
        
        if not candidates:
            return None
        
        # Επιλέγουμε τυχαία από τους υποψηφίους για ποικιλία
        selected_word, _ = random.choice(candidates[:min(5, len(candidates))])
        
        # Διατηρούμε την αρχική κεφαλαιοποίηση
        if word[0].isupper():
            selected_word = selected_word.capitalize()
        
        return selected_word
        
    except KeyError:
        return None


# Ανασύνθεση της πρότασης από tokens
def _reassemble_sentence(tokens: List[str]) -> str:
    # Ανασυνθέτει την πρόταση από tokens με σωστή διαχείριση κενών.
    # Βασικός χειρισμός κενών (δεν βάζουμε κενά πριν από σημεία στίξης).

    reconstructed = ""
    
    for i, token in enumerate(tokens):
        if i == 0:
            reconstructed = token
        elif token in {'.', ',', '!', '?', ';', ':', ')', ']', '}', "'s", "n't"}:
            reconstructed += token
        elif tokens[i-1] in {'(', '[', '{'}:
            reconstructed += token
        else:
            reconstructed += " " + token
    
    # Πρώτο κεφαλαίο
    if reconstructed:
        reconstructed = reconstructed[0].upper() + reconstructed[1:]
    
    # Να είμαστε σίγουροι ότι η πρόταση τελειώνει σωστά
    if reconstructed and reconstructed[-1] not in '.!?':
        reconstructed += '.'
    
    return reconstructed