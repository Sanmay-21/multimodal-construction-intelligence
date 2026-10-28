# Multimodal Construction Intelligence Platform
**Skill Wallet Capstone Project 1** — Streamlit prototype for site safety, crack triage, project estimates, and weather-aware construction guidance.

## Features
- Gemini multimodal analysis for uploaded JPG/PNG images, with a demonstration fallback.
- PPE checklist, hazard severity/remedies, score cards, and downloadable JSON report.
- Preliminary concrete/wall defect triage with limitations and next steps.
- Local planning calculations for budget, CapEx, indicative asset value, cement and steel.
- Conceptual architectural rendering prompt and Pollinations AI URL builder.
- Weather-aware site advisories and multi-turn assistant chat.
- No external database; state is held in the Streamlit session.

## Run locally
Python 3.10+ recommended.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit.

## Gemini API key
Enter a Google Gemini API key in the sidebar. For deployed apps, you may instead store it in Streamlit Secrets and adapt `app.py` to read `st.secrets`. Do not commit API keys to GitHub. Without a valid key, image modules use clearly labelled demonstration results and chat uses fallback guidance.

## Deploy to Streamlit Community Cloud
1. Push `app.py`, `requirements.txt`, and this README to a GitHub repository.
2. Create an app in Streamlit Community Cloud and select `app.py`.
3. Add secrets only through the deployment's Secrets settings if you choose to use them; never place secrets in source control.
4. Launch and test all tabs.

## Important limitations
This is a capstone prototype and not a certified safety inspection, structural diagnosis, quantity survey, or property valuation. Image-based PPE detection can miss obscured items. Crack width is not calibrated from a photo. The planning calculations use broad illustrative assumptions and must not be used as a bill of quantities or for procurement. OSHA and IS 456 are not interchangeable: IS 456 is a plain/reinforced concrete design code, not a PPE standard. Confirm site decisions with applicable local rules, project specifications, and qualified professionals.

## Architecture
Streamlit UI → Gemini multimodal / chat API (optional) → structured JSON and report display. Planning estimates run locally. No database is configured.
