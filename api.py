from fastapi import FastAPI
from pydantic import BaseModel
from utils import (
    fetch_news_articles, summarize_article, analyze_sentiment,
    comparative_sentiment_analysis, extract_topics, generate_final_sentiment_summary,
    text_to_speech_hindi, generate_hindi_sentiment_summary
)

app = FastAPI()

# Request model for receiving company name
class CompanyRequest(BaseModel):
    company_name: str

@app.get("/")
def home():
    return {"message": "Welcome to the News Analyzer API"}

@app.post("/analyze-news/")
def analyze_news(request: CompanyRequest):
    """
    Fetches news articles, performs sentiment analysis, and generates a Hindi TTS summary.
    """
    company_name = request.company_name
    articles = fetch_news_articles(company_name, max_articles=10)

    if not articles:
        return {"error": "No articles found. Try another company name."}

    structured_articles = []
    for article in enumerate(articles):
        title = article["title"]
        summary = summarize_article(article["content"])
        sentiment = analyze_sentiment(article["content"])
        topics = extract_topics(article["content"])

        structured_articles.append({
            "Title": title,
            "Summary": summary,
            "Sentiment": sentiment,
            "Topics": topics
        })

    # Perform Comparative Sentiment Analysis
    sentiment_analysis_result = comparative_sentiment_analysis(articles)

    # Generate Final Sentiment Analysis
    final_sentiment = generate_final_sentiment_summary(articles, company_name)
    sentiment_analysis_result["Final Sentiment Analysis"] = final_sentiment

    # Generate Hindi Sentiment Report
    hindi_summary_text = generate_hindi_sentiment_summary(company_name, sentiment_analysis_result)

    # Convert Hindi Summary to Speech
    hindi_audio_path = text_to_speech_hindi(hindi_summary_text, "hindi_sentiment_summary.mp3")

    return {
        "Company": company_name,
        "Articles": structured_articles,
        "Comparative Sentiment Score": sentiment_analysis_result,
        "Final Sentiment Analysis": final_sentiment,
        "Hindi TTS": hindi_audio_path if hindi_audio_path else "TTS conversion failed"
    }
