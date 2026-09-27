# English → Regional Language Translator
### Machine Translation using Natural Language Processing & Pretrained Transformer Models

![Project Banner](https://img.shields.io/badge/NLP-Machine%20Translation-6366f1)
![Model](https://img.shields.io/badge/Model-Helsinki--NLP%20MarianMT-10b981)
![Framework](https://img.shields.io/badge/Backend-FastAPI-38bdf8)
![Frontend](https://img.shields.io/badge/Frontend-React%2019%20%2B%20Vite-f43f5e)
![Evaluation](https://img.shields.io/badge/Metric-SacreBLEU-f59e0b)

---

## 1. Project Title
**English to Regional Language Translator (IndicTranslate)**  
*Neural Machine Translation for Indian Regional Languages using Transformer Architectures.*

---

## 2. Project Description
The **English to Regional Language Translator** is an end-to-end Machine Translation web application built as an academic Natural Language Processing mini-project. It translates English source text into Indian regional languages (**Hindi** and **Marathi**) using open-weights pretrained Transformer models from Hugging Face (`Helsinki-NLP/opus-mt-en-hi` and `Helsinki-NLP/opus-mt-en-mr`). 

All neural inferences run **locally** on CPU/CUDA without reliance on proprietary, paid external translation APIs (such as Google Cloud Translation or DeepL). The system features a responsive React/Vite user interface, a robust FastAPI backend with model in-memory caching, translation history tracking, and quantitative model evaluation using the standardized **BLEU (Bilingual Evaluation Understudy)** score.

---

## 3. Problem Statement
India is a linguistically diverse nation with 22 officially recognized languages and hundreds of regional dialects. While a vast amount of technical literature, academic knowledge, government resources, and digital web services are produced in English, large segments of the population are most fluent in regional languages like Hindi and Marathi. 

Manual human translation cannot scale to meet this demand. Automated **Machine Translation (MT)** provides a scalable solution to bridge the digital language barrier, enabling linguistic inclusivity and knowledge democratization.

---

## 4. Objectives
- **Local Neural Inference**: Implement translation entirely on local hardware using open pretrained Transformer models.
- **Support Regional Indian Languages**: Provide reliable translation from English into Hindi (`hi`) and Marathi (`mr`), with an extensible modular structure to support additional languages.
- **Low-Latency Architecture**: Cache loaded Transformer models and tokenizers in backend memory to avoid cold starts across API calls.
- **Empirical Evaluation**: Benchmark the translation system using standard automated evaluation metrics (**Corpus & Sentence SacreBLEU**) against human ground-truth translations.
- **Academic & Intuitive UI**: Build a clean, presentation-ready web dashboard with dual translation panels, sample test queries, copy utilities, history persistence, and model inspection.

---

## 5. Features
- **Dual-Language Support**: English → Hindi and English → Marathi.
- **Transformer-Powered Inference**: Utilizes MarianMT encoder-decoder neural models with beam search generation.
- **Real-Time Latency Tracking**: Computes and displays inference time in milliseconds for each translated sentence.
- **Model In-Memory Caching**: Thread-safe lazy loading ensures models are loaded into memory only once per process.
- **BLEU Evaluation Dashboard**: Dedicated `/evaluation` page to trigger live evaluations on a benchmark dataset and view sentence-level comparative results.
- **Translation History**: Local session persistence (via `localStorage`) with clear and reload capabilities.
- **Modern Responsive UI**: Built with React 19, custom CSS variables, glassmorphism design, and Devanagari typography.
- **CLI & Script Execution**: Standalone evaluation script (`backend/evaluation.py`) for command-line benchmarks.

---

## 6. Technology Stack

### Frontend
- **React.js 19**: Component-based user interface and state management.
- **Vite 8**: High-speed build tooling and local development server.
- **Lucide React**: Clean vector iconography.
- **Custom Modern CSS**: Tailored design tokens, responsive CSS grid/flexbox, glassmorphism cards, and Google Fonts (`Inter` + `Noto Sans Devanagari`).

### Backend
- **Python 3.10+ / 3.13**: Core programming language.
- **FastAPI**: Asynchronous high-performance REST API framework.
- **Uvicorn**: ASGI web server.
- **Pydantic v2**: Strict request/response data validation and serialization.

### NLP & Machine Learning
- **PyTorch (torch 2.9+)**: Deep learning tensor computing framework.
- **Hugging Face Transformers**: MarianMT model loading, pipeline orchestration, and generation.
- **SentencePiece**: Subword tokenization and Byte-Pair Encoding (BPE) vocabulary models.
- **SacreBLEU**: Standardized computation of BLEU scores.
- **Pandas**: Evaluation dataset parsing and manipulation.

---

## 7. NLP Concepts Used

```text
Natural Language Processing (NLP)
              ↓
  Machine Translation (MT)
              ↓
  Subword Tokenization (BPE / SentencePiece)
              ↓
  Transformer Architecture (Encoder-Decoder)
              ↓
  Pretrained Seq2Seq Language Models (MarianMT)
              ↓
  Autoregressive Generation (Beam Search)
              ↓
  Empirical Evaluation (BLEU Metric)
```

1. **Sequence-to-Sequence (Seq2Seq)**:
   Mapping an input sequence of variable length in the source language $X = (x_1, \dots, x_T)$ to an output sequence of variable length in the target language $Y = (y_1, \dots, y_{T'})$.

2. **Subword Tokenization (SentencePiece / BPE)**:
   Rather than treating words as atomic units (which suffers from Out-of-Vocabulary issues), SentencePiece segments words into subword units based on character frequency statistics.

3. **Self-Attention Mechanism**:
   Enables the model to weigh the relevance of all other tokens in a sentence when computing the representation of a given token, resolving pronoun antecedents and syntactic relationships:
   $$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

4. **Autoregressive Decoding & Beam Search**:
   During target generation, the decoder emits tokens one by one conditioned on previously generated tokens and encoder hidden states. Beam search maintains the top $K$ ($K=4$) candidate hypotheses at each step rather than greedy 1-best selection, improving output fluency.

---

## 8. Machine Translation Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                      Input English Text                     │
│               "I am learning machine learning."             │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  Text Preprocessing Unit                    │
│      (Whitespace trimming, punctuation normalization)       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              MarianTokenizer (SentencePiece)                │
│       Subword BPE token IDs: [142, 89, 2341, 1024, 2]       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 MarianMT Transformer Model                  │
│  ┌────────────────────────┐     ┌────────────────────────┐  │
│  │   Transformer Encoder  │ ──> │  Transformer Decoder   │  │
│  │  (6 Attention Layers)  │     │ (Autoregressive 6 Lyr) │  │
│  └────────────────────────┘     └────────────────────────┘  │
│                             │                               │
│                      Beam Search (K=4)                      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   Generated Token IDs                       │
│             [541, 1892, 4310, 192, 381, 108, 0]             │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Tokenizer Decoding                       │
│                     Detokenization                          │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Output Regional Translation                 │
│               "मैं मशीन लर्निंग सीख रहा हूँ।"               │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. Model Information

The models used in this project are part of the **OPUS-MT** project trained by Helsinki-NLP on the open parallel corpus (OPUS):

| Language Pair | Hugging Face Model ID | Parameters | Architecture | Target Script |
|:---|:---|:---|:---|:---|
| **English → Hindi** | `Helsinki-NLP/opus-mt-en-hi` | ~75 Million | MarianMT (BART/Transformer-based) | Devanagari |
| **English → Marathi** | `Helsinki-NLP/opus-mt-en-mr` | ~75 Million | MarianMT (BART/Transformer-based) | Devanagari |

### Why MarianMT?
- **Lightweight & Efficient**: ~300 MB disk footprint per model, allowing execution on standard consumer laptops with CPU.
- **Fast Latency**: Inference typically completes within 100ms - 400ms on modern multi-core CPUs.
- **No API Cost**: 100% free and open-source under the Apache-2.0 / CC-BY-4.0 licenses.
- **Extensible**: OPUS-MT provides pretrained checkpoints for dozens of languages (Bengali, Tamil, Telugu, Gujarati), which can be added simply by adding a key to `SUPPORTED_LANGUAGES` in `backend/translator.py`.

---

## 10. Dataset Information
A benchmark test dataset is located at:
`backend/data/test_dataset.csv`

The dataset contains parallel English sentences alongside human ground-truth reference translations in both Hindi and Marathi across various conversational and academic domains (greetings, technology, science, education).

```csv
english,hindi,marathi
"How are you?","आप कैसे हैं?","तुम्ही कसे आहात?"
"Good morning.","सुप्रभात।","शुभ प्रभात."
"Thank you.","धन्यवाद।","धन्यवाद."
"I am learning machine learning.","मैं मशीन लर्निंग सीख रहा हूँ।","मी मशीन लर्निंग शिकत आहे."
"I am learning NLP.","मैं NLP सीख रहा हूँ।","मी NLP शिकत आहे."
"Natural language processing is interesting.","प्राकृतिक भाषा प्रसंस्करण दिलचस्प है।","नैसर्गिक भाषा प्रक्रिया मनोरंजक आहे."
"India is a beautiful country.","भारत एक सुंदर देश है।","भारत एक सुंदर देश आहे."
"Knowledge is power.","ज्ञान ही शक्ति है।","ज्ञान हीच शक्ती आहे."
"Where is the library?","पुस्तकालय कहाँ है?","ग्रंथालय कुठे आहे?"
"We are working on an artificial intelligence project.","हम एक आर्टिफिशियल इंटेलिजेंस प्रोजेक्ट पर काम कर रहे हैं।","आम्ही एका आर्टिफिशियल इंटेलिजेंस प्रोजेक्टवर काम करत आहोत."
```
*Note: This sample dataset is strictly used for testing and quantitative evaluation. It is not used for fine-tuning or training.*

---

## 11. Project Structure

```text
nlp/
├── backend/
│   ├── data/
│   │   └── test_dataset.csv     # Sample evaluation benchmark dataset
│   ├── evaluation.py            # BLEU calculation engine and CLI test runner
│   ├── main.py                  # FastAPI server with CORS & REST endpoints
│   ├── models.py                # Pydantic schemas for request/response validation
│   ├── requirements.txt         # Python dependencies
│   └── translator.py            # MarianMT model manager, caching & inference
│
├── frontend/
│   ├── public/                  # Static assets
│   ├── src/
│   │   ├── components/
│   │   │   ├── AboutSection.jsx        # Project info & interactive pipeline diagram
│   │   │   ├── LanguageSelector.jsx    # Target language selector tabs
│   │   │   ├── Navbar.jsx              # Navigation header
│   │   │   ├── TranslationHistory.jsx  # History panel with localStorage sync
│   │   │   └── Translator.jsx          # Dual-panel translation workbench
│   │   ├── pages/
│   │   │   ├── Evaluation.jsx          # BLEU benchmark dashboard
│   │   │   └── Home.jsx                # Main translator landing view
│   │   ├── App.jsx                     # Application routing & layout
│   │   ├── index.css                   # Modern design system & styling
│   │   └── main.jsx                    # Vite React entry point
│   ├── index.html               # HTML document with Google Fonts
│   ├── package.json             # NPM dependencies and scripts
│   └── vite.config.js           # Vite server configuration
│
├── .gitignore                   # Ignore rules for python, node, and caches
├── README.md                    # Detailed documentation
└── requirements.txt             # Root level Python dependencies
```

---

## 12. Installation Instructions

### Prerequisites
- **Python**: Version 3.10 to 3.13 installed
- **Node.js**: Version 18+ and **npm** installed
- **Git**: (Optional, for version control)

### Step 1: Install Backend Dependencies
Open your terminal in the project root directory and run:

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Install Frontend Dependencies
Open a second terminal window or navigate to the `frontend` folder:

```bash
cd frontend
npm install
```

---

## 13. How to Run Backend

From the `backend` directory, launch the FastAPI server using Uvicorn:

```bash
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

- API Base URL: `http://127.0.0.1:8000`
- Interactive Swagger Documentation: `http://127.0.0.1:8000/docs`
- Alternative ReDoc Documentation: `http://127.0.0.1:8000/redoc`

---

## 14. How to Run Frontend

From the `frontend` directory, start the Vite development server:

```bash
cd frontend
npm run dev
```

- Access the web interface in your browser at: `http://localhost:5173`

---

## 15. API Documentation

### 1. `GET /`
- **Description**: Health check, device information (`cpu` or `cuda`), and supported language list.
- **Response**:
```json
{
  "status": "healthy",
  "service": "English to Regional Language Translator",
  "device": "cpu",
  "supported_languages": [
    {"code": "hi", "name": "Hindi", "native": "हिन्दी"},
    {"code": "mr", "name": "Marathi", "native": "मराठी"}
  ]
}
```

### 2. `GET /languages`
- **Description**: Returns all registered target languages and their respective Hugging Face model IDs.

### 3. `POST /translate`
- **Description**: Translates English source text to the specified target language.
- **Request Body**:
```json
{
  "text": "I am learning machine learning.",
  "source_language": "en",
  "target_language": "hi"
}
```
- **Response**:
```json
{
  "source_text": "I am learning machine learning.",
  "translated_text": "मैं मशीन लर्निंग सीख रहा हूँ।",
  "source_language": "en",
  "target_language": "hi",
  "inference_time_ms": 284.15
}
```

### 4. `POST /evaluate` (or `GET /evaluate?target_language=hi`)
- **Description**: Evaluates the model against the benchmark dataset and calculates genuine BLEU score and latency.
- **Request Body**:
```json
{
  "target_language": "hi"
}
```
- **Response**:
```json
{
  "target_language": "hi",
  "target_language_name": "Hindi",
  "bleu_score": 42.18,
  "num_sentences": 10,
  "avg_inference_time_ms": 295.4,
  "results": [
    {
      "id": 1,
      "source_text": "How are you?",
      "reference_text": "आप कैसे हैं?",
      "predicted_text": "आप कैसे हैं?",
      "sentence_bleu": 100.0
    }
  ]
}
```

---

## 16. Evaluation Methodology

Automated evaluation is performed through the following steps:
1. **Parallel Ingestion**: `evaluation.py` loads `backend/data/test_dataset.csv`.
2. **Model Inference**: Every English source sentence is fed through `translator.py`.
3. **Latency Measurement**: Wall-clock duration per sentence is tracked using high-resolution monotonic timers (`time.perf_counter()`).
4. **Scoring**: Predicted hypotheses and ground-truth references are passed to `sacrebleu.corpus_bleu()` and `sacrebleu.sentence_bleu()`.

You can also run the evaluation directly via the CLI:

```bash
# Evaluate Hindi
python backend/evaluation.py --lang hi

# Evaluate Marathi
python backend/evaluation.py --lang mr
```

---

## 17. BLEU Score Explanation

**BLEU (Bilingual Evaluation Understudy)** measures the lexical correspondence between machine translations and human references:

$$\text{BLEU} = \text{BP} \cdot \exp\left( \sum_{n=1}^{N} w_n \ln p_n \right)$$

Where:
- $p_n$: Modified $n$-gram precision (typically $N=4$, $w_n = 1/4$).
- $\text{BP}$: Brevity Penalty to penalize hypotheses shorter than the reference:
  $$\text{BP} = \begin{cases} 1 & \text{if } c > r \\ e^{(1 - r/c)} & \text{if } c \leq r \end{cases}$$
  where $c$ is the candidate length and $r$ is the effective reference length.

### Score Interpretation Table
| BLEU Range | Quality Level | Interpretation |
|:---|:---|:---|
| **< 10** | Almost Useless | Vocabulary poorly aligned or wrong language |
| **10 - 20** | Hard to Understand | Basic words translated but syntax incorrect |
| **20 - 30** | Fair / Understandable | Captures general meaning with grammatical flaws |
| **30 - 40** | Good Quality | Fluent, accurate translations for most common phrases |
| **40 - 50** | High Quality | Near human-level correspondence for standard domain text |
| **> 50** | Very High / Exact | Highly fluent, near-identical to references |

---

## 18. Limitations
- **Idiomatic Nuances**: Highly colloquial regional idioms or regional proverbs may be translated literally.
- **Named Entities**: Transliteration of unusual Western names or new technical jargon may require domain dictionary lookup.
- **Morphological Diversity**: Indian languages feature rich morphology and word compounding (sandhi), which can occasionally penalize exact n-gram matching in BLEU even when meaning is preserved.
- **Resource Intensity on CPU**: While MarianMT models are lightweight, translating long multi-page documents on CPU may exhibit noticeable latency.

---

## 19. Future Improvements
- **IndicTrans2 Integration**: Support larger Indic models (e.g., AI4Bharat IndicTrans2) when GPU resources are available.
- **Speech-to-Text & Text-to-Speech**: Integrate Whisper (STT) and gTTS / Coqui TTS for end-to-end voice translation.
- **Additional Languages**: Expand configuration to support Gujarati (`gu`), Bengali (`bn`), Tamil (`ta`), and Telugu (`te`).
- **Domain Adaptation**: Fine-tune models on medical or legal parallel corpora.
- **Export Formats**: Allow downloading translation history and evaluation reports as PDF or CSV.

---

## 20. College Viva & Presentation Q&A

**Q1: Why did you choose MarianMT instead of an API like Google Translate?**  
*Answer:* Relying on external paid APIs does not demonstrate NLP implementation. MarianMT allows us to run actual deep learning neural inference locally on our machine, control beam search parameters, observe subword tokenization directly, and demonstrate an autonomous ML project.

**Q2: How does MarianMT handle vocabulary differences between English and Devanagari?**  
*Answer:* MarianMT uses a SentencePiece subword tokenizer. Rather than whole words, text is split into subword units (BPE). This allows the model to handle unseen compound words and share subword roots across related Indian languages.

**Q3: What role does Beam Search play during text generation?**  
*Answer:* In greedy search, the model chooses the single highest probability token at step $t$, which can lead to sub-optimal sentences. Beam search maintains the top $K$ (e.g., $K=4$) candidate sequences globally, yielding grammatically sound translations.
#   n l p - p r o j e c t  
 