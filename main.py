# NLP 2025 - ενιαία main για το πρώτο ερώτημα
import os
import sys
# import json

# ============================== File imports ==============================
# paradoteo 1a
from sentence_pipeline.preprocessing_1.preprocessing import preprocess_pipeline
from sentence_pipeline.syntactic_analysis_2.syntactic_analysis import syntactic_analysis_pipeline
from sentence_pipeline.grammatical_correction_3.grammatical_correction4 import grammatical_correction_pipeline
# paradoteo 1b
from text_pipelines.pipeline_textblob_1.pipeline_1 import pipeline_textblob_1_main
from text_pipelines.pipeline_embeddings_2.pipeline_2 import pipeline_embeddings_2_main
from text_pipelines.pipeline_transformers_3.pipeline_3 import pipeline_transformer_3_main

# ============================== DIRECTORY STRUCTURE ==============================
BASE_DIR = "data"
RAW_DIR = os.path.join(BASE_DIR, "raw")

# προτάσεις - παραδοτέο 1α
SENTENCES_DIR = os.path.join(RAW_DIR, "sentences")
SENTENCE1_FILE = os.path.join(SENTENCES_DIR, "sentence1.txt")
SENTENCE2_FILE = os.path.join(SENTENCES_DIR, "sentence2.txt")

# κείμενο - παραδοτέο 1β
TEXTS_DIR = os.path.join(RAW_DIR, "texts")
TEXT1_FILE = os.path.join(TEXTS_DIR, "text1.txt")
TEXT2_FILE = os.path.join(TEXTS_DIR, "text2.txt")

# Results directory
RESULTS_DIR = os.path.join(BASE_DIR, "results")
SENTENCE_RESULTS_DIR = os.path.join(RESULTS_DIR, "sentence_pipeline")
TEXT_RESULTS_DIR = os.path.join(RESULTS_DIR, "text_pipelines")

# ============================== FILE I/O FUNCTIONS ==============================
# load from file
def load_file(filepath): 
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        sentence = f.read().strip()
    return sentence
    
# save to file 
def save_result(result_text, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(str(result_text))

# # save json to file - save results σε ολόκληρη μορφή αντί για κείμενο μόνο (tokens, pos_tags, κτλπ.)
# def save_json(data, output_path): 
#     os.makedirs(os.path.dirname(output_path), exist_ok=True)
#     with open(output_path, 'w', encoding='utf-8') as f:
#         json.dump(data, f, indent=2, ensure_ascii=False)

# create dir if not exist
def ensure_directories(): 
    directories = [
        RAW_DIR,
        SENTENCES_DIR,
        TEXTS_DIR,
        SENTENCE_RESULTS_DIR,
        os.path.join(TEXT_RESULTS_DIR, "pipeline_1_textblob"),
        os.path.join(TEXT_RESULTS_DIR, "pipeline_2_embeddings"),
        os.path.join(TEXT_RESULTS_DIR, "pipeline_3_transformer"),
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


# ============================== SENTENCE PIPELINE (1A) ==============================

def run_sentence_pipeline():
    print("\n" + "█" * 82)
    print("                    SENTENCE PIPELINE - DELIVERABLE 1A                         ")
    print("  1 (Preprocessing)  |  2 (Syntactic Analysis)  |  3 (Grammatical Correction)  ")
    print("█" * 82 + "\n")

    try:
        sentences = {
            'sentence1': load_file(SENTENCE1_FILE),
            'sentence2': load_file(SENTENCE2_FILE)
        } # Load sentences into dictionary

        print(f"✓ Loaded sentence1: {sentences['sentence1']}" )
        print(f"✓ Loaded sentence2: {sentences['sentence2']}" )

        results = {}  # Process and store results in dictionary
        
        for name, sentence in sentences.items():
            print("\n" + "█" * 82)
            print(f"{name.upper()}")

            print("\n[1] Preprocessing...")
            preprocess = preprocess_pipeline(sentence, verbose=True)

            print("\n[2] Syntactic Reconstruction...")
            syntax = syntactic_analysis_pipeline(preprocess, verbose=True)

            print("\n[3] Grammatical Correction...")
            corrected = grammatical_correction_pipeline(syntax['reconstructed'], verbose=True, syntactic_info=syntax)

            # Store results
            results[name] = {
                'original': sentence,
                'preprocessing': preprocess,
                'syntactic': syntax,
                'corrected': corrected
            }

            print("\n" + "=" * 82)
            print(f"✓ {name.upper()} complete")
            print("=" * 82)
        
        for name in results:
            # Save
            summary = f"Original: {results[name]['original']}\n"
            summary += f"Reconstructed: {results[name]['syntactic']['reconstructed']}\n"
            summary += f"Corrected: {results[name]['corrected']}"
            save_result(summary, os.path.join(SENTENCE_RESULTS_DIR, f"{name}_summary.txt"))
        
            # Print
            print(f"\n{name.upper()}:")
            print(f"  Original:      {results[name]['original']}")
            print(f"  Reconstructed: {results[name]['syntactic']['reconstructed']}")
            print(f"  Corrected:     {results[name]['corrected']}")

        print("\n" + "█" * 35 + "  SUMMARY  " + "█" * 36)
        print(f"\n Results saved in: {SENTENCE_RESULTS_DIR}/")
        print("\n" + "█" * 82)
    
        return results

    except FileNotFoundError as e:
        print(f"\n Error: {e}")
        print(f"\nPlease create these files:")
        print(f"  - {SENTENCE1_FILE}")
        print(f"  - {SENTENCE2_FILE}")
        return None

    except ImportError as e:
        print(f"\n Import Error: {e}")
        print("Make sure your modules are set up correctly.")
        return None


# ============================== TEXT PIPELINE (1B) ==============================

def run_text_pipeline():
    print("\n" + "█" * 82)
    print("                      TEXT PIPELINES - DELIVERABLE 1B                          ")
    print("            1 (TextBlob)     |     2 (Embeddings)     |     3 (Transformer)    ")
    print("█" * 82 + "\n")

    try:
        texts = {
            'text1': load_file(TEXT1_FILE),
            'text2': load_file(TEXT2_FILE)
        } # Load texts

        print(f"✓ Loaded text1: {len(texts['text1'])} characters")
        print(f"✓ Loaded text2: {len(texts['text2'])} characters")
    
        results = {} # Process and store results in dictionary

        for name, text in texts.items():
            print("\n" + "█" * 82)
            print(f"{name.upper()}")
    
            print("\n[1] TextBlob...")
            textblob_result = pipeline_textblob_1_main(text)
    
            print("\n[2] Embeddings...")
            embeddings_result = pipeline_embeddings_2_main(text)
    
            print("\n[3] Transformer...")
            transformer_result = pipeline_transformer_3_main(text)
    
            # Store results
            results[name] = {
                'input': text,
                'textblob': textblob_result,
                'embeddings': embeddings_result,
                'transformer': transformer_result
            }
    
            print("\n" + "=" * 82)
            print(f"✓ {name.upper()} complete")
            print("=" * 82)
    
        for name in results: # Save and print 
            # Individual pipeline results
            save_result(results[name]['textblob'], os.path.join(TEXT_RESULTS_DIR, "pipeline_1_textblob", f"{name}_result.txt"))
            save_result(results[name]['embeddings'], os.path.join(TEXT_RESULTS_DIR, "pipeline_2_embeddings", f"{name}_result.txt"))
            save_result(results[name]['transformer'], os.path.join(TEXT_RESULTS_DIR, "pipeline_3_transformer", f"{name}_result.txt"))
    
            # Summary
            summary = f"=== {name.upper()} RESULTS ===\n\n"
            summary += f"--- TextBlob ---\n{results[name]['textblob']}\n\n"
            summary += f"--- Embeddings ---\n{results[name]['embeddings']}\n\n"
            summary += f"--- Transformer ---\n{results[name]['transformer']}\n"
            save_result(summary, os.path.join(TEXT_RESULTS_DIR, f"{name}_summary.txt"))

        # Print summary
        print("\n" + "█" * 35 + "  SUMMARY  " + "█" * 36)
        print(f"\n Text pipelines completed!")
        print(f"\n Results saved in: {TEXT_RESULTS_DIR}/")
        print("\n" + "█" * 82)

        return results
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print(f"\nPlease create these files:")
        print(f"  - {TEXT1_FILE}")
        print(f"  - {TEXT2_FILE}")
        return None

    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("Make sure your text_pipelines modules are set up correctly.")
        return None


# ============================== MENU SYSTEM ==============================

def display_menu():
    print("\n" + "=" * 82)
    print("                         NLP ASSIGNMENT 2025                                   ")
    print("=" * 82)
    print("""
    Please select an option:

    [1] Sentence Pipeline (Deliverable 1A)
        Preprocessing -> Syntactic Reconstruction -> Grammatical Correction

    [2] Text Pipelines (Deliverable 1B)
          TextBlob | Embeddings | Transformer

    [3] Run Both Pipelines

    [0] Exit
    """)
    print("=" * 82)

    while True:
        choice = input("\nEnter your choice (0-3): ").strip()
        if choice in ['0', '1', '2', '3']:
            return choice
        print("Invalid choice. Please enter 0, 1, 2, or 3.")


def main():
    ensure_directories() # Ensure all directories exist

    while True:
        choice = display_menu()

        if choice == '0':
            print("\nGoodbye!")
            sys.exit(0)

        elif choice == '1':
            run_sentence_pipeline()
            input("\nPress Enter to return to menu...")

        elif choice == '2':
            run_text_pipeline()
            input("\nPress Enter to return to menu...")

        elif choice == '3':
            print("\n" + "★" * 82)
            print("                         RUNNING ALL PIPELINES                              ")

            print("\n[Part 1/2] Running Sentence Pipeline...")
            run_sentence_pipeline()

            input("\nPress Enter to continue to Text Pipelines...")

            print("\n[Part 2/2] Running Text Pipelines...")
            run_text_pipeline()

            print("\n" + "★" * 82)
            print("                      ALL PIPELINES COMPLETED                               ")
            print("★" * 82)
            input("\nPress Enter to return to menu...")


# ============================== ENTRY POINT ==============================

if __name__ == "__main__":
    main()