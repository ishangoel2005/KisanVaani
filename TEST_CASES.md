# KisanVaani — Manual Test Plan

Use this file during the demo and when collecting evidence for the project submission. Outputs from an LLM can vary, so the expected results below describe what the app should do, not a verbatim sentence.

| ID | Input / action | Expected behaviour | Evidence to capture |
|---|---|---|---|
| TC-01 | Type: `How can I reduce moisture and insect damage when storing grain?` Set answer language to English. | Gives a concise answer about cleaning/drying/storage checks; shows one or more TNAU source links. | Screenshot of question, answer and sources. |
| TC-02 | Type: `Why should I test soil before applying fertilizer?` | Retrieves Soil Health Card guidance and advises following test-based recommendations instead of guessing a dose. | Screenshot of answer with Government of India source. |
| TC-03 | Type: `What is integrated pest management?` | Explains monitoring and combining appropriate methods; avoids inventing pesticide names or doses. | Screenshot of answer and TNAU IPM source. |
| TC-04 | Speak an English question about grain storage; keep question language set to English. | Shows recognised speech, then an answer, sources and English audio playback. | Screenshot of recognised speech and answer/audio. |
| TC-05 | Speak a Hindi question; select Hindi in the question-language selector and `Same as question` for answer language. | Attempts Hindi transcription, Hindi answer and Hindi audio. Check recognition and pronunciation manually. | Screenshot of Hindi transcript and answer. |
| TC-06 | Speak a Tamil question; select Tamil in the question-language selector and `Same as question` for answer language. | Attempts Tamil transcription, Tamil answer and Tamil audio. Check recognition and pronunciation manually. | Screenshot of Tamil transcript and answer. |
| TC-07 | Type a Hindi or Tamil question in its native script and set the answer language to English. | Translates the question for retrieval and returns an English answer with the retrieved source links. | Screenshot showing original-language question and English answer. |
| TC-08 | Switch the interface language to Hindi, then Tamil. | Most app labels and instructions change; response-language selection continues to work independently. | One screenshot for Hindi UI and one for Tamil UI. |
| TC-09 | Ask: `Who won the football world cup in 1998?` | Does not force-match an agriculture source. Displays a message that the current agricultural knowledge base lacks sufficient evidence. | Screenshot of fallback message and no-source state. |
| TC-10 | Temporarily remove or rename the API key in a local test copy and submit a question. Restore it after the test. | App displays a setup error, without crashing. | Screenshot only if useful; never show the API key. |
| TC-11 | Disconnect the internet and attempt to generate an answer or speech. Reconnect after testing. | Text/API requests or gTTS may fail; the app should show an error instead of silently claiming success. | Optional screenshot of the error state. |
| TC-12 | Run `python -m pytest -q` in the project environment. | All local retrieval/language tests pass. | Screenshot of terminal showing the passing test count. |

## Demonstration notes

- Use a quiet room and short spoken questions. Voice accuracy varies with accent, microphone quality and background noise.
- For Romanised Hindi/Tamil (typed with English letters), explicitly select the question language because simple script detection cannot infer it reliably.
- Confirm that the source links open and support the answer. The knowledge base is intentionally small, so it will not cover all farm situations.
- Do not use real personal information or confidential audio in public demos.
