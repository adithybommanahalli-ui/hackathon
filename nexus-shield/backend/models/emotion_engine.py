"""
Emotion Engine - Social Pulse & Sentiment Analysis
Uses HuggingFace transformers for sentiment + fake news detection
"""
import os
import random
import requests
from typing import Dict, List, Optional

# Lazy-load transformers to avoid slow startup
_sentiment_pipeline = None
_fake_news_pipeline = None

NEWS_API_KEY = os.environ.get("NEWSAPI_KEY", "YOUR_NEWSAPI_KEY")

SAMPLE_HEADLINES = [
    "Global markets surge as tech stocks hit record highs",
    "Cybersecurity breach exposes millions of user records",
    "Scientists warn of unprecedented climate tipping points",
    "Government announces emergency economic relief package",
    "Protests erupt in major cities over new surveillance laws",
    "AI systems now outperform humans in complex reasoning tasks",
    "Critical infrastructure attack disrupts power grid in three states",
    "Social media platforms accused of amplifying misinformation",
    "New malware strain targets banking systems worldwide",
    "Public trust in institutions hits historic low, survey finds",
    "Hackers claim responsibility for hospital network shutdown",
    "Disinformation campaign linked to foreign state actors uncovered",
    "Emergency services overwhelmed as cyber attack cripples 911 systems",
    "Stock market flash crash triggered by algorithmic trading anomaly",
    "Whistleblower reveals mass data collection by tech giants",
]


def get_sentiment_pipeline():
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        try:
            from transformers import pipeline
            print("[Emotion] Loading sentiment model...")
            _sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                top_k=None,
            )
            print("[Emotion] Sentiment model loaded.")
        except Exception as e:
            print(f"[Emotion] Failed to load sentiment model: {e}")
            _sentiment_pipeline = "fallback"
    return _sentiment_pipeline


def get_fake_news_pipeline():
    global _fake_news_pipeline
    if _fake_news_pipeline is None:
        try:
            from transformers import pipeline
            print("[Emotion] Loading fake news model...")
            _fake_news_pipeline = pipeline(
                "text-classification",
                model="mrm8488/bert-tiny-finetuned-fake-news",
            )
            print("[Emotion] Fake news model loaded.")
        except Exception as e:
            print(f"[Emotion] Failed to load fake news model: {e}")
            _fake_news_pipeline = "fallback"
    return _fake_news_pipeline


def fetch_headlines(topic: str, count: int = 10) -> List[str]:
    """Fetch headlines from NewsAPI or fall back to samples."""
    if NEWS_API_KEY == "YOUR_NEWSAPI_KEY":
        # Return shuffled sample headlines
        shuffled = SAMPLE_HEADLINES.copy()
        random.shuffle(shuffled)
        return shuffled[:count]

    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": topic,
            "pageSize": count,
            "sortBy": "publishedAt",
            "apiKey": NEWS_API_KEY,
            "language": "en",
        }
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json()
        if data.get("status") == "ok":
            articles = data.get("articles", [])
            return [a["title"] for a in articles if a.get("title")][:count]
    except Exception as e:
        print(f"[Emotion] NewsAPI error: {e}")

    # Fallback
    shuffled = SAMPLE_HEADLINES.copy()
    random.shuffle(shuffled)
    return shuffled[:count]


def analyze_sentiment(texts: List[str]) -> Dict:
    """Run sentiment analysis on a list of texts."""
    pipeline = get_sentiment_pipeline()

    if pipeline == "fallback" or pipeline is None:
        # Simulate sentiment scores
        return _simulate_sentiment(texts)

    try:
        results = pipeline(texts, truncation=True, max_length=128)
        emotion_totals = {"positive": 0.0, "neutral": 0.0, "negative": 0.0}
        count = len(results)

        for result in results:
            for item in result:
                label = item["label"].lower()
                score = item["score"]
                if "pos" in label:
                    emotion_totals["positive"] += score
                elif "neu" in label:
                    emotion_totals["neutral"] += score
                else:
                    emotion_totals["negative"] += score

        # Normalize
        total = sum(emotion_totals.values()) or 1
        normalized = {k: round(v / total, 3) for k, v in emotion_totals.items()}

        # Split negative into angry/fear
        neg = normalized["negative"]
        angry = round(neg * 0.55, 3)
        fear = round(neg * 0.45, 3)

        return {
            "positive": normalized["positive"],
            "neutral": normalized["neutral"],
            "angry": angry,
            "fear": fear,
            "raw_negative": neg,
        }
    except Exception as e:
        print(f"[Emotion] Sentiment analysis error: {e}")
        return _simulate_sentiment(texts)


def analyze_fake_news(texts: List[str]) -> Dict:
    """Run fake news detection on a list of texts."""
    pipeline = get_fake_news_pipeline()

    if pipeline == "fallback" or pipeline is None:
        return _simulate_fake_news(texts)

    try:
        results = pipeline(texts, truncation=True, max_length=128)
        fake_count = sum(
            1 for r in results if r["label"].upper() in ("FAKE", "LABEL_1", "1")
        )
        fake_ratio = round(fake_count / len(texts), 3) if texts else 0
        return {
            "fake_count": fake_count,
            "real_count": len(texts) - fake_count,
            "fake_ratio": fake_ratio,
            "per_headline": [
                {
                    "text": t[:80],
                    "label": r["label"],
                    "confidence": round(r["score"], 3),
                }
                for t, r in zip(texts, results)
            ],
        }
    except Exception as e:
        print(f"[Emotion] Fake news analysis error: {e}")
        return _simulate_fake_news(texts)


def _simulate_sentiment(texts: List[str]) -> Dict:
    """Fallback simulated sentiment when model unavailable."""
    # Keyword-based heuristic
    angry_words = ["attack", "breach", "hack", "crisis", "protest", "crash", "cripple", "overwhelm"]
    fear_words = ["warn", "threat", "danger", "emergency", "unprecedented", "shutdown"]
    positive_words = ["surge", "record", "relief", "outperform", "high"]

    angry = 0.0
    fear = 0.0
    positive = 0.0

    for text in texts:
        t = text.lower()
        angry += sum(1 for w in angry_words if w in t)
        fear += sum(1 for w in fear_words if w in t)
        positive += sum(1 for w in positive_words if w in t)

    total = angry + fear + positive + len(texts) * 0.3  # neutral baseline
    neutral = max(0, len(texts) * 0.3)

    grand = angry + fear + positive + neutral or 1
    return {
        "positive": round(positive / grand, 3),
        "neutral": round(neutral / grand, 3),
        "angry": round(angry / grand, 3),
        "fear": round(fear / grand, 3),
        "raw_negative": round((angry + fear) / grand, 3),
    }


def _simulate_fake_news(texts: List[str]) -> Dict:
    """Fallback simulated fake news detection."""
    fake_keywords = ["claim", "allegedly", "sources say", "rumor", "unconfirmed", "whistleblower"]
    fake_count = sum(
        1 for t in texts if any(kw in t.lower() for kw in fake_keywords)
    )
    # Add some randomness
    import random
    extra = random.randint(0, max(1, len(texts) // 4))
    fake_count = min(fake_count + extra, len(texts))
    fake_ratio = round(fake_count / len(texts), 3) if texts else 0

    return {
        "fake_count": fake_count,
        "real_count": len(texts) - fake_count,
        "fake_ratio": fake_ratio,
        "per_headline": [
            {
                "text": t[:80],
                "label": "FAKE" if i < fake_count else "REAL",
                "confidence": round(random.uniform(0.6, 0.95), 3),
            }
            for i, t in enumerate(texts)
        ],
    }


class EmotionEngine:
    def __init__(self):
        pass

    def analyze(self, topic: str) -> Dict:
        """Full social analysis pipeline."""
        headlines = fetch_headlines(topic, count=10)
        sentiment = analyze_sentiment(headlines)
        fake_news = analyze_fake_news(headlines)

        # Bot activity simulation (heuristic)
        import random
        bot_activity = round(random.uniform(0.05, 0.35), 3)

        return {
            "topic": topic,
            "headlines": headlines[:5],
            "sentiment": sentiment,
            "fake_news": fake_news,
            "bot_activity": bot_activity,
            "emotion_anger_level": sentiment["angry"] + sentiment["fear"] * 0.5,
        }
