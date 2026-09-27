import logging
from contextlib import asynccontextmanager
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

import os
from evaluation import evaluate_model, load_dataset_records, resolve_dataset_path
from models import (
    DatasetInfoResponse,
    DatasetItem,
    EvaluationRequest,
    EvaluationResponse,
    LanguageInfo,
    TranslationRequest,
    TranslationResponse,
)
from translator import SUPPORTED_LANGUAGES, translation_engine

logger = logging.getLogger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Optional pre-warming can be logged or executed here
    logger.info("Starting English to Regional Language Translator API...")
    logger.info(f"Supported languages: {list(SUPPORTED_LANGUAGES.keys())}")
    yield
    logger.info("Shutting down Translator API...")


app = FastAPI(
    title="English to Regional Language Translator API",
    description="Machine Translation using NLP Transformer models (Helsinki-NLP MarianMT)",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local development (e.g. Vite on port 5173)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def health_check():
    """Returns basic API status and metadata."""
    return {
        "status": "healthy",
        "service": "English to Regional Language Translator",
        "device": translation_engine.device,
        "supported_languages": [
            {"code": code, "name": meta["name"], "native": meta["native_name"]}
            for code, meta in SUPPORTED_LANGUAGES.items()
        ],
    }


@app.get("/languages", response_model=List[LanguageInfo], tags=["Languages"])
def get_supported_languages():
    """Returns the list of currently supported target languages and models."""
    return [
        LanguageInfo(
            code=code,
            name=meta["name"],
            native_name=meta["native_name"],
            model_id=meta["model_id"],
        )
        for code, meta in SUPPORTED_LANGUAGES.items()
    ]


@app.post("/translate", response_model=TranslationResponse, tags=["Translation"])
def translate_text(payload: TranslationRequest):
    """
    Translates an English sentence or paragraph into a supported regional language (Hindi / Marathi).
    Validates input and ensures robust error handling.
    """
    cleaned_text = payload.text.strip() if payload.text else ""
    if not cleaned_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Input text cannot be empty. Please provide English text to translate.",
        )

    if len(cleaned_text) > 5000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Input text exceeds the maximum permitted length of 5000 characters.",
        )

    if payload.source_language.lower() != "en":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported source language '{payload.source_language}'. Only English ('en') is supported.",
        )

    target_lang = payload.target_language.lower()
    if not translation_engine.is_language_supported(target_lang):
        supported = ", ".join(SUPPORTED_LANGUAGES.keys())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported target language '{payload.target_language}'. Supported target languages: {supported}",
        )

    try:
        translated_text, inference_time_ms = translation_engine.translate(
            text=cleaned_text,
            target_language=target_lang,
            source_language=payload.source_language.lower(),
        )

        return TranslationResponse(
            source_text=cleaned_text,
            translated_text=translated_text,
            source_language=payload.source_language,
            target_language=target_lang,
            inference_time_ms=inference_time_ms,
        )
    except Exception as exc:
        logger.error(f"Translation error: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(exc)}",
        )


@app.get("/dataset", response_model=DatasetInfoResponse, tags=["Dataset"])
def get_dataset(limit: Optional[int] = None):
    """
    Returns the loaded test database records (including newly added words)
    along with dataset metadata and total count.
    """
    try:
        resolved_path = resolve_dataset_path()
        items_data = load_dataset_records(limit=limit)
        return DatasetInfoResponse(
            total_count=len(items_data),
            dataset_name=os.path.basename(resolved_path),
            items=[DatasetItem(**item) for item in items_data],
        )
    except Exception as exc:
        logger.error(f"Error fetching dataset: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load dataset: {str(exc)}",
        )


@app.post("/evaluate", response_model=EvaluationResponse, tags=["Evaluation"])
def evaluate_target_language(payload: EvaluationRequest):
    """
    Runs genuine BLEU score evaluation against the sample test dataset.
    Returns corpus BLEU score, average latency, and individual sentence comparisons.
    """
    target_lang = payload.target_language.lower()
    if not translation_engine.is_language_supported(target_lang):
        supported = ", ".join(SUPPORTED_LANGUAGES.keys())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported target language '{payload.target_language}'. Supported: {supported}",
        )

    try:
        results = evaluate_model(target_language=target_lang, limit=payload.limit)
        return EvaluationResponse(**results)
    except Exception as exc:
        logger.error(f"Evaluation error: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation failed: {str(exc)}",
        )


@app.get("/evaluate", response_model=EvaluationResponse, tags=["Evaluation"])
def evaluate_default(target_language: str = "hi", limit: Optional[int] = None):
    """GET convenience endpoint for running BLEU evaluation."""
    return evaluate_target_language(EvaluationRequest(target_language=target_language, limit=limit))

