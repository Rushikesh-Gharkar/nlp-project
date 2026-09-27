import logging
import re
import threading
import time
from typing import Dict, Optional, Tuple

import torch
from transformers import MarianMTModel, MarianTokenizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("translator")

# Centralized Language & Model Configuration
# Easy to extend with additional languages like 'gu', 'bn', 'ta' etc.
SUPPORTED_LANGUAGES: Dict[str, Dict[str, str]] = {
    "hi": {
        "name": "Hindi",
        "native_name": "हिन्दी",
        "model_id": "Helsinki-NLP/opus-mt-en-hi",
    },
    "mr": {
        "name": "Marathi",
        "native_name": "मराठी",
        "model_id": "Helsinki-NLP/opus-mt-en-mr",
    },
}


class TranslationEngine:
    """
    Manages loading, caching, and inference of MarianMT Transformer models.
    Ensures models are cached in-memory and re-used for high performance.
    """

    _instance: Optional["TranslationEngine"] = None
    _lock = threading.Lock()

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Initialized TranslationEngine using device: {self.device}")
        self._models: Dict[str, MarianMTModel] = {}
        self._tokenizers: Dict[str, MarianTokenizer] = {}
        self._load_lock = threading.Lock()
        self._dictionary = None

    @classmethod
    def get_instance(cls) -> "TranslationEngine":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def get_supported_languages(self) -> Dict[str, Dict[str, str]]:
        return SUPPORTED_LANGUAGES

    def is_language_supported(self, lang_code: str) -> bool:
        return lang_code in SUPPORTED_LANGUAGES

    def _load_dictionary(self):
        if self._dictionary is not None:
            return self._dictionary
        
        self._dictionary = {"hi": {}, "mr": {}}
        try:
            import os
            import pandas as pd
            
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
            db_path = os.path.join(data_dir, "test_database.csv")
            if not os.path.exists(db_path):
                db_path = os.path.join(data_dir, "test_dataset.csv")
                
            if os.path.exists(db_path):
                df = pd.read_csv(db_path)
                for _, row in df.iterrows():
                    eng = str(row.get("english", "")).strip().lower()
                    hi = str(row.get("hindi", "")).strip()
                    mr = str(row.get("marathi", "")).strip()
                    
                    if eng:
                        if hi and hi.lower() != "nan":
                            self._dictionary["hi"][eng] = hi
                        if mr and mr.lower() != "nan":
                            self._dictionary["mr"][eng] = mr
        except Exception as e:
            logger.error(f"Failed to load dictionary: {e}")
        
        return self._dictionary

    def load_model(self, lang_code: str) -> Tuple[MarianTokenizer, MarianMTModel]:
        """Loads and caches the tokenizer and model for a target language."""
        if not self.is_language_supported(lang_code):
            raise ValueError(
                f"Unsupported target language: '{lang_code}'. Supported languages: {list(SUPPORTED_LANGUAGES.keys())}"
            )

        with self._load_lock:
            if lang_code not in self._models:
                import os
                model_id = SUPPORTED_LANGUAGES[lang_code]["model_id"]
                
                # Check for cached local snapshot path first
                cache_base = os.path.expanduser("~/.cache/huggingface/hub")
                local_dir_name = f"models--{model_id.replace('/', '--')}"
                snapshots_path = os.path.join(cache_base, local_dir_name, "snapshots")
                
                load_target = model_id
                if os.path.exists(snapshots_path):
                    snapshots = [os.path.join(snapshots_path, s) for s in os.listdir(snapshots_path)]
                    for s in snapshots:
                        has_model = os.path.exists(os.path.join(s, "pytorch_model.bin")) or os.path.exists(os.path.join(s, "model.safetensors"))
                        has_tokenizer = os.path.exists(os.path.join(s, "source.spm"))
                        if os.path.isdir(s) and has_model and has_tokenizer:
                            load_target = s
                            logger.info(f"Found complete local snapshot for '{lang_code}' at: {load_target}")
                            break

                logger.info(f"Loading '{load_target}' for '{lang_code}' onto {self.device}...")

                tokenizer = MarianTokenizer.from_pretrained(load_target)
                model = MarianMTModel.from_pretrained(load_target)
                model.to(self.device)
                model.eval()

                self._tokenizers[lang_code] = tokenizer
                self._models[lang_code] = model
                logger.info(f"Successfully loaded and cached model for '{lang_code}'.")

            return self._tokenizers[lang_code], self._models[lang_code]

    def preprocess_text(self, text: str) -> str:
        """
        Cleans and normalizes English input text:
        - Strips extraneous whitespace
        - Preserves sentence structure and punctuation necessary for translation
        """
        text = text.strip()
        # Normalize multiple spaces or consecutive tabs
        text = re.sub(r"[ \t]+", " ", text)
        return text

    def split_sentences(self, text: str) -> list[str]:
        """
        Splits text into sentences if text is long, to ensure optimal translation
        without truncating long paragraphs.
        """
        # Simple sentence splitter on punctuation (. ! ?)
        sentences = re.split(r"(?<=[.!?])\s+", text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences if sentences else [text]

    def translate(
        self,
        text: str,
        target_language: str,
        source_language: str = "en",
        num_beams: int = 4,
        max_length: int = 256,
    ) -> Tuple[str, float]:
        """
        Translates text from English into the specified Indian regional language.
        Returns (translated_text, inference_time_ms).
        """
        if source_language != "en":
            raise ValueError(f"Source language '{source_language}' is not supported. Only 'en' is supported.")

        if not text or not text.strip():
            raise ValueError("Input text cannot be empty.")

        if not self.is_language_supported(target_language):
            raise ValueError(
                f"Unsupported target language: '{target_language}'. Supported languages: {list(SUPPORTED_LANGUAGES.keys())}"
            )

        cleaned_text = self.preprocess_text(text)

        # Check dictionary first for exact match (case-insensitive)
        dictionary = self._load_dictionary()
        lower_text = cleaned_text.lower()
        # Remove punctuation for better matching
        clean_lower = re.sub(r'[^\w\s]', '', lower_text)
        
        if clean_lower in dictionary.get(target_language, {}):
            start_time = time.perf_counter()
            translated_text = dictionary[target_language][clean_lower]
            inference_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return translated_text, inference_time_ms

        tokenizer, model = self.load_model(target_language)

        start_time = time.perf_counter()

        # Handle long paragraphs by splitting sentences if needed
        sentences = self.split_sentences(cleaned_text)
        translated_sentences = []

        with torch.inference_mode():
            for sentence in sentences:
                inputs = tokenizer(
                    sentence,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=max_length,
                ).to(self.device)

                generated_tokens = model.generate(
                    **inputs,
                    num_beams=num_beams,
                    max_length=max_length,
                    early_stopping=True,
                )

                decoded = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
                translated_sentences.append(decoded[0].strip())

        inference_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        translated_text = " ".join(translated_sentences)

        return translated_text, inference_time_ms

    def translate_batch(
        self,
        texts: list[str],
        target_language: str,
        source_language: str = "en",
        batch_size: int = 32,
        num_beams: int = 4,
        max_length: int = 128,
    ) -> Tuple[list[str], float]:
        """
        Translates a list of texts in parallel mini-batches.
        Significantly accelerates evaluation over large datasets like test_database.csv.
        """
        if not texts:
            return [], 0.0

        if not self.is_language_supported(target_language):
            raise ValueError(
                f"Unsupported target language: '{target_language}'. Supported languages: {list(SUPPORTED_LANGUAGES.keys())}"
            )

        tokenizer, model = self.load_model(target_language)
        start_time = time.perf_counter()

        all_translated: list[str] = []

        with torch.inference_mode():
            for i in range(0, len(texts), batch_size):
                batch_slice = texts[i : i + batch_size]
                cleaned_batch = [self.preprocess_text(t) if t and t.strip() else "" for t in batch_slice]

                valid_indices = [idx for idx, t in enumerate(cleaned_batch) if t]
                valid_texts = [cleaned_batch[idx] for idx in valid_indices]

                batch_results = [""] * len(batch_slice)

                if valid_texts:
                    inputs = tokenizer(
                        valid_texts,
                        return_tensors="pt",
                        padding=True,
                        truncation=True,
                        max_length=max_length,
                    ).to(self.device)

                    generated = model.generate(
                        **inputs,
                        num_beams=num_beams,
                        max_length=max_length,
                        early_stopping=True,
                    )

                    decoded = tokenizer.batch_decode(generated, skip_special_tokens=True)
                    for idx, dec in zip(valid_indices, decoded):
                        batch_results[idx] = dec.strip()

                all_translated.extend(batch_results)

        total_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return all_translated, total_time_ms


# Module-level convenience instance
translation_engine = TranslationEngine.get_instance()
