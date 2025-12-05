ADDITIONALS = [
    "id",
    "distance",
    "certainty",
    "score",
    "explain_score"
]

FUSION_TYPES = ["relative", "ranked"]

LIMIT_MIN_VALUE = 1
LIMIT_MAX_VALUE = 100000
LIMIT_DEFAULT_VALUE = 200

DEFAULT_ALPHA = 0.6
DEFAULT_WITH_ADDITIONAL = ["score"]
DEFAULT_FUSION = "ranked"
DEFAULT_LIMIT = 50

# Search types available
# Based on Weaviate documentation:
# - BM25 keyword search is built into Weaviate, no external API needed
# - near_text requires vectorizer (text2vec-openai/google) which needs LLM API key
# - hybrid combines BM25 + vector search, so needs LLM API key for vector component
SEARCH_TYPES = {
    "keyword": {"label": "🔤 Keyword Search (BM25)", "needs_llm": False},
    "near_text": {"label": "📝 Near Text (Semantic)", "needs_llm": True},
    "hybrid": {"label": "🔀 Hybrid Search", "needs_llm": True}
}

SEARCH_TYPES_LIST = list(SEARCH_TYPES.keys())
DEFAULT_SEARCH_TYPE = "keyword"
