# Pipeline 1: ανακατασκευή κειμένου με βάση τη βιβλιοθήκη TextBlob
# Αυτόματη ανακατασκευή κειμένου χρησιμοποιώντας το TextBlob library ως στατιστική προσέγγιση NLP

# Το pipeline επιδεικνύει: POS tagging, Noun phrase extraction, Basic sentence transformation, Spelling correction, Sentence simplification
# όχι custom κανόνες ή χειροκίνητη παρέμβαση - αυτόματο "μοντέλο" 

from textblob import TextBlob
from typing import List, Tuple
import re
import warnings

warnings.filterwarnings('ignore')

def pipeline_textblob_1_main(text):
    #main συνάρτηση για το pipeline 1 - καλεί τις υπόλοιπες, εκτυπώνει και επιστρέφει το νέο κείμενο στη main
    
    try:
        og_text = text
        reconstructed_txt = reconstruct_text_with_textblob(text)

        print("\n" + "="*82)
        print("                  PIPELINE 1: TextBlob-based Text Reconstruction                  ")
        print("\n" + "="* 82)
        print("                                  ORIGINAL TEXT:                                  ")
        print("\n" + "-"* 82)
        print(og_text)
        print("\n" + "="* 82)
        print("                        RECONSTRUCTED WITH TEXTBLOB TEXT:                         ")
        print("\n" + "-"* 82)
        print(reconstructed_txt)
        
    except Exception as e:
        print(f"\n ======= Unexpected error: {e} =======")
        import traceback
        traceback.print_exc()
        raise 

    return reconstructed_txt

# η συνάρτηση που είναι υπεύθυνη για το reconstruction με τη χρήση textblob
def reconstruct_text_with_textblob(text:str)->str:
    # TextBlob object
    blob = TextBlob(text)

    # επεξεργασία κάθε πρότασης
    reconstructed_sentences = []

    for sentence in blob.sentences: # corrections and reconstruction
        reconstructed = _reconstruct_sentence(sentence)
        clean_sent_str = str(reconstructed).strip()
        if reconstructed: reconstructed_sentences.append(reconstructed)
    # ένωσε τις προτάσεις
    return " ".join(reconstructed_sentences)


# Ανακατασκευή της πρότασης με τη χρήση του TextBlob    
def _reconstruct_sentence(sentence: TextBlob) ->str:    
    # Βήματα:
    # 1. Διόρθωση ορθογραφίας (TextBlob το κάνει)
    # 2. Εξαγωγή POS tags και noun phrases (TextBlob το κάνει αυτόματα)
    # 3. Αβαδιοργάνωση με βάση τα γλωσσικά χαρακτηριστικά
    # 4. Καθαρισμός και μορφοποίηση αποτελέσματος
    # Δέχεται αντικείμενο TextBlob -> επιστρέφει string

    # Βήμα 1: Διόρθωση ορθογραφίας 
    corrected = sentence.correct()
    
    # Β΄ήμα 2: εξαγωγή ετικετών
    words = corrected.words # tokenization
    tags = corrected.tags  # POS tags από TextBlob
    noun_phrases = corrected.noun_phrases  # Noun phrases από TextBlob
    
    # Βήμα 3: Αναδιοργάνωση με POS patterns από TextBlob POS tags
    reconstructed = _reorganize_by_pos(words, tags, noun_phrases)
    
    # Βήμα 4: καθάρισμα
    reconstructed = _clean_text(reconstructed)
    
    # Πρώτο κεφαλαίο
    if reconstructed:
        reconstructed = reconstructed[0].upper() + reconstructed[1:]
    
    return reconstructed

# Αναδιοργάνωση με βάση τις ετικέτες από το TextBlob
def _reorganize_by_pos(words: List[str], tags: List[Tuple[str, str]], noun_phrases: List[str]) -> str:
    # Αυτόματη προσθήκη POS tags από TextBlob:
    # - Υποκείμενο Subject (nouns/pronouns: NN*, PRP*)
    # - Ρήμα Verbs (VB*)
    # - Αντικείμενο - Objects and complements
    # - Modifiers (adjectives/adverbs: JJ*, RB*)
    # Οργανώνει αυτόματα σε SVO με τα POS tags του TextBlob χωρίς custom κανόνες
    
    # Διαχωρισμός ανά κατηγορίες (αυτόματα από το textblob)
    subjects = []
    verbs = []
    objects = []
    modifiers = []
    others = []
    
    for word, tag in tags:
        if tag.startswith('NN') or tag.startswith('PRP'):  # Nouns and pronouns
            subjects.append(word)
        elif tag.startswith('VB'):  # Verbs
            verbs.append(word)
        elif tag.startswith('JJ') or tag.startswith('RB'):  # Adjectives and adverbs
            modifiers.append(word)
        elif tag in ['DT', 'IN', 'TO', 'CC']:  # Determiners, prepositions, conjunctions
            others.append(word)
        else:
            objects.append(word)
    
    # Αυτόματη κατασκευή πρότασης
    result_parts = []
    
    # Πρώτα το υποκείμενο
    if subjects: result_parts.extend(subjects)  # όριο για αποφυγή πλεονασμού
    
    # μετά το ρήμα
    if verbs: result_parts.extend(verbs)
    
    # και μετά το αντικείμενο
    if objects: result_parts.extend(objects)
    
    if modifiers: result_parts.extend(modifiers)
    
    # Προσθήκη υπόλοιπων λέξεων στη πρόταση
    if others: result_parts.extend(others)
    
    # Αν η ανακατασκευή δεν ήταν καλή, επιστρέφει το αρχικό
    if not result_parts: return " ".join(words)
    
    return " ".join(result_parts)

# Καθαρισμός και κανονικοποίηση κειμένου
def _clean_text(text: str) -> str:
    # Αφαίρεση κενού διαστήματος
    # Διόρθωση της απόστασης με το σημείο στίξης
    # Αφαίρεση διπλού σημείου στίξης
    # Διασφάλιση ότι η πρόταση τελειώνει σωστά
        
    # αφαίρεση κενού
    text = re.sub(r'\s+', ' ', text)
    
    # φτιάξε το punctuation
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    text = re.sub(r'([.,!?;:])\s*', r'\1 ', text)
    
    # αφαίρεση διπλότυπου
    text = re.sub(r'([.,!?;:])\1+', r'\1', text)
    
    # Να είμαστε σίγουροι ότι η πρόταση τελειώνει σωστά
    text = text.strip()
    if text and text[-1] not in '.!?':
        text += '.'
    
    return text
