# NLP Text Reconstruction Project
A Natural Language Processing project implementing multiple text reconstruction approaches: rule-based grammatical correction, statistical methods (TextBlob), word embeddings, and transformer-based generation.

## Project Structure
```
paradoteo1/
├── main.py                          # Entry point with interactive menu
├── data/
│   ├── raw/
│   │   ├── sentences/               # Input sentences for pipeline 1A
│   │   └── texts/                   # Input texts for pipeline 1B
│   └── results/                     # Output results
├── sentence_pipeline/               # Deliverable 1A
│   ├── preprocessing_1/             # Text normalization
│   ├── syntactic_analysis_2/        # POS-based reconstruction
│   └── grammatical_correction_3/    # Grammar rule application
└── text_pipelines/                  # Deliverable 1B
    ├── pipeline_textblob_1/         # TextBlob approach
    ├── pipeline_embeddings_2/       # Word embeddings approach
    └── pipeline_transformers_3/     # Transformer approach
```

## Requirements

### Python Version
- Python 3.8 or higher

### Dependencies

Install all required packages:
```bash
pip install nltk textblob gensim transformers torch numpy contractions
```

Or via the `requirements.txt` with:
```
nltk>=3.6
textblob>=0.15.3
gensim>=4.0.0
transformers>=4.20.0
torch>=1.9.0
numpy>=1.19.0
contractions>=0.0.50
```

Then install with:
```bash
pip install -r requirements.txt
```

### NLTK Data
After installing NLTK, download the required data:
```python
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('brown')
```

Or run in terminal:
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('wordnet'); nltk.download('omw-1.4')"
```

## Installation

### Prerequisites
This project requires **Anaconda** (or Miniconda) to manage Python and dependencies.
**Install Anaconda** (if not already installed):
   - Download from: https://www.anaconda.com/download
   - Follow the installation instructions for your operating system

### Setup
1. Clone or download the project
2. Open Anaconda Prompt (Windows) or terminal (Linux/Mac)
3. Create a new virtual environment:
   ```bash
   conda create -n nlp_project python=3.10
   ```
4. Activate the virtual environment:
   ```bash
   conda activate nlp_project
   ```
5. Navigate to the project directory:
   ```bash
   cd "/path/to/paradoteo1"
   ```
6. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Or install manually:
   ```bash
   pip install nltk textblob gensim transformers torch numpy contractions
   ```
7. Download NLTK data (see Requirements section above)
8. First run will automatically download:
   - GloVe embeddings (~128MB) for Pipeline 2
   - Flan-T5-Base model (~250MB) for Pipeline 3

## How to Run
First, make sure the virtual environment is activated:
```bash
conda activate nlp_project
```
Then run the main script:
```bash
python main.py
```

### Menu Options

| Option  | Description |
|---------|------------------------------------------------------------------------|
|  **1**  | Sentence Pipeline (1A) - Rule-based syntactical-grammatical correction |
|  **2**  | Text Pipelines (1B) - Three different text reconstruction approaches   |
|  **3**  | Run Both Pipelines                                                     |
|  **0**  | Exit                                                                   |

## Pipeline Descriptions
### Deliverable 1A: Sentence Pipeline

Processes sentences through three stages:
1. **Preprocessing** - Normalization, tokenization, POS tagging, lemmatization
2. **Syntactic Analysis** - Identifies noun phrases, verb groups, clause structure
3. **Grammatical Correction** - Applies three grammar rules:
   - Subject-verb agreement
   - Morphological consistency (tense)
   - Determiner-noun consistency

### Deliverable 1B: Text Pipelines

Three different approaches to text reconstruction:

| Pipeline   | Method               | Model/Library                   |
|------------|----------------------|---------------------------------|
| Pipeline 1 | Statistical          | TextBlob Library                |
| Pipeline 2 | Embeddings           | GloVe (glove-wiki-gigaword-100) |
| Pipeline 3 | Neural / Transformer | Google Flan-T5-Base             |

## Input Files
Place input txt files in:
- `data/raw/sentences/` - For sentence pipeline (1A)
- `data/raw/texts/` - For text pipelines (1B)

## Output
Results are saved to:
- `data/results/sentence_pipeline/` - Sentence pipeline results
- `data/results/text_pipelines/` - Text pipeline results

## GPU Support
By default, the transformer pipeline runs on CPU. To use GPU, edit `text_pipelines/pipeline_transformers_3/pipeline_3.py` and change:
```python
device=-1  # CPU
```
to:
```python
device=0   # GPU (CUDA)
```

## Troubleshooting

### "No module named X"
Install the missing package: `pip install X`

### NLTK data not found
Run the NLTK download commands listed in the Requirements section.

### Out of memory with transformer
The project uses `flan-t5-base` (~250MB). If still too large, you can try `flan-t5-small` by editing `pipeline_3.py`.

### First run is slow
Initial run downloads pretrained models (GloVe, Flan-T5). Subsequent runs will be faster.
