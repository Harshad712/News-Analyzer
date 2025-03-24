import gradio as gr
import requests

# Backend API URL (Replace with your actual Hugging Face backend URL or with your local backend URL)
BACKEND_URL = "https://Harshad712-news-analyzer-backend.hf.space/analyze-news/"


def analyze_news(company_name):
    """Fetch and analyze news articles for the given company."""
    response = requests.post(BACKEND_URL, json={"company_name": company_name})

    if response.status_code == 200:
        data = response.json()

        # Extract Hindi TTS URL
        audio_url = data.get("Hindi TTS", "")

        # If an audio file is available, return it in Gradio format
        if audio_url and "http" in audio_url:
            return data, audio_url
        else:
            return data, None
    else:
        return {"error": f"Failed to fetch data. Status Code: {response.status_code}"}, None


# Gradio UI
with gr.Blocks() as app:
    gr.Markdown("# 📰 News Sentiment Analyzer")
    company_input = gr.Textbox(label="Enter Company Name", placeholder="e.g., Tesla")
    analyze_button = gr.Button("Analyze News")
    output_box = gr.JSON(label="Analysis Result")
    audio_output = gr.Audio(label="Hindi Audio")

    analyze_button.click(analyze_news, inputs=company_input, outputs=[output_box, audio_output])

# Launch Gradio app
app.launch()
