import requests
from bs4 import BeautifulSoup
import time
import random
from transformers import pipeline
from collections import Counter
import spacy
from gtts import gTTS
import os
from deep_translator import GoogleTranslator


def fetch_news_articles(company, max_articles=10):
    """
    Extracts news articles from BBC News with Title, Author, Full Content, and Metadata.

    Args:
        company (str): The company name to search for.
        max_articles (int): Number of articles to extract.

    Returns:
        list: A list of dictionaries containing article details.
    """

    base_url = f"https://www.bbc.co.uk/search?q={company.replace(' ', '%20')}"
    headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ]),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.bbc.co.uk/",
    }

    articles = []
    page_number = 1  # Start from the first page

    try:
        while len(articles) < max_articles:
            url = f"{base_url}&page={page_number}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Find all articles on the current page
            article_containers = soup.find_all("div", class_="ssrcss-1imfos9-PageStack e1k195vp1")

            if not article_containers:
                print(" No more articles found.")
                break  # Stop pagination if no more articles are found

            for result in article_containers:
                try:
                    # Extract Title and Link
                    title_tag = result.find("a", class_="ssrcss-1yagzb7-PromoLink exn3ah95")
                    if not title_tag:
                        continue  # Skip if title isn't found

                    title = title_tag.get_text(strip=True)
                    link = title_tag["href"] if title_tag else None

                    if not link.startswith("http"):
                        link = "https://www.bbc.co.uk" + link

                    # Fetch individual article content
                    article_response = requests.get(link, headers=headers)
                    article_soup = BeautifulSoup(article_response.text, "html.parser")

                    # Extract full content
                    content_div = article_soup.find("article", class_="ssrcss-15tkd6i-ArticleWrapper e1nh2i2l3")
                    full_content = " ".join([p.get_text(strip=True) for p in content_div.find_all("p")]) if content_div else "Content unavailable"

                    # Extract Date
                    date_tag = article_soup.find("time")
                    date = date_tag["datetime"] if date_tag else "Date unavailable"

                    # Add article data to the list
                    articles.append({
                        "title": title,
                        "url": link,
                        "date": date,
                        "content": full_content
                    })

                    if len(articles) >= max_articles:
                        break  # Stop if enough articles are collected

                except Exception as e:
                    print(f" Skipped article due to error: {e}")

            page_number += 1
            time.sleep(random.uniform(1, 3))  # Add delay to avoid detection

        if not articles:
            print(" No articles found. Try adjusting the search term or source.")

        return articles

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch articles: {e}"}


# Initialize pipelines
summarizer = pipeline("summarization", model="models/bart-large-cnn")
sentiment_analyzer = pipeline("sentiment-analysis", model="models/distilbert-base-uncased-finetuned-sst-2-english")


def summarize_article(content, max_length=130):
    """
    Summarizes the given article content using a transformer model.

    Args:
        content (str): The full text of the article.
        max_length (int): Maximum token length for the summary.

    Returns:
        str: The summarized content.
    """
    if len(content) < 50:
        return content  # Skip summarization for very short content

    try:
        summary = summarizer(content, max_length=max_length, min_length=50, do_sample=False)
        return summary[0]["summary_text"]
    except Exception as e:
        print(f" Summarization failed: {e}")
        return "Summary unavailable"


def analyze_sentiment(content):
    """
    Analyzes sentiment using a transformer model.

    Args:
        content (str): The text to analyze.

    Returns:
        str: Sentiment result (Positive, Negative, Neutral).
    """
    try:
        result = sentiment_analyzer(content[:500])  # Limit content for efficient analysis
        return result[0]["label"]
    except Exception as e:
        print(f" Sentiment analysis failed: {e}")
        return "Sentiment unavailable"


# Load the NLP model
nlp = spacy.load("en_core_web_sm")


def extract_topics(content):
    """
    Extracts key topics from the article using Named Entity Recognition (NER).

    Args:
        content (str): The text content of the article.

    Returns:
        list: A list of extracted topics.
    """
    doc = nlp(content)
    topics = set()

    # Extract named entities related to organizations, tech, and market
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT", "GPE"]:  # Organization, Product, Geopolitical Entity
            topics.add(ent.text)

    # If no topics found via NER, fallback to keyword-based matching
    if not topics:
        if "electric vehicle" in content.lower() or "EV" in content:
            topics.add("Electric Vehicles")
        if "stock market" in content.lower() or "shares" in content:
            topics.add("Stock Market")
        if "regulation" in content.lower() or "law" in content:
            topics.add("Regulations")
        if "autonomous" in content.lower() or "self-driving" in content:
            topics.add("Autonomous Vehicles")
    return list(topics)


def generate_impact_statement(article_1, article_2, common_topics, unique_1, unique_2):
    """
    Generates a dynamic impact statement based on sentiment and topic differences.

    Args:
        article_1 (dict): First article details.
        article_2 (dict): Second article details.
        common_topics (list): Common topics between both articles.
        unique_1 (list): Unique topics in article 1.
        unique_2 (list): Unique topics in article 2.

    Returns:
        str: A dynamically generated impact statement.
    """
    sentiment_1 = analyze_sentiment(article_1["content"])
    sentiment_2 = analyze_sentiment(article_2["content"])

    if sentiment_1 == "POSITIVE" and sentiment_2 == "NEGATIVE":
        return f"While \"{article_1['title']}\" presents an optimistic view, \"{article_2['title']}\" raises concerns, creating a mixed outlook."
    elif sentiment_1 == "NEGATIVE" and sentiment_2 == "POSITIVE":
        return f"\"{article_1['title']}\" highlights risks, while \"{article_2['title']}\" reassures investors with a positive narrative."
    elif sentiment_1 == "POSITIVE" and sentiment_2 == "POSITIVE":
        return "Both articles support a strong outlook for the company, reinforcing confidence in the market."
    elif sentiment_1 == "NEGATIVE" and sentiment_2 == "NEGATIVE":
        return "Both articles emphasize risks, signaling potential challenges ahead."
    else:
        return f"\"{article_1['title']}\" and \"{article_2['title']}\" cover different aspects, offering diverse perspectives on {', '.join(common_topics) if common_topics else 'various topics'}."


def comparative_sentiment_analysis(articles):
    """
    Performs comparative sentiment analysis on a list of articles.

    Args:
        articles (list): A list of dictionaries containing article details.

    Returns:
        dict: Structured JSON format with sentiment distribution and analysis.
    """
    sentiments = [analyze_sentiment(article['content']) for article in articles]
    sentiment_counts = Counter(sentiments)

    positive_count = sentiment_counts.get("POSITIVE", 0)
    negative_count = sentiment_counts.get("NEGATIVE", 0)
    neutral_count = sentiment_counts.get("NEUTRAL", 0)

    sentiment_summary = {
        "Sentiment Distribution": {
            "Positive": positive_count,
            "Negative": negative_count,
            "Neutral": neutral_count
        },
        "Coverage Differences": [],
        "Topic Overlap": {
            "Common Topics": [],
            "Unique Topics in Article 1": [],
            "Unique Topics in Article 2": []
        }
    }

    # Ensure at least two articles for comparison
    if len(articles) > 1:
        article_1_topics = extract_topics(articles[0]["content"])
        article_2_topics = extract_topics(articles[1]["content"])

        # Identify common & unique topics
        common_topics = list(set(article_1_topics) & set(article_2_topics))
        unique_article_1 = list(set(article_1_topics) - set(article_2_topics))
        unique_article_2 = list(set(article_2_topics) - set(article_1_topics))

        sentiment_summary["Coverage Differences"].append({
            "Comparison": f"Article 1 highlights '{articles[0]['title']}', while Article 2 discusses '{articles[1]['title']}'.",
            "Impact": generate_impact_statement(articles[0], articles[1], common_topics, unique_article_1, unique_article_2)
        })

        sentiment_summary["Coverage Differences"].append({
            "Comparison": f"Article 1 focuses on {', '.join(article_1_topics)}, whereas Article 2 is about {', '.join(article_2_topics)}.",
            "Impact": f"Common themes include {', '.join(common_topics) if common_topics else 'none'}, but Article 1 uniquely covers {', '.join(unique_article_1) if unique_article_1 else 'no additional topics'}, while Article 2 focuses on {', '.join(unique_article_2) if unique_article_2 else 'no additional topics'}."
        })

        sentiment_summary["Topic Overlap"] = {
            "Common Topics": common_topics,
            "Unique Topics in Article 1": unique_article_1,
            "Unique Topics in Article 2": unique_article_2
        }

    return sentiment_summary


def generate_final_sentiment_summary(articles, company):
    """
    Generates a dynamic final sentiment analysis based on sentiment distribution.

    Args:
        articles (list): A list of dictionaries containing article details.
        company (str): The name of the company.

    Returns:
        str: A dynamically generated sentiment summary.
    """
    sentiments = [analyze_sentiment(article['content']) for article in articles]
    sentiment_counts = Counter(sentiments)

    positive = sentiment_counts.get("POSITIVE", 0)
    negative = sentiment_counts.get("NEGATIVE", 0)
    neutral = sentiment_counts.get("NEUTRAL", 0)
    total = positive + negative + neutral

    if total == 0:
        return f"No sentiment analysis available for {company} at this time."

    if positive > negative and positive > neutral:
        return f"{company} is receiving mostly positive coverage, indicating potential investor confidence and growth opportunities."
    elif negative > positive and negative > neutral:
        return f"Recent news about {company} has been mostly negative, suggesting challenges that could impact its market position."
    elif neutral > positive and neutral > negative:
        return f"Coverage on {company} remains mostly neutral, reflecting a balanced perspective without strong positive or negative sentiment."
    else:
        return f"Mixed sentiment exists for {company}. Some reports highlight growth, while others raise concerns."


def text_to_speech_hindi(text, file_name="sentiment_summary.mp3"):
    """
    Converts the given text into Hindi speech using gTTS and saves it as an MP3 file.

    Args:
        text (str): The full sentiment analysis report.
        file_name (str): The name of the output audio file.

    Returns:
        str: The path of the saved MP3 file.
    """
    try:
        if not text or len(text.strip()) == 0:
            return None  # Skip TTS if text is empty

        tts = gTTS(text=text, lang="hi")  # Convert text to Hindi speech
        file_path = os.path.join("audio", file_name)

        # Ensure the "audio" directory exists
        os.makedirs("audio", exist_ok=True)
        tts.save(file_path)

        return file_path
    except Exception as e:
        print(f" TTS Conversion failed: {e}")
        return None


def generate_hindi_sentiment_summary(company, sentiment_analysis):
    """
    Generates a Hindi summary for the entire sentiment report.

    Args:
        company (str): The company name.
        sentiment_analysis (dict): The comparative sentiment analysis results.

    Returns:
        str: A Hindi text summary.
    """
    # Construct summary in English
    english_summary = f"Latest news summary for {company}:\n\n"

    # Sentiment Distribution
    english_summary += "Overall Sentiment Distribution:\n"
    english_summary += f"Positive News: {sentiment_analysis['Sentiment Distribution']['Positive']} articles\n"
    english_summary += f"Negative News: {sentiment_analysis['Sentiment Distribution']['Negative']} articles\n"
    english_summary += f"Neutral News: {sentiment_analysis['Sentiment Distribution']['Neutral']} articles\n\n"

    # Coverage Differences
    english_summary += "News Coverage Differences:\n"
    for diff in sentiment_analysis["Coverage Differences"]:
        english_summary += f"- {diff['Comparison']}.\n"
        english_summary += f"  Impact: {diff['Impact']}.\n\n"

    # Final Sentiment Analysis
    english_summary += f"Final Sentiment Analysis:\n{sentiment_analysis['Final Sentiment Analysis']}.\n"

    # Translate the entire summary to Hindi
    translator = GoogleTranslator(source="en", target="hi")
    hindi_summary = translator.translate(english_summary)

    return hindi_summary
