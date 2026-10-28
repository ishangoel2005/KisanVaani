# KisanVaani - Multilingual Voice-First Agricultural Assistant

KisanVaani is a student-project prototype for agricultural information access. The interface starts in English and can switch to Hindi or Tamil. A user can type a question or record speech in English, Hindi or Tamil. The app transcribes speech, retrieves relevant material from a small curated agricultural knowledge base, asks an LLM to answer only from the retrieved material, displays source links and creates a spoken answer.

> **Safety and scope:** This is an educational prototype, not an official agricultural service. Its knowledge base is small and incomplete. Do not use it as the sole basis for pesticide, fertilizer, irrigation or disease-treatment decisions. Refer to your local Krishi Vigyan Kendra (KVK), agricultural university or agriculture department for location-specific guidance.

## 1. How the app works

1. The user chooses an interface language (English by default), a question language (auto-detect / English / Hindi / Tamil) and an answer language (same as question / English / Hindi / Tamil).
2. Typed text is used directly. Recorded audio is transcribed by Groq Whisper.
3. Hindi and Tamil questions are translated into an English search query by the LLM. English questions skip this translation call.
4. The local TF-IDF retrieval code finds the most relevant entries in `knowledge_base/agri_guides.json`.
5. The LLM is given only the question and retrieved source content and is instructed to cite sources as `[S1]`, `[S2]`, etc. If nothing sufficiently relevant is retrieved, the app uses a cautious fallback instead of asking the LLM to guess.
6. gTTS creates an MP3 in the selected response language and Streamlit displays the text, source links and audio player.

## 2. Folder structure

```text
KisanVaani/
├── app.py                         # Streamlit application / UI
├── requirements.txt               # Runtime Python packages
├── requirements-dev.txt           # Optional test packages
├── .env.example                   # Example environment file (no real key)
├── .gitignore                     # Keeps .env and secrets out of Git
├── README.md                      # This guide
├── .streamlit/
│   └── config.toml                # Theme and deployment config
├── knowledge_base/
│   └── agri_guides.json           # Curated facts and their source URLs
├── kisanvaani/
│   ├── __init__.py
│   ├── assistant.py               # Translation, RAG orchestration, grounded answer
│   ├── i18n.py                    # English, Hindi and Tamil UI text
│   ├── language.py                # Language/script helper functions
│   ├── rag.py                     # Local TF-IDF retrieval and source ranking
│   └── speech.py                  # Groq transcription and gTTS speech output
└── tests/
    └── test_rag.py                # Basic tests for retrieval and language detection
```

## 3. What you need

- Windows 10/11, macOS or Linux.
- Python **3.11 or 3.12** recommended for the least setup friction.
- An internet connection.
- A Groq API key for speech transcription and LLM answers. Check the current available models and any account/rate limits in your Groq console.
- A microphone and a recent browser for voice recording. Microphone access generally requires a secure browser context; localhost is supported by modern browsers.

The app does not train a model. The retrieval index is built locally from the included JSON knowledge base. Speech transcription and answer generation require network access and API usage. gTTS also requires an internet connection.

**Data handling:** When you use voice input, the recording is sent to Groq for transcription. Questions are sent to Groq for translation when needed and for answer generation. Answer text is sent to gTTS to create speech. Do not submit personal, confidential or sensitive information. Review each provider's current privacy terms and usage rules before deploying publicly. API usage may be subject to account limits or charges.

## 4. Get a Groq API key

1. Open <https://console.groq.com/keys> and sign in or create an account.
2. Create an API key and copy it somewhere safe temporarily.
3. Do not put the key directly in Python source code, GitHub, screenshots or a LinkedIn post.
4. If your console does not offer the model configured below, choose an available chat model and change `GROQ_CHAT_MODEL` in your local `.env` file. The speech model can similarly be changed with `GROQ_STT_MODEL`.

The starter project defaults to `openai/gpt-oss-20b` for chat and `whisper-large-v3-turbo` for transcription. Model availability may change; check the model list in your Groq console if you receive a model-not-found or access error.

## 5. Set up the project on Windows

### Step 1 - Extract the project

Download `KisanVaani_Source.zip` and extract it. You should see the `KisanVaani` folder containing `app.py`, `requirements.txt`, `kisanvaani` and `knowledge_base`.

### Step 2 - Open the project folder in VS Code

1. Install VS Code if needed.
2. In VS Code, choose **File → Open Folder** and select the extracted `KisanVaani` folder.
3. Open **Terminal → New Terminal**.
4. Confirm that the terminal is inside the `KisanVaani` folder. Run `dir`; `app.py` and `requirements.txt` should be listed.

### Step 3 - Create a virtual environment

In the VS Code PowerShell terminal, run these commands one at a time:

```powershell
py -3.11 -m venv .venv
```

If Python 3.11 is not installed but Python 3.12 is, use:

```powershell
py -3.12 -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use Command Prompt instead and run:

```bat
.venv\Scripts\activate.bat
```

Or, if permitted by your computer's security policy, allow activation only in the current PowerShell process with:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

When activated, the terminal prompt usually begins with `(.venv)`.

### Step 4 - Install packages

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

For running the test suite too:

```powershell
python -m pip install -r requirements-dev.txt
```

### Step 5 - Add your API key

In the VS Code Explorer, find `.env.example`, copy it and name the copy `.env` in the same top-level `KisanVaani` folder. Open `.env` and replace the placeholder with your real key:

```dotenv
GROQ_API_KEY=paste_your_real_key_here
GROQ_CHAT_MODEL=openai/gpt-oss-20b
GROQ_STT_MODEL=whisper-large-v3-turbo
```

Do not add quotation marks unless your provider specifically requires them. Save the file. Do not share `.env`; `.gitignore` is set up to exclude it.

### Step 6 - Run the app

In the same terminal, run:

```powershell
python -m streamlit run app.py
```

Streamlit normally opens a browser automatically. If it does not, the terminal will show a local URL similar to `http://localhost:8501`; copy that address into your browser.

To stop the app, return to the terminal and press `Ctrl+C`.

## 6. How to use the app

1. Leave **Interface language** as English to begin. Switch it to Hindi or Tamil to translate the user-facing labels.
2. In the sidebar, choose **Question language**. Start with **Auto-detect**; for best voice recognition, explicitly choose English, Hindi or Tamil before recording.
3. Choose **Answer language**. `Same as question` follows the detected or selected question language. You can override it, for example: ask in Tamil and choose English for the answer.
4. Select **Speak to KisanVaani**, record a short question, stop recording, then click **Transcribe and ask**. The recognised question, answer, audio and source links will appear below.
5. Alternatively, choose **Type your question**, enter a question and click **Ask KisanVaani**.
6. Check the source links and read the safety note. The first knowledge base covers general storage, soil testing, IPM, wheat irrigation and water-saving practices; it cannot answer every crop question.

Questions to try:

- `How can I reduce moisture and insect damage when storing grain?`
- `Why should I get my soil tested before applying fertiliser?`
- `What is integrated pest management?`
- `What should I consider when planning wheat irrigation?`
- `How can I reduce water loss from irrigation?`
- A question about football, a film or another unrelated subject - it should say the current agricultural knowledge base lacks enough evidence.

## 7. Run tests

With the virtual environment active, run:

```powershell
python -m pytest -q
```

The included tests check that the knowledge base loads, common agriculture questions retrieve relevant material, unrelated questions are not force-matched and Hindi/Tamil scripts are detected. These tests do not call the Groq API and do not test microphone or audio quality.

## 8. How to add more agricultural knowledge

Edit `knowledge_base/agri_guides.json`. Each list item should contain the following fields:

```json
{
  "id": "unique_short_id",
  "title": "Short source-backed topic title",
  "topics": ["keyword one", "keyword two", "crop name"],
  "content": "A concise and carefully checked summary of the source material.",
  "source_title": "Publisher or institution - page title",
  "source_url": "https://official-source.example/page"
}
```

Use a trustworthy source, ideally ICAR, a state agricultural university, a Government of India agricultural portal or a relevant KVK. Summarise rather than copying long passages. Do not add unsupported pesticide doses or universal irrigation schedules. After changing the knowledge base, restart the app so the cached retrieval index is rebuilt.

## 9. Deploy to Streamlit Community Cloud

1. Create a GitHub repository for the project.
2. Upload the source files, but **never upload `.env` or an API key**. The included `.gitignore` excludes `.env` and `.streamlit/secrets.toml`.
3. Open <https://share.streamlit.io/> and choose **Create app**.
4. Select your GitHub repository and branch; set the main file path to `app.py`.
5. In **Advanced settings → Secrets**, paste the following (with your real key):

```toml
GROQ_API_KEY = "paste_your_real_key_here"
GROQ_CHAT_MODEL = "openai/gpt-oss-20b"
GROQ_STT_MODEL = "whisper-large-v3-turbo"
```

6. Deploy, open the public app URL and test both typed and spoken questions from a phone and desktop.
7. Check the provider's current rate limits, billing and usage rules before sharing the link widely. Never expose the key in the app UI or repository.

Official Streamlit deployment documentation: <https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app>

## 10. Common issues

### `ModuleNotFoundError: No module named 'streamlit'`

Activate `.venv` in the project root and run `python -m pip install -r requirements.txt` again.

### `GROQ_API_KEY` missing

Check that the file is named exactly `.env`, is in the same folder as `app.py` and contains `GROQ_API_KEY=...`. Restart Streamlit after changing `.env`.

### Model not found / model access denied

Check your available models in the Groq console. Change the model in `.env` to a model your account can access. Restart the app.

### Speech transcription fails

Check the API key and network connection. Try choosing the spoken language explicitly in the sidebar. Record a shorter clip, speak clearly and keep background noise low. If voice fails, type the same question to continue testing the RAG and answer components.

### Browser does not record audio

Allow microphone access for the local Streamlit page. Try Chrome or Edge, reload the page and confirm that the correct microphone is selected in your operating system.

### Text answer works but no audio is played

The gTTS request requires an internet connection and may occasionally fail. The text answer remains usable. Check internet access and try again. gTTS is intended here as a convenient demo path; for a production application, replace it with a supported, officially provisioned text-to-speech service and review its terms and privacy requirements.

### It gives no answer to a valid question

The knowledge base is intentionally small. Try a question using the same topic terms as the source material, or add a relevant source-backed item to the JSON file. This retrieval system is lexical TF-IDF search, not a large semantic embedding model; it can miss paraphrases.

### It gives an answer that is not well supported

Do not trust it blindly. Check the source links. Improve the source entry, adjust the prompt or threshold and add a test case. In a real agricultural service, answers should be reviewed by agricultural domain experts and evaluated across regional languages and crops.

## 11. Current limitations and sensible next upgrades

- The curated source set is small and primarily written in English. Hindi/Tamil questions are translated to English for retrieval; generated answers are returned in the selected language.
- Script-based language detection cannot reliably identify Romanised Hindi or Tamil. Choose the question language explicitly for these cases.
- The retrieval uses word and character TF-IDF similarity. A later version could use multilingual sentence embeddings and a vector database, but that adds memory, setup and deployment complexity.
- The answer is not connected to live weather, live market prices, farm images, government schemes or the user's location.
- Voice quality, pronunciation, speech accuracy and latency must be tested with real English, Hindi and Tamil speakers. A language selector does not guarantee perfect recognition or pronunciation.
- For deployment beyond a student prototype, use officially supported speech services, protect user audio, add rate limits, monitor usage and consult agriculture experts to validate the knowledge base and safety behaviour.

## 12. Official sources used in the starter knowledge base

- Tamil Nadu Agricultural University (TNAU), storage structures: <https://agritech.tnau.ac.in/crop_protection/crop_prot_crop_insect_sto_sto%20str.html>
- TNAU, grain storage: <https://agritech.tnau.ac.in/crop_protection/crop_prot_crop_insect%20_storage_gra%20pro.html>
- Government of India, Soil Health Card FAQ: <https://soilhealth.dac.gov.in/files/FAQ_Final_English.pdf>
- TNAU, integrated pest management introduction: <https://agritech.tnau.ac.in/crop_protection/crop_prot_ipm_introduction.html>
- TNAU, wheat after-cultivation guidance: <https://agritech.tnau.ac.in/agriculture/agri_cropproduction_wheat_aftercultivation.html>
- TNAU, drip irrigation: <https://www.agritech.tnau.ac.in/agriculture/agri_irrigationmgt_dripirrigation.html>
- TNAU, good agricultural practices: <https://agritech.tnau.ac.in/gap_gmp_glp/gap_Agricultural%20compon.html>
