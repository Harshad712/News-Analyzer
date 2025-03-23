"""
FastAPI News Sentiment Analyzer API.

This API fetches news articles for a given company,
performs sentiment analysis,
generates a comparative sentiment analysis report,
and converts the summary into
Hindi speech.

Author: [Your Name]
"""

from fastapi import FastAPI
from pydantic import BaseModel
from utils import (
    fetch_news_articles,
    summarize_article,
    analyze_sentiment,
    comparative_sentiment_analysis,
    extract_topics,
    generate_hindi_sentiment_summary,
    text_to_speech_hindi
)

app = FastAPI()


class CompanyRequest(BaseModel):
    """
    Request model for receiving the company name as input.
    """
    company_name: str


@app.get("/")
def home():
    """
    Home route to check if the API is running.
    """
    return {"message": "Welcome to the News Analyzer API"}


@app.post("/analyze-news/")
def analyze_news(request: CompanyRequest):
    """
    Fetches news articles, performs sentiment analysis, and generates a Hindi TTS summary.

    Args:
        request (CompanyRequest): JSON request containing the company name.

    Returns:
        dict: A structured response containing:
            - Company name
            - List of articles with title, summary, sentiment, and topics
            - Comparative sentiment analysis results
            - Final sentiment summary
            - Hindi TTS audio file path
    """
    company_name = request.company_name
    articles = fetch_news_articles(company_name, max_articles=10)

    if not articles:
        return {"error": "No articles found. Try another company name."}

    structured_articles = []
    for article in articles:  # ✅ Removed incorrect enumerate()
        title = article["title"]
        summary = summarize_article(article["content"])
        sentiment = analyze_sentiment(article["content"])
        topics = extract_topics(article["content"])

        structured_articles.append(
            {
                "Title": title,
                "Summary": summary,
                "Sentiment": sentiment,
                "Topics": topics,
            }
        )

    # Perform Comparative Sentiment Analysis
    sentiment_analysis_result = comparative_sentiment_analysis(articles)

    # Generate Final Sentiment Analysis (Removed duplicate variable)
    sentiment_analysis_result["Final Sentiment Analysis"] = generate_hindi_sentiment_summary(
        company_name, sentiment_analysis_result
    )

    # Convert Hindi Summary to Speech
    hindi_audio_path = text_to_speech_hindi(
        sentiment_analysis_result["Final Sentiment Analysis"], "hindi_sentiment_summary.mp3"
    )

    return {
        "Company": company_name,
        "Articles": structured_articles,
        "Comparative Sentiment Score": sentiment_analysis_result,
        "Final Sentiment Analysis": sentiment_analysis_result["Final Sentiment Analysis"],
        "Hindi TTS": hindi_audio_path if hindi_audio_path else "TTS conversion failed",
    }
