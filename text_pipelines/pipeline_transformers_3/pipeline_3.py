# Pipeline 3: Transformer-based text reconstruction with text-to-text generation
# Το pipeline χρησιμοποιεί encoder-decoder transformer για επανεγγραφή κειμένου με βάση τα συμφραζόμενα

from transformers import pipeline as hf_pipeline
#from typing import Optional
import warnings

warnings.filterwarnings('ignore')


def pipeline_transformer_3_main(text: str) -> str:
    # Χρησιμοποιεί ένα pretrained encoder-decoder transformer model για ανακατασκεύη κειμένου με text-to-text generation.
    # Το μοντέλο επεξεργάζεται την είσοδο με attention mechanisms για να παράγει σαφή και συνεκτική έξοδο  
    
    try:
        original_text = text
        reconstructed_text = reconstruct_with_transformer(text)
        
        print("\n" + "="*82)
        print("            PIPELINE 3: Transformer-based Text Reconstruction               ")
        print("\n" + "="*82)
        print("                              ORIGINAL TEXT:                                ")
        print("\n" + "-"*82)
        print(original_text)
        print("\n" + "="*82)
        print("                    RECONSTRUCTED WITH TRANSFORMER TEXT:                    ")
        print("\n" + "-"*82)
        print(reconstructed_text)
        print("\n" + "="*82)
        
        return reconstructed_text
    # Exception: αν αποτύχει η ανακατασκεύη
    except Exception as e:
        print(f"\n ======= Unexpected error : {e} =======")
        import traceback
        traceback.print_exc()
        raise

# Ανακατασκευή κειμένου με βάση pretrained transformer μέσω text-to-text
def reconstruct_with_transformer(text: str) -> str:    
    # Χρήση encoder-decoder transformer:
    # 1. Encoder: επεξεργάζεται το κείμενο εισόδου και δημιουργεί αναπαραστάσεις με βάση τα συμφραζόμενα 
    # 2. Decoder: δημιουργεί βελτιωμένο κείμενο token-by-token, φροντίζοντας για την έξοδο του encoder μέσω cross-attention
    # 3. Το generation αξιοποιεί την κατανόηση του μοντέλου σε grammar, coherence, semantic clarity
    
    # Δεν πρόκειται για εξαγωγή ή ανάλυση embeddings αλλά για χρήση των δημιουργικών δυνατοτήτων του transformer για την ανακατασκευή κειμένου
            
    # Default: grammar-focused T5 model
    # These models are trained on text-to-text tasks: (incorrect text) -> (corrected text)
    # model_name = "pszemraj/flan-t5-large-grammar-synthesis"
    # model_name = "t5-base" # μικρό, γρήγορο
    # χρήση με input_text = f"grammar: {text}"

    model_name = "google/flan-t5-base" # μικρότερο, πιο γρήγορο
    # model_name = "prithvida/grammar_error_correcter_v1" # συγκεκριμένο για γραμματικά errors 
    # επιβεβαίωση για το ποιό μοντέλο χρησιμοποιείται για λόγους debug
    print(f"[Pipeline 3] Loading model: {model_name}") 
    
    # Initialize text2text-generation pipeline
    # This wraps a T5/BART-style encoder-decoder model
    reconstructor = hf_pipeline(
        "text2text-generation",
        model=model_name,
        device=-1,  # CPU; αλλαή σε 0 για GPU
        max_length=512
    )
    
    # Προετοιμασία input για το model
    # Κάποια μοντέλα χρειάζονται ακριβής οδηγίες
    if "t5" in model_name.lower():
        input_text = f"Rewrite this text to fix all grammar errors and make it clear and formal: {text}" 
    else:
        input_text = text
    
    # Generate reconstructed text
    # The model uses its encoder-decoder architecture to:
    # - Encode: Transform input into contextualized representations
    # - Decode: Generate improved output conditioned on those representations
    result = reconstructor(
        input_text,
        max_length=512,
        min_length=30,
        do_sample=True,  # Deterministic generation (greedy decoding)
        temperature=0.8, # Controls randomness (0.7-0.9 good)
        top_p=0.95,     # Nucleus sampling
        num_beams=1,      # Beam search for better quality
        repetition_penalty=1.2 # prevents repetition
    )
    
    # Εξαγωγή generated text από την έξοδο του μοντέλου
    reconstructed = result[0]['generated_text']
    
    # post-processing για το format του κειμένου
    reconstructed = _post_process_output(reconstructed)
    
    return reconstructed

# Ελαφρύ post-processing για την έξοδο
def _post_process_output(text: str) -> str:
    # Αυτή η συνάρτηση εκτελεί μόνο formatting. Όλες οι σημασιολογικές και γραμματικές βελτιώσεις 
    # προέρχονται από το transformer generation και όχι από διορθώσεις σε κανόνες
    
    import re
    
    # Cleanup
    text = text.strip()
    
    # Πρώτο γράμμα κεφαλαίο
    if text: text = text[0].upper() + text[1:]
    
    # Κενό πριν και μετά τη τελεία
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)  # Αφαίρεση κενού
    text = re.sub(r'([.,!?;:])\s*', r'\1 ', text)  # Προσθήκη 
    
    # Αφαίρεση διπλότυπων σημείων στίξης
    text = re.sub(r'([.,!?;:])\1+', r'\1', text)
    
    # Πρόταση τελειώνει με τη σωστή στίξη
    if text and text[-1] not in '.!?': text += '.'
    
    # Τελικός καθαρισμός πολλαπλών χώρων
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


# # Alternative: Χρήση paraphrasing μοντέλου αντί για γραμματική διόρθωση
# def reconstruct_with_paraphrasing(text: str) -> str:
#     # Μπορεί να χρησιμοποιηθεί για έμφαση σε σημασιολογική διόρθωση αντί για καθαρή γραμματική διόρθωση
#     # Δέχεται text (str) -> επιστρέφει Paraphrased/reconstructed text

#     paraphraser = hf_pipeline(
#         "text2text-generation",
#         model="Vamsi/T5_Paraphrase_Paws",
#         device=-1
#     )
    
#     input_text = f"paraphrase: {text}"
    
#     result = paraphraser(
#         input_text,
#         max_length=512,
#         num_beams=4,
#         early_stopping=True
#     )
    
#     reconstructed = result[0]['generated_text']
#     return _post_process_output(reconstructed)