from typing import List, Optional
from pydantic import BaseModel, Field


class TranslationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="English text to be translated")
    source_language: str = Field(default="en", description="Source language code (defaults to 'en')")
    target_language: str = Field(..., description="Target language code (e.g. 'hi', 'mr')")


class TranslationResponse(BaseModel):
    source_text: str
    translated_text: str
    source_language: str
    target_language: str
    inference_time_ms: Optional[float] = None


class EvaluationRequest(BaseModel):
    target_language: str = Field(default="hi", description="Target language code to evaluate ('hi' or 'mr')")
    limit: Optional[int] = Field(default=None, description="Optional maximum number of sentences/words to evaluate (defaults to all)")


class EvaluationSentenceResult(BaseModel):
    id: int
    source_text: str
    reference_text: str
    predicted_text: str
    sentence_bleu: float


class EvaluationResponse(BaseModel):
    target_language: str
    target_language_name: str
    dataset_name: Optional[str] = "test_database.csv"
    bleu_score: float
    num_sentences: int
    avg_inference_time_ms: float
    total_duration_seconds: Optional[float] = None
    score_distribution: Optional[dict] = None
    results: List[EvaluationSentenceResult]


class DatasetItem(BaseModel):
    id: int
    english: str
    hindi: str
    marathi: str


class DatasetInfoResponse(BaseModel):
    total_count: int
    dataset_name: str
    items: List[DatasetItem]


class LanguageInfo(BaseModel):
    code: str
    name: str
    native_name: str
    model_id: str

