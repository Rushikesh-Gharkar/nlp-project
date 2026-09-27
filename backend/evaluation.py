import argparse
import logging
import os
import sys
import time
from typing import Dict, List

import pandas as pd
import sacrebleu

# Allow importing from current directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from translator import SUPPORTED_LANGUAGES, translation_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("evaluation")

def resolve_dataset_path(custom_path: str = None) -> str:
    """Resolves dataset file, preferring custom_path, test_database.csv, or test_dataset.csv."""
    if custom_path and os.path.exists(custom_path):
        return custom_path

    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    for name in ["test_database.csv", "test_dataset.csv"]:
        candidate = os.path.join(data_dir, name)
        if os.path.exists(candidate):
            return candidate

    return os.path.join(data_dir, "test_dataset.csv")


DEFAULT_DATASET_PATH = resolve_dataset_path()


def load_dataset_records(dataset_path: str = None, limit: int = None) -> List[Dict]:
    """Loads all test records from the active CSV dataset."""
    path = resolve_dataset_path(dataset_path)
    if not os.path.exists(path):
        return []
    df = pd.read_csv(path)
    if limit and limit > 0:
        df = df.head(limit)
    records = []
    for idx, row in df.iterrows():
        records.append({
            "id": idx + 1,
            "english": str(row.get("english", "")).strip(),
            "hindi": str(row.get("hindi", "")).strip(),
            "marathi": str(row.get("marathi", "")).strip(),
        })
    return records


def evaluate_model(
    target_language: str = "hi",
    dataset_path: str = None,
    limit: int = None,
    batch_size: int = 32,
) -> Dict:
    """
    Evaluates the machine translation model on the test dataset.
    Uses batch translation for 10x-20x speedup across all sentences/words.
    Computes:
    - Corpus BLEU score (0 - 100) using SacreBLEU
    - Sentence-level BLEU scores
    - Latency benchmarks
    - Detailed prediction vs reference comparisons
    """
    actual_path = resolve_dataset_path(dataset_path)
    if not os.path.exists(actual_path):
        raise FileNotFoundError(f"Test dataset not found at: {actual_path}")

    if target_language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported target language: {target_language}")

    df = pd.read_csv(actual_path)

    # Column mapping
    lang_col_map = {
        "hi": "hindi",
        "mr": "marathi",
    }
    target_col = lang_col_map.get(target_language)
    if target_col not in df.columns or "english" not in df.columns:
        raise ValueError(f"Dataset must contain 'english' and '{target_col}' columns.")

    if limit and limit > 0:
        df = df.head(limit)

    sources = [str(s).strip() for s in df["english"].tolist()]
    references = [str(r).strip() for r in df[target_col].tolist()]

    logger.info(
        f"Running BLEU evaluation for '{target_language}' on {len(sources)} items from {os.path.basename(actual_path)}..."
    )

    eval_start_time = time.perf_counter()

    # High-speed batch inference
    predictions, batch_latency_ms = translation_engine.translate_batch(
        texts=sources,
        target_language=target_language,
        source_language="en",
        batch_size=batch_size,
    )

    total_duration_sec = round(time.perf_counter() - eval_start_time, 2)
    avg_latency = round(batch_latency_ms / len(sources), 2) if sources else 0.0

    sentence_results: List[Dict] = []
    score_distribution = {"high": 0, "medium": 0, "low": 0}

    for idx, (source, reference, pred) in enumerate(zip(sources, references, predictions)):
        sent_bleu = sacrebleu.sentence_bleu(pred, [reference]).score
        sent_bleu = round(sent_bleu, 2)

        if sent_bleu >= 40:
            score_distribution["high"] += 1
        elif sent_bleu >= 20:
            score_distribution["medium"] += 1
        else:
            score_distribution["low"] += 1

        sentence_results.append({
            "id": idx + 1,
            "source_text": source,
            "reference_text": reference,
            "predicted_text": pred,
            "sentence_bleu": sent_bleu,
        })

    # Corpus BLEU
    corpus_bleu = sacrebleu.corpus_bleu(predictions, [references]).score
    corpus_bleu_rounded = round(corpus_bleu, 2)

    logger.info(
        f"Evaluation complete. Corpus BLEU: {corpus_bleu_rounded}, Items: {len(sources)}, "
        f"Total Duration: {total_duration_sec}s, Avg Latency: {avg_latency} ms"
    )

    return {
        "target_language": target_language,
        "target_language_name": SUPPORTED_LANGUAGES[target_language]["name"],
        "dataset_name": os.path.basename(actual_path),
        "bleu_score": corpus_bleu_rounded,
        "num_sentences": len(sources),
        "avg_inference_time_ms": avg_latency,
        "total_duration_seconds": total_duration_sec,
        "score_distribution": score_distribution,
        "results": sentence_results,
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate English to Regional Language Translation Model via BLEU")
    parser.add_argument(
        "--lang",
        choices=list(SUPPORTED_LANGUAGES.keys()),
        default="hi",
        help="Target language code ('hi' for Hindi, 'mr' for Marathi)",
    )
    parser.add_argument(
        "--dataset",
        default=DEFAULT_DATASET_PATH,
        help="Path to evaluation CSV dataset",
    )
    args = parser.parse_args()

    print(f"=== Model Evaluation: English -> {SUPPORTED_LANGUAGES[args.lang]['name']} ===")
    results = evaluate_model(target_language=args.lang, dataset_path=args.dataset)

    print("\n--- Summary Metrics ---")
    print(f"Target Language: {results['target_language_name']} ({results['target_language']})")
    print(f"Total Sentences: {results['num_sentences']}")
    print(f"Corpus BLEU Score: {results['bleu_score']} / 100")
    print(f"Average Inference Latency: {results['avg_inference_time_ms']} ms/sentence")

    print("\n--- Detailed Sentence Comparison ---")
    for item in results["results"]:
        print(f"[{item['id']}] English:   {item['source_text']}")
        print(f"    Predicted: {item['predicted_text']}")
        print(f"    Reference: {item['reference_text']}")
        print(f"    BLEU:      {item['sentence_bleu']}")
        print("-" * 50)


if __name__ == "__main__":
    main()
