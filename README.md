
# News Analyzer  

###  Overview  
The **News Analyzer** is a full-stack application that:  
- **Scrapes news articles** for a given company using BeautifulSoup.  
- **Performs summarization** on the extracted news articles.  
- **Analyzes sentiment** (Positive, Negative, Neutral) using NLP models.  
- **Generates Hindi text-to-speech (TTS) audio** summarizing the sentiment.  
- **Provides an interactive UI** using Gradio.  

 **Backend:** FastAPI | Transformers | BeautifulSoup | gTTS  
 **Frontend:** Gradio  

---

##  1. Project Setup (Installation & Running) 

###  Step 1: Clone the Repository  
```bash
git clone https://github.com/Harshad/News-Analyzer.git
cd news-analyzer
```

###  Step 2: Create a Virtual Environment  
```bash
python -m venv news_env
source news_env/bin/activate   # On macOS/Linux
news_env\Scripts\activate      # On Windows
```

###  Step 3: Install Dependencies  
```bash
pip install -r requirements.txt
```

###  Step 4: Run the Backend API  
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```
 **FastAPI will start running at:** `http://127.0.0.1:8000/docs`

###  Step 5: Run the Gradio Frontend  
```bash
python app.py
```
 **Gradio will start running at:** `http://127.0.0.1:7860`

---

##  2. Model Details  

The project uses the following models:

###  Summarization Model
- **Model:** `facebook/bart-large-cnn`
- **Purpose:** Extracts a concise summary of news articles.
- **Why Chosen?** It is pre-trained for text summarization and performs well on news data.

###  Sentiment Analysis Model
- **Model:** `distilbert-base-uncased-finetuned-sst-2-english`
- **Purpose:** Classifies news articles as **Positive, Negative, or Neutral.**
- **Why Chosen?** A lightweight and accurate sentiment analysis model from Hugging Face.

###  Text-to-Speech (TTS) Model
- **Model:** `gTTS (Google Text-to-Speech)`
- **Purpose:** Converts the summary into Hindi speech.
- **Why Chosen?** Supports Hindi and is lightweight for deployment.

---

##  3. API Development  

###  Backend API
The backend is built using **FastAPI** and provides the following endpoints:

#### **1 Analyze News API**
- **Endpoint:** `POST /analyze-news/`
- **Description:** Fetches news articles, summarizes them, performs sentiment analysis, and generates Hindi TTS.
- **Request Body:**
  ```json
  { "company_name": "Tesla" }
  ```
- **Response Example:**
  ```json
  {
    "Company": "Tesla",
    "Articles": [
      {
        "Title": "Tesla's New Model Breaks Sales Records",
        "Summary": "Tesla's latest EV sees record sales in Q3...",
        "Sentiment": "Positive",
        "Topics": ["Electric Vehicles", "Stock Market", "Innovation"]
      }
    ],
    "Hindi TTS": "tesla_summary.mp3"
  }
  ```
- **How to Access via Postman:**  
  - Open **Postman** and send a `POST` request to:  
    `http://127.0.0.1:8000/analyze-news/`  
  - Select **Body → raw → JSON** and enter:  
    ```json
    { "company_name": "Tesla" }
    ```

#### **2 Fetch Audio API**
- **Endpoint:** `GET /audio/{filename}`
- **Description:** Returns the generated Hindi TTS audio file.
- **Example Usage:**  
  ```
  http://127.0.0.1:8000/audio/tesla_summary.mp3
  ```

---

##  4. API Usage (Third-Party Integrations)  

| API/Library      | Purpose |
|-----------------|-----------------------------------------------------|
| **Hugging Face Transformers** | Used for text summarization and sentiment analysis. |
| **BeautifulSoup** | Scrapes news articles from `news.google.com`. |
| **Google TTS (gTTS)** | Converts the summary into Hindi speech. |
| **FastAPI** | Handles API requests. |
| **Gradio** | Provides a user-friendly web UI. |

---

##  5. Assumptions & Limitations  

###  Assumptions
- News articles are **scrapable via BeautifulSoup** (non-JS links).
- Sentiment analysis assumes **generalized polarity** (may not capture nuances).
- Hindi TTS **uses simple pronunciation** (not 100% natural like human speech).

###  Limitations
- **Speed:** Running on CPU can slow down processing.  
   **Solution:** Use a GPU when deploying on Hugging Face Spaces.  
- **Data Accuracy:** Summarization **may miss key details** in complex articles.  
   **Solution:** Use a fine-tuned summarization model for better accuracy.  
- **Storage Limit:** Hugging Face Spaces **limits free storage to 1GB.**  
   **Solution:** Download and store models locally instead of redownloading them.  

---

##  6. Deployment on Hugging Face Spaces  

###  Backend Deployment
 **1. Create a new Space on Hugging Face** (Select `Docker`).  
 **2. Push Backend Code to the Space:**
```bash
git add .
git commit -m "Deploying backend"
git push
```
 **3. Check the Logs & Restart if Needed.**

 **Backend URL Example:**  
```
https://Harshad712-news-analyzer-backend.hf.space/analyze-news/
```

###  Frontend Deployment
 **1. Create a separate Space for the frontend.**  
 **2. Modify `app.py` to point to the deployed backend URL.**  
 **3. Push Frontend Code to the Space:**
```bash
git add .
git commit -m "Deploying frontend"
git push
```
 **4 Access the UI via Hugging Face Spaces.**

 **Frontend URL Example:**  
```
https://Harshad712-news-analyzer-frontend.hf.space/
```

---

##  7. Future Improvements  
 **Improve Model Efficiency** → Use a more optimized model for summarization.  
 **Better UI/UX** → Add interactive visualizations in the Gradio frontend.  
 **Multi-language Support** → Extend to more Indian languages.  

##  8. License  
 MIT License - Free to use and modify.

---

