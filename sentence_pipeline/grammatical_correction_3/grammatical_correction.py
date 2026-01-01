import re

# ============================== STEP 1: SPELLING CORRECTION ==============================

def apply_spelling_correction(text):
    # απλή ορθογραφική διόρθωση με χρήση dictionary.
    # αντικατάσταση από προκαθορισμένο dictionary
    
    # Dictionary με κοινά ορθογραφικά → σωστές φόρμες (έχει μόνο πολύ συνηθισμένα λάθη)
    spelling_corrections = {
        # συχνά typos
        r'\brecieve\b': 'receive',
        r'\boccured\b': 'occurred',
        r'\bseperate\b': 'separate',
        r'\bdefinately\b': 'definitely',
        r'\bwierd\b': 'weird',
        r'\bneccessary\b': 'necessary',
        r'\boccasion\b': 'occasion',
        r'\bpublically\b': 'publicly',
        r'\bthier\b': 'their',
        r'\bbeleive\b': 'believe',
        r'\bbeggining\b': 'beginning',
        r'\bcommited\b': 'committed',
        r'\bexistance\b': 'existence',
        r'\bconsious\b': 'conscious',
        r'\bfourty\b': 'forty',
        r'\buntill\b': 'until',
        
        # συντομεύσεις χωρίς απόστροφο
        r'\bcant\b': "can't",
        r'\bdont\b': "don't",
        r'\bdidnt\b': "didn't",
        r'\bisnt\b': "isn't",
        r'\barent\b': "aren't",
        r'\bwasnt\b': "wasn't",
        r'\bwerent\b': "weren't",
        r'\bhasnt\b': "hasn't",
        r'\bhavent\b': "haven't",
        r'\bhadnt\b': "hadn't",
        r'\bwont\b': "won't",
        r'\bwouldnt\b': "wouldn't",
        r'\bshouldnt\b': "shouldn't",
        r'\bcouldnt\b': "couldn't",
        
        # πιο συγκεκριμένα
        r'\balot\b': 'a lot',
        r'\btheir are\b': 'there are',
        r'\byour welcome\b': "you're welcome",
    }
    
    corrected_text = text
    for pattern, replacement in spelling_corrections.items():
        corrected_text = re.sub(pattern, replacement, corrected_text, flags=re.IGNORECASE)
    
    return corrected_text

# ============================== STEP 2: SURFACE GRAMMAR RULES ==============================

def apply_surface_grammar_rules(text, pos_tags):
    # Επιφανειακοί γραμματικοί κανόνες
    # χρήση POS tags για αφαίρεση επιθέτων, καθαρισμό διπλών προσδιοριστικών, επαναλαμβανόμενων tokens
    # Δεν δημιουργούνται νέες ετικέτες, εφαρμόζονται οι κανόνες μόνο αν POS tags παρέχονται από προηγούμενο στάδιο επεξεργασίας
    # Δεν έχουμε: Deep syntax, dependency parsing, subject-verb agreement, POS generation
    # Δέχεται κείμενο και POS tags από προηγούμενη επεξεργασία και το επιστρέφει καθαρισμένο
    # Πληροφορίες: Natural Language Processing Recipes - Chapter 4 (Grammatical Normalization)    
    
    # Αν δεν υπάρχουν POS tags, χρησιμοποίησε μόνο καθαρισμένο σε επίπεδο συμβολοσειράς
    if pos_tags is None or len(pos_tags) == 0:
        return apply_string_level_cleanup(text)
    
    tokens = pos_tags
    cleaned_tokens = []
    i = 0
    
    while i < len(tokens):
        word, pos = tokens[i]
        
        # Rule 1: αφαίρεση διπλών προσδιορισμών (the the, a a)
        if pos == 'DT' and i + 1 < len(tokens):
            next_word, next_pos = tokens[i + 1]
            if next_pos == 'DT' and word.lower() == next_word.lower():
                # παράλειψη διπλότυπου προσδιοριστή
                i += 1
                continue
        
        # Rule 2: αφαίρεση "ορφανών" επιθέτων στο τέλος (επίθετο που δεν ακολουθείται από ουσιαστικό)
        if pos in ['JJ', 'JJR', 'JJS'] and i == len(tokens) - 1:
            i += 1 # τελευταία λέξη επίθετο -> αφαίρεση
            continue
        
        # Rule 3: επιφανειακός έλεγχος για διπλότυπες λέξεις
        if i + 1 < len(tokens):
            next_word, _ = tokens[i + 1]
            if word.lower() == next_word.lower():
                cleaned_tokens.append(word) # Διπλύτυπη λέξη -> διατήρηση μιας
                i += 2
                continue
        
        # Rule 4: αφαίρεση ορφανών προσδιοριστών στο τέλος
        if pos == 'DT' and i == len(tokens) - 1:
            i += 1 # προσδιοριστική τελευταία λέξη -> αφαίρεση
            continue
        
        # Rule 5: αφαίρεση υπερβολικών διαδοχικών επιθέτων (σφάλμα ανακατασκευής)
        if pos in ['JJ', 'JJR', 'JJS']:
            adj_count = 1
            j = i + 1
            while j < len(tokens) and tokens[j][1] in ['JJ', 'JJR', 'JJS']:
                adj_count += 1
                j += 1
            
            if adj_count > 3: # If >3 διαδοχικά επίθετα, κράτα 2
                i += adj_count - 2
                continue

        # Rule 6: Remove orphan prepositions at end
        if pos == 'IN' and i == len(tokens) - 1:
            # Last word is preposition → remove
            i += 1
            continue
        
        # Rule 7: Remove consecutive prepositions (in to with → keep first)
        if pos == 'IN' and i + 1 < len(tokens):
            next_word, next_pos = tokens[i + 1]
            if next_pos == 'IN':
                # Two prepositions in a row → skip second
                cleaned_tokens.append(word)
                i += 2
                continue
        
        cleaned_tokens.append(word)
        i += 1
    
    result = ' '.join(cleaned_tokens) # Ανακατασκευή κειμένου
    
    return result


def apply_string_level_cleanup(text):
    # Εφαρμογή καθαρισμού στην συμβολοσειρά, χωρίς POS tags    
    # Συντηρητικοί κανόνες που δεν απαιτούν συντακτική ανάλυση
    
    # Αφαίρεση διπ΄λότυπων (λέξη λέξη -> λέξη)
    text = re.sub(r'\b(\w+)\s+\1\b', r'\1', text, flags=re.IGNORECASE)
    
    # αφαίρεση τριπλών + επαναλαμβανόμενων τροποποιητών
    text = re.sub(r'\b(very|really|so)\s+\1\s+\1\b', 
                  r'\1', text, flags=re.IGNORECASE)
    
    return text

# ============================== STEP 2.5: SYNTACTIC-BASED GRAMMAR RULES ==============================

# --- Constants for grammar rules ---

# Singular pronouns that require singular verbs
SINGULAR_PRONOUNS = {'i', 'he', 'she', 'it', 'this', 'that', 'everyone', 'someone', 
                     'anyone', 'no one', 'nobody', 'somebody', 'everybody', 'each', 
                     'either', 'neither', 'one'}

# Plural pronouns that require plural verbs
PLURAL_PRONOUNS = {'we', 'they', 'these', 'those', 'both', 'few', 'many', 'several'}

# Special case: 'you' can be singular or plural but takes plural verb forms
SECOND_PERSON_PRONOUNS = {'you'}

# Verb form mappings for agreement
VERB_AGREEMENT_MAP = {
    # singular -> plural forms
    'is': 'are',
    'was': 'were',
    'has': 'have',
    'does': 'do',
    # plural -> singular forms (reverse mapping)
    'are': 'is',
    'were': 'was',
    'have': 'has',
    'do': 'does',
}

# Singular determiners
SINGULAR_DETERMINERS = {'a', 'an', 'this', 'that', 'every', 'each', 'either', 'neither'}

# Plural determiners
PLURAL_DETERMINERS = {'these', 'those', 'many', 'few', 'several', 'both', 'some', 'all'}

# Base form verb endings for tense detection
PAST_TENSE_INDICATORS = {'VBD'}  # Past tense verbs
PRESENT_TENSE_INDICATORS = {'VBZ', 'VBP', 'VBG'}  # Present tense forms
BASE_FORM_INDICATORS = {'VB'}  # Base form


def get_subject_number(subject_tokens, pos_tags):
    """
    Determine if subject is singular or plural based on tokens and POS tags.
    Returns: 'singular', 'plural', or 'unknown'
    """
    if not subject_tokens:
        return 'unknown'
    
    # Get the head noun (last noun in the subject phrase)
    head_word = subject_tokens[-1].lower()
    
    # Check pronouns first
    if head_word in SINGULAR_PRONOUNS:
        return 'singular'
    if head_word in PLURAL_PRONOUNS:
        return 'plural'
    if head_word in SECOND_PERSON_PRONOUNS:
        return 'plural'  # 'you' takes plural verb forms
    
    # Find POS tag for head word
    for token, pos in pos_tags:
        if token.lower() == head_word:
            # NNS and NNPS are plural nouns
            if pos in ['NNS', 'NNPS']:
                return 'plural'
            # NN and NNP are singular nouns
            elif pos in ['NN', 'NNP']:
                return 'singular'
            # PRP needs specific check
            elif pos == 'PRP':
                if head_word in SINGULAR_PRONOUNS:
                    return 'singular'
                elif head_word in PLURAL_PRONOUNS:
                    return 'plural'
                elif head_word in SECOND_PERSON_PRONOUNS:
                    return 'plural'
    
    return 'unknown'


def apply_subject_verb_agreement(text, pos_tags, svo_components):
    """
    Rule 1: Subject-Verb Agreement
    Uses SVO components from syntactic analysis to enforce agreement.
    - singular subject → is / has / does
    - plural subject → are / have / do
    """
    if not svo_components or not pos_tags:
        return text
    
    subject = svo_components.get('subject', [])
    verb = svo_components.get('verb', [])
    
    if not subject or not verb:
        return text
    
    # Determine subject number
    subject_number = get_subject_number(subject, pos_tags)
    
    if subject_number == 'unknown':
        return text
    
    corrected_text = text
    
    # Check each verb token for agreement
    for verb_token in verb:
        verb_lower = verb_token.lower()
        
        if verb_lower in VERB_AGREEMENT_MAP:
            # Determine if verb form matches subject number
            needs_singular = subject_number == 'singular'
            is_singular_verb = verb_lower in ['is', 'was', 'has', 'does']
            
            if needs_singular and not is_singular_verb:
                # Subject is singular but verb is plural -> fix
                correct_form = VERB_AGREEMENT_MAP.get(verb_lower, verb_lower)
                # Preserve original case
                if verb_token[0].isupper():
                    correct_form = correct_form.capitalize()
                corrected_text = re.sub(
                    r'\b' + re.escape(verb_token) + r'\b',
                    correct_form,
                    corrected_text,
                    count=1
                )
            elif not needs_singular and is_singular_verb:
                # Subject is plural but verb is singular -> fix
                correct_form = VERB_AGREEMENT_MAP.get(verb_lower, verb_lower)
                # Preserve original case
                if verb_token[0].isupper():
                    correct_form = correct_form.capitalize()
                corrected_text = re.sub(
                    r'\b' + re.escape(verb_token) + r'\b',
                    correct_form,
                    corrected_text,
                    count=1
                )
    
    return corrected_text


def get_main_verb_tense(verb_groups, pos_tags):
    """
    Identify the tense/form of the main verb from verb groups.
    Returns: 'past', 'present', 'base', or 'unknown'
    """
    if not verb_groups:
        return 'unknown', None
    
    # Find the main verb group
    main_verb_info = None
    for start, end, tokens, is_main in verb_groups:
        if is_main:
            main_verb_info = (start, end, tokens)
            break
    
    if not main_verb_info:
        # Use first verb group as fallback
        if verb_groups:
            start, end, tokens, _ = verb_groups[0]
            main_verb_info = (start, end, tokens)
        else:
            return 'unknown', None
    
    start, end, main_tokens = main_verb_info
    
    # Check POS tags for main verb tokens
    for i in range(start, min(end, len(pos_tags))):
        token, pos = pos_tags[i]
        if pos in PAST_TENSE_INDICATORS:
            return 'past', main_tokens
        elif pos in PRESENT_TENSE_INDICATORS:
            return 'present', main_tokens
        elif pos in BASE_FORM_INDICATORS:
            return 'base', main_tokens
    
    return 'unknown', main_tokens


def get_verb_base_form(verb):
    """
    Get approximate base form of a verb using simple rules.
    This is a simplified heuristic-based approach.
    """
    verb_lower = verb.lower()
    
    # Common irregular verbs mapping
    irregular_verbs = {
        'is': 'be', 'am': 'be', 'are': 'be', 'was': 'be', 'were': 'be', 'been': 'be', 'being': 'be',
        'has': 'have', 'had': 'have', 'having': 'have',
        'does': 'do', 'did': 'do', 'doing': 'do', 'done': 'do',
        'goes': 'go', 'went': 'go', 'gone': 'go', 'going': 'go',
        'says': 'say', 'said': 'say', 'saying': 'say',
        'makes': 'make', 'made': 'make', 'making': 'make',
        'takes': 'take', 'took': 'take', 'taken': 'take', 'taking': 'take',
        'comes': 'come', 'came': 'come', 'coming': 'come',
        'sees': 'see', 'saw': 'see', 'seen': 'see', 'seeing': 'see',
        'gets': 'get', 'got': 'get', 'gotten': 'get', 'getting': 'get',
        'knows': 'know', 'knew': 'know', 'known': 'know', 'knowing': 'know',
        'thinks': 'think', 'thought': 'think', 'thinking': 'think',
        'gives': 'give', 'gave': 'give', 'given': 'give', 'giving': 'give',
        'finds': 'find', 'found': 'find', 'finding': 'find',
        'tells': 'tell', 'told': 'tell', 'telling': 'tell',
        'becomes': 'become', 'became': 'become', 'becoming': 'become',
        'leaves': 'leave', 'left': 'leave', 'leaving': 'leave',
        'puts': 'put', 'putting': 'put',
        'keeps': 'keep', 'kept': 'keep', 'keeping': 'keep',
        'lets': 'let', 'letting': 'let',
        'begins': 'begin', 'began': 'begin', 'begun': 'begin', 'beginning': 'begin',
        'shows': 'show', 'showed': 'show', 'shown': 'show', 'showing': 'show',
        'hears': 'hear', 'heard': 'hear', 'hearing': 'hear',
        'runs': 'run', 'ran': 'run', 'running': 'run',
        'holds': 'hold', 'held': 'hold', 'holding': 'hold',
        'brings': 'bring', 'brought': 'bring', 'bringing': 'bring',
        'writes': 'write', 'wrote': 'write', 'written': 'write', 'writing': 'write',
        'sits': 'sit', 'sat': 'sit', 'sitting': 'sit',
        'stands': 'stand', 'stood': 'stand', 'standing': 'stand',
        'loses': 'lose', 'lost': 'lose', 'losing': 'lose',
        'pays': 'pay', 'paid': 'pay', 'paying': 'pay',
        'meets': 'meet', 'met': 'meet', 'meeting': 'meet',
        'sends': 'send', 'sent': 'send', 'sending': 'send',
        'builds': 'build', 'built': 'build', 'building': 'build',
        'falls': 'fall', 'fell': 'fall', 'fallen': 'fall', 'falling': 'fall',
        'cuts': 'cut', 'cutting': 'cut',
        'reads': 'read', 'reading': 'read',
        'grows': 'grow', 'grew': 'grow', 'grown': 'grow', 'growing': 'grow',
        'opens': 'open', 'opened': 'open', 'opening': 'open',
        'walks': 'walk', 'walked': 'walk', 'walking': 'walk',
        'wins': 'win', 'won': 'win', 'winning': 'win',
        'teaches': 'teach', 'taught': 'teach', 'teaching': 'teach',
        'buys': 'buy', 'bought': 'buy', 'buying': 'buy',
        'spends': 'spend', 'spent': 'spend', 'spending': 'spend',
        'watches': 'watch', 'watched': 'watch', 'watching': 'watch',
        'speaks': 'speak', 'spoke': 'speak', 'spoken': 'speak', 'speaking': 'speak',
        'stops': 'stop', 'stopped': 'stop', 'stopping': 'stop',
        'plays': 'play', 'played': 'play', 'playing': 'play',
        'moves': 'move', 'moved': 'move', 'moving': 'move',
        'lives': 'live', 'lived': 'live', 'living': 'live',
        'works': 'work', 'worked': 'work', 'working': 'work',
        'calls': 'call', 'called': 'call', 'calling': 'call',
        'tries': 'try', 'tried': 'try', 'trying': 'try',
        'asks': 'ask', 'asked': 'ask', 'asking': 'ask',
        'needs': 'need', 'needed': 'need', 'needing': 'need',
        'feels': 'feel', 'felt': 'feel', 'feeling': 'feel',
        'creates': 'create', 'created': 'create', 'creating': 'create',
        'provides': 'provide', 'provided': 'provide', 'providing': 'provide',
        'includes': 'include', 'included': 'include', 'including': 'include',
        'continues': 'continue', 'continued': 'continue', 'continuing': 'continue',
        'changes': 'change', 'changed': 'change', 'changing': 'change',
        'leads': 'lead', 'led': 'lead', 'leading': 'lead',
        'understands': 'understand', 'understood': 'understand', 'understanding': 'understand',
        'follows': 'follow', 'followed': 'follow', 'following': 'follow',
        'reaches': 'reach', 'reached': 'reach', 'reaching': 'reach',
        'sets': 'set', 'setting': 'set',
        'learns': 'learn', 'learned': 'learn', 'learnt': 'learn', 'learning': 'learn',
        'helps': 'help', 'helped': 'help', 'helping': 'help',
        'starts': 'start', 'started': 'start', 'starting': 'start',
        'carries': 'carry', 'carried': 'carry', 'carrying': 'carry',
        'happens': 'happen', 'happened': 'happen', 'happening': 'happen',
        'looks': 'look', 'looked': 'look', 'looking': 'look',
        'uses': 'use', 'used': 'use', 'using': 'use',
        'wants': 'want', 'wanted': 'want', 'wanting': 'want',
        'goes': 'go', 'went': 'go', 'gone': 'go', 'going': 'go',
    }
    
    if verb_lower in irregular_verbs:
        return irregular_verbs[verb_lower]
    
    # Regular verb patterns
    # -ing form
    if verb_lower.endswith('ing'):
        # running -> run, making -> make
        base = verb_lower[:-3]
        if base.endswith(base[-1]) and len(base) > 2:  # doubled consonant
            base = base[:-1]
        elif len(base) > 0:
            # Check if we need to add 'e' back
            if base + 'e' + 'ing' == verb_lower + 'ing':
                base = base + 'e'
        return base if base else verb_lower
    
    # -ed form (past tense)
    if verb_lower.endswith('ed'):
        base = verb_lower[:-2]
        if base.endswith(base[-1]) and len(base) > 2:  # doubled consonant
            base = base[:-1]
        return base if base else verb_lower
    
    # -s/-es form (3rd person singular)
    if verb_lower.endswith('ies'):
        return verb_lower[:-3] + 'y'
    if verb_lower.endswith('es'):
        return verb_lower[:-2]
    if verb_lower.endswith('s'):
        return verb_lower[:-1]
    
    return verb_lower


def apply_morphological_consistency(text, pos_tags, verb_groups):
    """
    Rule 2: Morphological Consistency of Verbs
    Identifies the main verb tense and normalizes other verbs to maintain consistency.
    Does not infer new tense or change sentence meaning.
    """
    if not verb_groups or not pos_tags or len(verb_groups) <= 1:
        return text
    
    # Get main verb tense
    main_tense, main_tokens = get_main_verb_tense(verb_groups, pos_tags)
    
    if main_tense == 'unknown' or not main_tokens:
        return text
    
    corrected_text = text
    
    # Common tense inconsistency patterns to fix
    # These are surface-level fixes based on detected patterns
    inconsistent_patterns = {
        # If main verb is past, fix present forms that should be past
        'past': {
            r'\b(and|then|but)\s+(is)\b': r'\1 was',
            r'\b(and|then|but)\s+(are)\b': r'\1 were',
            r'\b(and|then|but)\s+(has)\b': r'\1 had',
            r'\b(and|then|but)\s+(have)\b': r'\1 had',
            r'\b(and|then|but)\s+(does)\b': r'\1 did',
            r'\b(and|then|but)\s+(do)\b': r'\1 did',
        },
        # If main verb is present, fix past forms that should be present
        'present': {
            r'\b(and|then|but)\s+(was)\b': r'\1 is',
            r'\b(and|then|but)\s+(were)\b': r'\1 are',
            r'\b(and|then|but)\s+(had)\b': r'\1 has',
            r'\b(and|then|but)\s+(did)\b': r'\1 does',
        }
    }
    
    if main_tense in inconsistent_patterns:
        for pattern, replacement in inconsistent_patterns[main_tense].items():
            corrected_text = re.sub(pattern, replacement, corrected_text, flags=re.IGNORECASE)
    
    return corrected_text


def get_noun_number_from_phrase(phrase_tokens, pos_tags):
    """
    Determine if noun phrase is singular or plural.
    Returns: 'singular', 'plural', or 'unknown'
    """
    if not phrase_tokens:
        return 'unknown'
    
    # Get the head noun (typically the last noun in the phrase)
    for token in reversed(phrase_tokens):
        token_lower = token.lower()
        # Find POS tag for this token
        for word, pos in pos_tags:
            if word.lower() == token_lower:
                if pos in ['NNS', 'NNPS']:
                    return 'plural'
                elif pos in ['NN', 'NNP']:
                    return 'singular'
    
    return 'unknown'


def apply_determiner_noun_consistency(text, pos_tags, noun_phrases):
    """
    Rule 3: Determiner-Noun Consistency
    Uses noun phrase information from syntactic analysis to enforce agreement.
    - Avoid singular determiners with plural nouns
    - Remove orphan determiners
    """
    if not pos_tags or not noun_phrases:
        return text
    
    corrected_text = text
    
    # Check each noun phrase for determiner-noun consistency
    for start_idx, end_idx, phrase_tokens in noun_phrases:
        if len(phrase_tokens) < 2:
            continue
        
        # Check if first token is a determiner
        first_token = phrase_tokens[0].lower()
        
        # Get the determiner's POS tag
        det_pos = None
        if start_idx < len(pos_tags):
            det_pos = pos_tags[start_idx][1]
        
        if det_pos != 'DT':
            continue
        
        # Get noun number
        noun_number = get_noun_number_from_phrase(phrase_tokens[1:], pos_tags)
        
        if noun_number == 'unknown':
            continue
        
        # Check for inconsistencies
        if first_token in SINGULAR_DETERMINERS and noun_number == 'plural':
            # Singular determiner with plural noun - problematic
            # Fix: remove 'a'/'an' before plural nouns
            if first_token in ['a', 'an']:
                # Remove the article before plural noun
                phrase_str = ' '.join(phrase_tokens)
                fixed_phrase = ' '.join(phrase_tokens[1:])
                corrected_text = corrected_text.replace(phrase_str, fixed_phrase, 1)
            # For 'this'/'that' with plural -> 'these'/'those'
            elif first_token == 'this':
                phrase_str = ' '.join(phrase_tokens)
                new_phrase = 'these ' + ' '.join(phrase_tokens[1:])
                corrected_text = re.sub(
                    r'\b' + re.escape(phrase_str) + r'\b',
                    new_phrase,
                    corrected_text,
                    count=1,
                    flags=re.IGNORECASE
                )
            elif first_token == 'that':
                phrase_str = ' '.join(phrase_tokens)
                new_phrase = 'those ' + ' '.join(phrase_tokens[1:])
                corrected_text = re.sub(
                    r'\b' + re.escape(phrase_str) + r'\b',
                    new_phrase,
                    corrected_text,
                    count=1,
                    flags=re.IGNORECASE
                )
        
        elif first_token in PLURAL_DETERMINERS and noun_number == 'singular':
            # Plural determiner with singular noun
            # For 'these'/'those' with singular -> 'this'/'that'
            if first_token == 'these':
                phrase_str = ' '.join(phrase_tokens)
                new_phrase = 'this ' + ' '.join(phrase_tokens[1:])
                corrected_text = re.sub(
                    r'\b' + re.escape(phrase_str) + r'\b',
                    new_phrase,
                    corrected_text,
                    count=1,
                    flags=re.IGNORECASE
                )
            elif first_token == 'those':
                phrase_str = ' '.join(phrase_tokens)
                new_phrase = 'that ' + ' '.join(phrase_tokens[1:])
                corrected_text = re.sub(
                    r'\b' + re.escape(phrase_str) + r'\b',
                    new_phrase,
                    corrected_text,
                    count=1,
                    flags=re.IGNORECASE
                )
    
    # Remove orphan determiners (determiners not followed by noun-like content)
    # This is handled by looking for patterns like "the ." or "a ," 
    corrected_text = re.sub(r'\b(a|an|the)\s+([.,!?;:])', r'\2', corrected_text)
    
    return corrected_text


def apply_syntactic_grammar_rules(text, pos_tags, syntactic_info):
    """
    Apply grammar rules using syntactic analysis information.
    This function integrates all three required grammar rules:
    1. Subject-Verb Agreement
    2. Morphological Consistency of Verbs
    3. Determiner-Noun Consistency
    """
    if not syntactic_info:
        return text
    
    # Extract syntactic components
    noun_phrases = syntactic_info.get('noun_phrases', [])
    verb_groups = syntactic_info.get('verb_groups', [])
    svo_components = syntactic_info.get('svo_components', {})
    
    corrected_text = text
    
    # Rule 1: Subject-Verb Agreement
    corrected_text = apply_subject_verb_agreement(corrected_text, pos_tags, svo_components)
    
    # Rule 2: Morphological Consistency of Verbs
    corrected_text = apply_morphological_consistency(corrected_text, pos_tags, verb_groups)
    
    # Rule 3: Determiner-Noun Consistency
    corrected_text = apply_determiner_noun_consistency(corrected_text, pos_tags, noun_phrases)
    
    return corrected_text
    
# ============================== STEP 3: POST-PROCESSING ==============================

def apply_post_processing(text):    
    # Εφαρμογή βασικής μορφοποίησης κειμένου 
    # χρήση κανόνων μορφοποίησης κειμένου: Πρώτο γράμμα κεφαλαίο, προσθήκη τελείας στο τέλος, 
    # καθαρισμός κενών και βασική στίξη  
    
    if not text:
        return text
    
    text = re.sub(r'\s+', ' ', text.strip()) # αφαίρεση επιπλέων κενών (αν και ήδη έχει γίνει 3 φο΄ρες)
    
    # Διόρθωση κενών γύρω από τα σημεία στίξης και αφαίρεση τους πριν 
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    
    # προσθήκη κενού μετά τα σημεία στίξης αν λείπει
    text = re.sub(r'([.,!?;:])([A-Za-z])', r'\1 \2', text)
    
    # Πρώτο γράμμα κεφαλαίο
    if text: text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
    
    # πρόσθεσε τελεία αν λείπει και δενμ υπάρχει άλλο σημείο στίξης
    if text and text[-1] not in '.!?': text += '.'
    
    # Διόρθωση πολλαπλών σημείων στίξης
    text = re.sub(r'\.{2,}', '.', text)
    text = re.sub(r'!{2,}', '!', text)
    text = re.sub(r'\?{2,}', '?', text)
    
    # Καθαρισμός ειδικών χαρακτήρων
    text = re.sub(r'\s+([.,!?])', r'\1', text)
    
    return text

# ============================== STEP 4: PRINT FUNCTIONS ==============================

def print_correction_step(step_number, step_name, content):
    # εκτύπωση βήματος με μορφοποίηση
    # δέχεται step_number, όνομα βήματος, περιεχόμενο προς εμφάνιση
    print(f"\n[Step {step_number}] {step_name}")
    print("-" * 80)
    
    if isinstance(content, str):
        print(content)
    elif isinstance(content, dict):
        for key, value in content.items():
            print(f"  {key}: {value}")
    else:
        print(content)

# =========== STEP 0.5: Επιπλέον προσθήκη POS tags στο reconstructed text ================
def retag_reconstructed_text(reconstructed_text):
    # Προσθήκη ετικετών POS στο νέο string η συνατκτική ανακατασκεύη αναδιατάσσει το κείμενο άρα οι ετικέτες του pre-processing δεν ταιριάζουν εδώ
    # δέχεται reconstructed_text(string) -> επιστρέφει New POS tags [(token, tag), ...]
    from nltk.tokenize import word_tokenize
    from nltk import pos_tag
    
    # Tokenize and tag the reconstructed text
    tokens = word_tokenize(reconstructed_text)
    new_pos_tags = pos_tag(tokens)
    
    return new_pos_tags

# ============================== MAIN GRAMMATICAL CORRECTION PIPELINE ==============================

def grammatical_correction_pipeline(text, verbose, syntactic_info=None):
    """
    Διαδικασία γραμματικής διόρθωσης. Κάνει σε σειρά τα εξής:
    1. Διόρθωση ορθογραφίας
    2. Εφαρμογή επιφανειακών γραμματικών κανόνων
    2.5. Εφαρμογή γραμματικών κανόνων βασισμένων σε συντακτική ανάλυση (NEW)
         - Subject-Verb Agreement
         - Morphological Consistency of Verbs  
         - Determiner-Noun Consistency
    3. Post-processing 
    
    Δέχεται:
    - text: κείμενο προς διόρθωση
    - verbose: αν αληθής τυπώνει τα βήματα
    - syntactic_info: (optional) dictionary με αποτελέσματα συντακτικής ανάλυσης
                     (noun_phrases, verb_groups, svo_components, clauses)
    
    Based on: Natural Language Processing Recipes
    """

    if not text or not text.strip(): 
        return text
    
    if verbose:
        print("\n" + "="*80)
        print("GRAMMATICAL CORRECTION & SMOOTHING")
        print("="*80)
        print_correction_step(0, "Input (Reconstructed Sentence)", text)

    # Step 0.5: προσθήκη νέων ετικετών στο reconstructed
    pos_tags = retag_reconstructed_text(text)
    if verbose: 
        print_correction_step(0.5, "Re-tagged for Grammar Rules", f"{len(pos_tags)} POS tags: {pos_tags[:5]}...")

    # Step 1: διόρθωση ορθογραφικών
    corrected = apply_spelling_correction(text)
    if verbose:
        changes = "Changes applied" if corrected != text else "No changes"
        print_correction_step(1, "After Spelling Correction", f"{corrected}\n({changes})")
    
    # Step 2: επιφανειακοί γραμματικοί κανόνες
    before_grammar = corrected
    corrected = apply_surface_grammar_rules(corrected, pos_tags)
    if verbose:
        changes = "Changes applied" if corrected != before_grammar else "No changes"
        print_correction_step(2, "After Surface Grammar Rules", f"{corrected}\n({changes})")
    
    # Step 2.5: Syntactic-based grammar rules (NEW)
    # Only apply if syntactic_info is provided
    if syntactic_info:
        before_syntactic = corrected
        
        # Re-tag after surface grammar rules (text may have changed)
        pos_tags = retag_reconstructed_text(corrected)
        
        corrected = apply_syntactic_grammar_rules(corrected, pos_tags, syntactic_info)
        
        if verbose:
            changes = "Changes applied" if corrected != before_syntactic else "No changes"
            print_correction_step(2.5, "After Syntactic Grammar Rules", f"{corrected}\n({changes})")
            
            # Print details of what was checked
            svo = syntactic_info.get('svo_components', {})
            if svo.get('subject') and svo.get('verb'):
                print(f"    Subject: {' '.join(svo.get('subject', []))}")
                print(f"    Verb: {' '.join(svo.get('verb', []))}")
                print(f"    Applied: Subject-Verb Agreement, Morphological Consistency, Determiner-Noun Consistency")
    
    # Step 3: Post-processing
    before_post = corrected
    corrected = apply_post_processing(corrected)
    if verbose:
        changes = "Changes applied" if corrected != before_post else "No changes"
        print_correction_step(3, "After Post-processing (FINAL)", f"{corrected}\n({changes})")
    
    if verbose:
        print("\n" + "="*80)
        print("✓ Grammatical correction complete")
        print("="*80)
    
    return corrected