# Συντακτική ανακατασκευή χρησιμοποιώντας ετικέτες POS, εξαγωγή ουσιαστικών (noun),
# string transformation με βάση κανόνες και pattern matching
import re
from typing import List, Tuple, Dict

# ============== CONSTANTS ==============

# συνδετικές λέξεις
SUBORDINATE_CONJUNCTIONS = {
    'although', 'because', 'if', 'when', 'while', 'since', 
    'unless', 'until', 'whereas', 'though', 'after', 'before', 'as'
}

# βοηθητικά ρήματα
AUXILIARY_VERBS = {
    'be', 'am', 'is', 'are', 'was', 'were', 'been', 'being',
    'have', 'has', 'had', 'having',
    'do', 'does', 'did', 'doing',
    'will', 'would', 'shall', 'should', 'may', 'might', 'must', 
    'can', 'could', 'ought'
}


# ΝΝ = common noun
# NNS = common noun plural
# NNP = proper noun, singular
# NNPS = proper noun, plural

# PRP = αντωνυμία personal pronoun
# PRP$ = possesive pronoun πχ my

# DT = determiner πχ the

# JJ = adjective - επίθετο good
# JJR = comparative adjective better
# JJS = superlative adjective πχ best

# RB = επίρρημα adverb πχ quickly
# RBR = comparative adverb πχ faster
# RBS = superlative adverb πχ fastest

# VB* = όλα τα ρήματα πιάνονται σε αυτό
# MD = modal πχ can, should, will

# IN = preposition/ subordinating conjuction πχ in, on, because, if

# RP = phrasal verb particles πχ up, out, pick up



# ============== STEP 1: POS PATTERN DETECTION ==============

def identify_noun_phrases(pos_tags):
    # Βρες “ονοματικές φράσεις” (NP) με απλούς κανόνες POS.
    # Patterns:
    # - DT? JJ* NN(S)?  (e.g., "the big dog")
    # - PRP$ JJ* NN(S)?  (e.g., "my new car")
    # - NN(S)? alone
    # - PRP alone
    # Επιστρέφει: List[Tuple[start_idx, end_idx, tokens]]
    noun_phrases = []
    i = 0
    
    while i < len(pos_tags):
        phrase_start = i
        phrase_tokens = []
        
        # Pronouns alone (PRP)
        if pos_tags[i][1] == 'PRP':
            noun_phrases.append((i, i+1, [pos_tags[i][0]]))
            i += 1
            continue
        
        # Determiners (DT) or Possessives (PRP$)
        if pos_tags[i][1] in ['DT', 'PRP$']:
            phrase_tokens.append(pos_tags[i][0])
            i += 1
        
        # Adjectives (JJ, JJR, JJS)
        while i < len(pos_tags) and pos_tags[i][1] in ['JJ', 'JJR', 'JJS']:
            phrase_tokens.append(pos_tags[i][0])
            i += 1
        
        # Nouns (NN, NNS, NNP, NNPS)
        if i < len(pos_tags) and pos_tags[i][1] in ['NN', 'NNS', 'NNP', 'NNPS']:
            phrase_tokens.append(pos_tags[i][0])
            i += 1
            
            # We have a noun phrase
            if len(phrase_tokens) > 0:
                noun_phrases.append((phrase_start, i, phrase_tokens))
        else:
            # Not a complete noun phrase
            if len(phrase_tokens) == 0:
                # Check if standalone noun
                if i < len(pos_tags) and pos_tags[i][1] in ['NN', 'NNS', 'NNP', 'NNPS']:
                    noun_phrases.append((i, i+1, [pos_tags[i][0]]))
                    i += 1
                else:
                    i = phrase_start + 1
            else:
                i = phrase_start + 1
    
    return noun_phrases

# Αναγνώριση ομάδων ρημάτων και διάκριση βοηθητικών από κύριων ρημάτων 
def find_verb_groups(pos_tags):
    # Επιστρέφει: List of (start_idx, end_idx, tokens, is_main_verb)
    verb_groups = []
    i = 0
    
    while i < len(pos_tags):
        phrase_start = i
        phrase_tokens = []
        
        # Έλεγχος κύριου ή δευτερεύων / βοηθητικού
        if pos_tags[i][1] == 'MD' or (pos_tags[i][1].startswith('VB') and pos_tags[i][0].lower() in AUXILIARY_VERBS):
            phrase_tokens.append(pos_tags[i][0])
            i += 1
        
        # κύριο ρήμα
        if i < len(pos_tags) and pos_tags[i][1].startswith('VB'):
            phrase_tokens.append(pos_tags[i][0])
            is_main = pos_tags[i][0].lower() not in AUXILIARY_VERBS
            i += 1
            
            if i < len(pos_tags) and pos_tags[i][1] == 'RP':
                phrase_tokens.append(pos_tags[i][0])
                i += 1
            
            if len(phrase_tokens) > 0:
                verb_groups.append((phrase_start, i, phrase_tokens, is_main))
        else:
            if len(phrase_tokens) > 0:
                verb_groups.append((phrase_start, i, phrase_tokens, False))
            else:
                i += 1
    
    return verb_groups

# Εντοπισμός δευτερεύουσων συδνέσμων χρησιμοποιώντας μόνο την λίστα λέξεων 
def detect_subordinate_conjunctions(pos_tags):
    subordinate_markers = []
    
    for i, (token, pos) in enumerate(pos_tags):
        if token.lower() in SUBORDINATE_CONJUNCTIONS:
            subordinate_markers.append((i, token.lower()))
    
    return subordinate_markers

# ============== STEP 2: PROBLEMATIC PATTERN DETECTION WITH FIXES ==============
def fix_preposition_adjective_no_noun(pos_tags, problem_idx):
    # Fix: IN + JJ without NN
    # Επισύναψη επίθετου στην πλησιέστερη ακόλουθη ονοματική φράση - Επιστρέφει τροποποιημένα POS tags 
    # Εύρεση πλησιέστερου ουσιαστικού μετά το επίθετο
    nearest_noun_idx = None
    for i in range(problem_idx + 2, min(problem_idx + 5, len(pos_tags))):
        if pos_tags[i][1] in ['NN', 'NNS', 'NNP', 'NNPS']:
            nearest_noun_idx = i
            break
    
    if nearest_noun_idx:
        adj_token = pos_tags[problem_idx + 1] # Επίθετο δίπλα από το ουσιαστικό 
        # Αναδιάταξη: διατήρηση πρόθεσης, μετακίνηση επιθέτου και ουσιαστικού μαζί
        new_tags = (
            pos_tags[:problem_idx+1] +  # Keep up to preposition
            [adj_token] +                # Adjective
            [pos_tags[nearest_noun_idx]] +  # Noun
            pos_tags[problem_idx+2:nearest_noun_idx] +  # In-between
            pos_tags[nearest_noun_idx+1:]  # Rest
        )
        return new_tags
    
    return pos_tags

# ρήμα χωρίς σαφές υποκείμενο
def fix_verb_without_subject(pos_tags, verb_idx):
    # Εύρεση πλησιέστερου NP/PRP και μετακίνησή τους πριν το ρήμα
    # Αναζήτηση υποψήφιων υποκειμένων γύρω από το ρήμα - εντός 5 tokens 
    subject_idx = None
    
    # Πρώτα έλεγχος πριν το ρήμα
    for i in range(max(0, verb_idx - 5), verb_idx):
        if pos_tags[i][1] in ['NN', 'NNS', 'NNP', 'NNPS', 'PRP']:
            subject_idx = i
    
    # Αν δεν το βρει, τότε έλεγξε μετά το ρήμα
    if subject_idx is None:
        for i in range(verb_idx + 1, min(verb_idx + 5, len(pos_tags))):
            if pos_tags[i][1] in ['NN', 'NNS', 'NNP', 'NNPS', 'PRP']:
                subject_idx = i
                break
    
    if subject_idx is not None and subject_idx != verb_idx - 1:
        # Μετακίνησε το υποκείμενο πριν το ρήμα 
        subject_token = pos_tags[subject_idx]
        
        if subject_idx < verb_idx:
            # Υποκείμενο είναι πριν αλλά όχι αμέσως πριν
            new_tags = (
                pos_tags[:subject_idx] +  # Before 
                pos_tags[subject_idx+1:verb_idx] +  # Between (subject-verb)
                [subject_token] +  # Subject moved 
                pos_tags[verb_idx:]  # Verb and rest
            )
        else:
            # Υποκείμενο είναι μετά, μετακίνησε το πριν
            new_tags = (
                pos_tags[:verb_idx] +  # Before
                [subject_token] +  # Subject moved 
                pos_tags[verb_idx:subject_idx] +  # Verb to subject
                pos_tags[subject_idx+1:]  # After subject
            )
        
        return new_tags
    
    return pos_tags

# Η πρόταση ξεκινάει με επίθετο/ επίρρημα χωρίς δομή
def fix_unusual_start(pos_tags):
    # Μετακίνηση μετά το πρώτο noun phrase ή verb
    if len(pos_tags) < 2:
        return pos_tags
    
    first_token = pos_tags[0]
    
    # Βρες πρώτο ουσιαστικό ή ρήμα
    target_idx = None
    for i in range(1, len(pos_tags)):
        if pos_tags[i][1] in ['NN', 'NNS', 'NNP', 'NNPS', 'PRP'] or pos_tags[i][1].startswith('VB'):
            target_idx = i
            break
    
    if target_idx:
        # Μετακίνηση επιθέτου/επιρρήματος μετά τον στόχο
        new_tags = (
            pos_tags[1:target_idx+1] +  # Skip first, go to target
            [first_token] +  # Move first token here
            pos_tags[target_idx+1:]  # Rest
        )
        return new_tags
    
    return pos_tags

# Εντοπισμός προβληματικών μοτίβων και εφαρμογή διορθώσεων
def detect_and_fix_problems(pos_tags):
    # Επιστρέφει: (fixed_pos_tags, problems_found)
    problems = []
    fixed_tags = list(pos_tags)
    
    # Problem 1: IN + JJ without NN
    i = 0
    while i < len(fixed_tags) - 1:
        if fixed_tags[i][1] == 'IN' and fixed_tags[i+1][1] in ['JJ', 'JJR', 'JJS']:
            # Check if followed by noun
            has_noun = False
            if i+2 < len(fixed_tags) and fixed_tags[i+2][1] in ['NN', 'NNS', 'NNP', 'NNPS']:
                has_noun = True
            
            if not has_noun:
                problems.append({
                    'type': 'preposition_adjective_no_noun',
                    'position': i,
                    'original': [fixed_tags[i][0], fixed_tags[i+1][0]]
                })
                fixed_tags = fix_preposition_adjective_no_noun(fixed_tags, i)
        i += 1
    
    # Problem 2: Verb without subject (check main verbs only)
    verb_groups = find_verb_groups(fixed_tags)
    for start, end, tokens, is_main in verb_groups:
        if is_main:
            # Check for subject before verb
            has_subject = False
            for i in range(max(0, start - 3), start):
                if fixed_tags[i][1] in ['NN', 'NNS', 'NNP', 'NNPS', 'PRP']:
                    has_subject = True
                    break
            
            if not has_subject and start > 0:
                problems.append({
                    'type': 'verb_without_subject',
                    'position': start,
                    'original': tokens
                })
                fixed_tags = fix_verb_without_subject(fixed_tags, start)
    
    # Problem 3: Unusual start
    if len(fixed_tags) > 0 and fixed_tags[0][1] in ['JJ', 'RB', 'RBR', 'RBS']:
        if len(fixed_tags) < 3 or fixed_tags[1][1] not in ['NN', 'NNS', 'NNP', 'NNPS', 'PRP']:
            problems.append({
                'type': 'unusual_start',
                'position': 0,
                'original': [fixed_tags[0][0]]
            })
            # Apply fix
            fixed_tags = fix_unusual_start(fixed_tags)
    
    return fixed_tags, problems

# ============== STEP 3: S-V-O EXTRACTION ==============

# Εξαγωγή SVO Υποκείμενο-Ρήμα-Αντικείμενο
def extract_svo_components(pos_tags):
    # Επιστρέφει dictionary με: 'subject', 'verb', 'object', 'prepositional_phrases', 'other'
    components = {
        'subject': [],
        'verb': [],
        'object': [],
        'prepositional_phrases': [],  # ← ΝΕΟ!
        'other': []
    }
    
    noun_phrases = identify_noun_phrases(pos_tags)
    verb_groups = find_verb_groups(pos_tags)
    
    # Βρες όλα τα ρήματα (για να ελέγξουμε πολλαπλά ρήματα) 
    all_verb_positions = [start for start, end, tokens, is_main in verb_groups]
    
    # Βρες το κύριο ρήμα (πρώτα είναι το κύριο, μετά το βοηθητικό)
    main_verb_idx = None
    main_verb_tokens = []
    
    for start, end, tokens, is_main in verb_groups:
        if is_main:
            main_verb_idx = start
            main_verb_tokens = tokens
            components['verb'] = tokens
            break
    
    # Αν δεν έχει κύριο ρήμα, χρησιμοποίησε το πρώτο
    if main_verb_idx is None and len(verb_groups) > 0:
        main_verb_idx = verb_groups[0][0]
        main_verb_tokens = verb_groups[0][2]
        components['verb'] = main_verb_tokens
    
    # Εξαγωγή προθετικών φράσεων (IN + NP)
    prepositional_phrases = extract_prepositional_phrases(pos_tags, noun_phrases)
    components['prepositional_phrases'] = prepositional_phrases
    
    # Υποκείμενο: κοντινότερο NP πριν το κύριο ρήμα (όχι το πρώτο NP)
    if main_verb_idx is not None:
        closest_np = None
        closest_distance = float('inf')
        
        for start, end, tokens in noun_phrases:
            if end <= main_verb_idx:
                distance = main_verb_idx - end
                if distance < closest_distance:
                    closest_distance = distance
                    closest_np = tokens
        
        if closest_np:
            components['subject'] = closest_np
    
    # Υποκείμενο: Πρώτο NP μετά το κύριο ρήμα
    if main_verb_idx is not None:
        verb_end = main_verb_idx + len(main_verb_tokens)
        for start, end, tokens in noun_phrases:
            if start >= verb_end:
                components['object'] = tokens
                break
    
    # Συλλογή υπόλοιπων tokens (εκτός από prep phrases)
    used_indices = set()
    
    # Σημείωσε χρησιμοποιημένους δείκτες
    for start, end, tokens in noun_phrases:
        if tokens == components['subject'] or tokens == components['object']:
            used_indices.update(range(start, end))
    
    if main_verb_idx is not None:
        used_indices.update(range(main_verb_idx, main_verb_idx + len(main_verb_tokens)))
    
    # Σημείωσε τους δείκτες προθετικών φράσεων
    for prep_idx, np_start, np_end in prepositional_phrases:
        used_indices.update(range(prep_idx, np_end))
    
    # Σύλλεξε τα λοιπά tokens
    for i, (token, pos) in enumerate(pos_tags):
        if i not in used_indices and token not in [',', '.', '!', '?']:
            components['other'].append(token)
    
    return components
    
# helper function για το SVO - Εξαγωγή προθετικών φράσεων (IN + NP)
def extract_prepositional_phrases(pos_tags, noun_phrases):
    # Επιστρέφει λίστα
    prep_phrases = []
    
    for i, (token, pos) in enumerate(pos_tags):
        if pos == 'IN': # Ψάξε το NP που ακολουθεί 
            for start, end, tokens in noun_phrases:
                if start == i + 1:  
                    prep_phrases.append((i, start, end))
                    break
    
    return prep_phrases



# ============== STEP 4: CLAUSE IDENTIFICATION AND REORDERING ==============

# Διαχωρισμός πρότασης σε κύριες και εξαρτημένες χρησιμοποι΄ώντας σαφής συνδέσμους
def identify_clauses(pos_tags):
    # Επιστρέφει dictionary με: 'main', 'dependent', 'subordinate_positions'
    clauses = {
        'main': [],
        'dependent': [],
        'subordinate_positions': []
    }
    
    sub_positions = detect_subordinate_conjunctions(pos_tags) # Βρες σαφείς βοηθητικούς συνδέσμους
    
    if len(sub_positions) == 0: # Αν δεν υπάρχει εξαρτημένη πρόταση, τότε όλα είναι κύρια        
        clauses['main'] = list(range(len(pos_tags)))
        return clauses
    
    clauses['subordinate_positions'] = [pos for pos, word in sub_positions]
    
    # Αν ο δευτερεύων σύνδεσμος είναι στην αρχή (3 πρώτες θέσεις )
    if sub_positions[0][0] < 3:
        # Η εξαρτημένη πρόταση προηγείται - βρες αν υπάρχει κομμα
        boundary = len(pos_tags) // 2
        for i in range(sub_positions[0][0] + 1, len(pos_tags)):
            if pos_tags[i][0] == ',':
                boundary = i
                break
        
        clauses['dependent'] = list(range(sub_positions[0][0], boundary + 1))
        clauses['main'] = list(range(boundary + 1, len(pos_tags)))
    else: # Κύρια πρόταση πρώτα
        clauses['main'] = list(range(0, sub_positions[0][0]))
        clauses['dependent'] = list(range(sub_positions[0][0], len(pos_tags)))
    
    return clauses


def reorder_clause(pos_tags):
    # Αναδιάταξη μιας μεμονωμένης πρότασης σε δομή S-V-O με προθετικές φράσεις.
    if len(pos_tags) == 0:
        return ""
    
    components = extract_svo_components(pos_tags)
    # Σχηματισμός πρότασης: Υποκείμενο + Ρήμα + Αντικείμενο + Προθετικές φράσεις + Άλλο
    parts = []
    
    if components['subject']:
        parts.append(' '.join(components['subject']))
    
    if components['verb']:
        parts.append(' '.join(components['verb']))
    
    if components['object']:
        parts.append(' '.join(components['object']))
    
    # Προσθήκη προθετικών φράσεων (που διατηρούνται μαζί ως μονάδες)
    if components['prepositional_phrases']:
        for prep_idx, np_start, np_end in components['prepositional_phrases']:
            prep_token = pos_tags[prep_idx][0]
            np_tokens = [pos_tags[i][0] for i in range(np_start, np_end)]
            prep_phrase = f"{prep_token} {' '.join(np_tokens)}"
            parts.append(prep_phrase)
    
    # Προσθήκη υπόλοιπων tokens
    if components['other']:
        parts.append(' '.join(components['other']))
    
    result = ' '.join(parts)
    
    return result


def handle_clauses(pos_tags):
    # Χειρισμός πολλαπλών προτάσεων με καλύτερη ανίχνευση ορίων.
    # 1. Διαχωρισμός με συντονισμένους συνδέσμους (and, but, or)
    # 2. Προσδιορισμός εξαρτημένων προτάσεων (με δευτερεύοντες συνδέσμους)
    # 3. Αναδιάταξη

    # CΈλεγχος για συντονισμένους συνδέσμους (CC: and, but, or)
    coord_conj_positions = []
    for i, (token, pos) in enumerate(pos_tags):
        if pos == 'CC' or token.lower() in ['but', 'and', 'or']:
            coord_conj_positions.append(i)
    
    # Αν υπάρχουν πολλαπλοί συντονισμένοι σύνδεσμοι, χωρίσε τους σε ξεχωριστές προτάσεις
    if len(coord_conj_positions) > 0:
        clauses = []
        start = 0
        
        for conj_pos in coord_conj_positions:
            clause_tokens = pos_tags[start:conj_pos]
            if len(clause_tokens) > 0:
                clauses.append((clause_tokens, None))  # (tokens, conjunction)
            
            conjunction = pos_tags[conj_pos][0] # Αποθήκευση συνδέσμο
            start = conj_pos + 1
            clauses[-1] = (clauses[-1][0], conjunction) if clauses else (clause_tokens, conjunction)
        
        if start < len(pos_tags): # Τε΄λευταία πρόταση
            clauses.append((pos_tags[start:], None))
        
        # Αναδιάταξη και συνδυασμός κάθε πρότασης
        reconstructed_clauses = []
        for clause_tokens, conj in clauses:
            if len(clause_tokens) > 0:
                reordered = reorder_clause(clause_tokens)
                if conj:
                    reconstructed_clauses.append(f"{reordered} {conj}")
                else:
                    reconstructed_clauses.append(reordered)
        
        return ' '.join(reconstructed_clauses)
    
    # Αλλιώς χειρισμός ως μια πρόταση με εξαρτημένη
    clause_info = identify_clauses(pos_tags)
    
    if len(clause_info['dependent']) == 0:
        return reorder_clause(pos_tags)
    
    main_tokens = [pos_tags[i] for i in clause_info['main']]
    dependent_tokens = [pos_tags[i] for i in clause_info['dependent']]
    
    main_reconstructed = ""
    if len(main_tokens) > 0:
        main_reconstructed = reorder_clause(main_tokens)
    
    dependent_reconstructed = ""
    if len(dependent_tokens) > 0:
        conjunction = dependent_tokens[0][0]
        rest_tokens = dependent_tokens[1:]
        
        if len(rest_tokens) > 0:
            rest_reconstructed = reorder_clause(rest_tokens)
            dependent_reconstructed = f"{conjunction} {rest_reconstructed}".strip()
        else:
            dependent_reconstructed = conjunction
    
    if main_reconstructed and dependent_reconstructed:
        result = f"{main_reconstructed}, {dependent_reconstructed}"
    elif main_reconstructed:
        result = main_reconstructed
    else:
        result = dependent_reconstructed
    
    return result

# ============== STEP 5: PRINT FUNCTIONS ==============

def print_analysis_step(step_number, step_name, content):
    # Εκτύπωση βήματος
    print(f"\n[Step {step_number}] {step_name}")
    print("-" * 80)
    
    if isinstance(content, str):
        print(content)
    elif isinstance(content, list):
        if len(content) > 0:
            if isinstance(content[0], tuple):
                print(f"Found {len(content)} items:")
                for item in content[:5]:
                    print(f"  {item}")
                if len(content) > 5:
                    print(f"  ... and {len(content) - 5} more")
            else:
                print(content)
        else:
            print("None found")
    elif isinstance(content, dict):
        for key, value in content.items():
            if isinstance(value, list):
                print(f"  {key}: {len(value)} items")
            else:
                print(f"  {key}: {value}")
    else:
        print(content)

# ============== MAIN SYNTACTIC ANALYSIS PIPELINE ==============

def syntactic_analysis_pipeline(preprocessing_dict, verbose):
    # 1. Εντοπισμός και διόρθωση προβληματικών μοτίβων
    # 2. Προσδιορισμός noun phrases και verb groups
    # 3. Εξαγωγή S-V-O στοιχείων 
    # 4. Προσδιορισμός και αναδιάταξη προτάσεων
    # 5. Αναδόμηση πρότασης
    # Παίρνει pos_tags από το preprocessing και μεταβλητή που αν αληθής δείχνει τα βήματα
    # Επιστρέφει dicrionary με: original, reconstructed, analysis details
    pos_tags = preprocessing_dict.get('pos_tags', [])

    if len(pos_tags) == 0:
        return {
            'original': '',
            'reconstructed': '',
            'noun_phrases': [],
            'verb_groups': [],
            'problems_fixed': [],
            'clauses': {},
            'svo_components': {}
        }
    
    # Original 
    original = ' '.join([token for token, _ in pos_tags])
    
    if verbose:
        print("\n" + "="*80)
        print("SYNTACTIC ANALYSIS & RECONSTRUCTION")
        print("="*80)
        print_analysis_step(0, "Original Sentence", original)
    
    # Step 1: Εντοπισμός και διόρθωση προβλημάτων
    fixed_pos_tags, problems = detect_and_fix_problems(pos_tags)
    
    if verbose:
        if len(problems) > 0:
            print_analysis_step(1, "Problems Detected & Fixed", problems)
        else:
            print_analysis_step(1, "Problems Detected & Fixed", "No problems detected")
    
    # Step 2: Αναγνώριση noun phrases
    noun_phrases = identify_noun_phrases(fixed_pos_tags)
    if verbose:
        print_analysis_step(2, "Noun Phrases Identified", noun_phrases)
    
    # Step 3: Αναγνώριση verb groups 
    verb_groups = find_verb_groups(fixed_pos_tags)
    if verbose:
        formatted_verbs = [(start, end, tokens, "MAIN" if is_main else "AUX") 
                          for start, end, tokens, is_main in verb_groups]
        print_analysis_step(3, "Verb Groups Identified", formatted_verbs)
    
    # Step 4: Αναγνώριση προτάσεων
    clauses = identify_clauses(fixed_pos_tags)
    if verbose:
        print_analysis_step(4, "Clause Structure", clauses)
    
    # Step 5: Εξαγωγή S-V-O 
    svo_components = extract_svo_components(fixed_pos_tags)
    if verbose:
        print_analysis_step(5, "S-V-O Components Extracted", svo_components)
    
    # Step 6: Ανακατασκευή με χειρισμό προτάσεων
    reconstructed = handle_clauses(fixed_pos_tags)
    
    # Step 7: Καθαρισμός
    reconstructed = re.sub(r'\s+([.,!?])', r'\1', reconstructed)
    reconstructed = re.sub(r'\s+', ' ', reconstructed).strip()
    
    # Πρώτο γράμμα κεφαλαίο
    if reconstructed: reconstructed = reconstructed[0].upper() + reconstructed[1:]
    
    # Βάλε τελεία αν λείπει
    if reconstructed and reconstructed[-1] not in '.!?': reconstructed += '.'
    
    if verbose:
        print_analysis_step(6, "Reconstructed Sentence (FINAL)", reconstructed)
        print("\n" + "="*80)
        print("✓ Syntactic reconstruction complete")
        print("="*80)
    
    # Return only syntactic analysis results
    return {
        'original': original,
        'reconstructed': reconstructed,
        'noun_phrases': noun_phrases,
        'verb_groups': verb_groups,
        'problems_fixed': problems,
        'clauses': clauses,
        'svo_components': svo_components
    }
