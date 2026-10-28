import json
import os
import re
from datetime import datetime
from typing import Any, Dict, List

import streamlit as st
from PIL import Image

try:
    import google.generativeai as genai
except Exception:
    genai = None

APP_NAME = "Multimodal Construction Intelligence Platform"
SEVERITIES = ["Low", "Medium", "High", "Critical"]

st.set_page_config(page_title=APP_NAME, page_icon="🏗️", layout="wide", initial_sidebar_state="expanded")

# ---------------------------- Styling ---------------------------------------
st.markdown("""
<style>
:root { --ink:#172033; --muted:#667085; --brand:#f59e0b; --panel:#ffffff; }
.stApp { background: linear-gradient(180deg,#f7f9fc 0%,#eef2f7 100%); color:var(--ink); }
.block-container { padding-top:1.5rem; max-width:1450px; }
.hero { padding:1.5rem 1.7rem; border-radius:20px; color:white;
        background:linear-gradient(115deg,#111827,#26364d 65%,#8b5e14);
        box-shadow:0 12px 30px rgba(16,24,40,.12); margin-bottom:1rem; }
.hero h1 { font-size:2rem; margin:0 0 .4rem 0; }
.hero p { margin:0; color:#e5e7eb; }
.panel { background:white; padding:1.1rem 1.2rem; border:1px solid #e5eaf1;
         border-radius:16px; box-shadow:0 5px 18px rgba(16,24,40,.04); margin-bottom:.8rem; }
.pill { display:inline-block; padding:.25rem .7rem; border-radius:99px; font-size:.82rem;
        font-weight:700; margin:.1rem; }
.pill-green { background:#dcfce7; color:#166534; }
.pill-amber { background:#fef3c7; color:#92400e; }
.pill-red { background:#fee2e2; color:#991b1b; }
.pill-blue { background:#dbeafe; color:#1e40af; }
.small-muted { color:#667085; font-size:.9rem; }
div[data-testid="stMetric"] { background:white; padding:1rem; border:1px solid #e5eaf1; border-radius:14px; }
section[data-testid="stSidebar"] { background:#111827; }
section[data-testid="stSidebar"] * { color:#f9fafb; }
.stButton>button { border-radius:10px; font-weight:650; }
</style>
""", unsafe_allow_html=True)

def pill(text: str, kind: str = "blue") -> str:
    return f'<span class="pill pill-{kind}">{text}</span>'

def get_gemini_model(api_key: str):
    if not api_key or not genai:
        return None
    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel("gemini-1.5-flash")
    except Exception:
        return None

def extract_json(text: str) -> Dict[str, Any]:
    """Parse JSON from a model response, including fenced JSON."""
    cleaned = re.sub(r"^```(?:json)?|```$", "", (text or "").strip(), flags=re.MULTILINE).strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start >= 0 and end > start:
        cleaned = cleaned[start:end + 1]
    return json.loads(cleaned)

def gemini_json(prompt: str, image: Image.Image, api_key: str) -> Dict[str, Any]:
    model = get_gemini_model(api_key)
    if not model:
        raise RuntimeError("Gemini is unavailable or no API key was supplied.")
    response = model.generate_content([prompt, image], generation_config={"response_mime_type": "application/json", "temperature": 0.2})
    return extract_json(response.text)

def gemini_chat(messages: List[Dict[str, str]], api_key: str) -> str:
    model = get_gemini_model(api_key)
    if not model:
        return "Demonstration mode: add a Gemini API key in the sidebar to enable AI-generated answers. In the meantime, follow your approved method statements, site safety plan, and instructions from the responsible engineer."
    try:
        history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in messages[:-1]]
        chat = model.start_chat(history=history)
        return chat.send_message(messages[-1]["content"]).text
    except Exception as exc:
        return f"I couldn't reach Gemini right now ({type(exc).__name__}). Check the API key and connection, or use the demonstration guidance below."

def safety_demo() -> Dict[str, Any]:
    return {
        "safety_score": 78,
        "overall_status": "Needs Attention",
        "ppe_detection": {
            "hard_hat": {"detected": True, "notes": "Helmet appears visible; confirm correct fit and chin strap where required."},
            "high_visibility_vest": {"detected": True, "notes": "High-visibility garment appears present."},
            "steel_toe_boots": {"detected": False, "notes": "Footwear compliance cannot be confirmed from this image."},
            "safety_harness": {"detected": None, "notes": "Harness is task- and height-dependent; verify against site fall-protection plan."}
        },
        "hazards": [
            {"hazard": "Unverified protective footwear", "severity": "Medium", "remedy": "Verify safety footwear before access to the active work zone."},
            {"hazard": "Potentially unprotected work-at-height activity", "severity": "High", "remedy": "If work at height is occurring, provide compliant fall protection and inspect anchorages before work."}
        ],
        "limitations": "Demonstration data only; not an actual assessment of the uploaded image."
    }

def crack_demo() -> Dict[str, Any]:
    return {
        "defect_type": "Hairline",
        "estimated_crack_width_mm": 0.3,
        "confidence": "Low (demonstration)",
        "root_causes": ["Could be drying shrinkage or a surface finish issue; image alone cannot establish cause."],
        "recommended_repairs": ["Map and monitor the crack; measure width with a crack gauge.", "Refer to a qualified structural engineer if it grows, leaks, or is near a support."],
        "urgency": "Routine inspection",
        "limitations": "Demonstration data only; width and diagnosis are not measured from the uploaded image."
    }

def inr(value: float) -> str:
    if value >= 1e7:
        return f"₹{value/1e7:.2f} Cr"
    if value >= 1e5:
        return f"₹{value/1e5:.2f} L"
    return f"₹{value:,.0f}"

def safe_download_json(data: Dict[str, Any], filename: str):
    st.download_button("⬇️ Download JSON report", json.dumps(data, indent=2, ensure_ascii=False), file_name=filename, mime="application/json", use_container_width=True)

# ---------------------------- Sidebar ---------------------------------------
with st.sidebar:
    st.markdown("## 🏗️ Site Intelligence")
    st.caption("Skill Wallet Capstone Project 1")
    api_key = st.text_input("Google Gemini API key", type="password", help="Used only for this app session. Prefer Streamlit Secrets for deployed projects.")
    if api_key:
        st.success("API key entered for this session")
    else:
        st.info("Demonstration mode is active")
    st.markdown("---")
    st.markdown("### Architecture")
    st.markdown("**Streamlit UI** → **Gemini multimodal API** → structured JSON → report & metrics")
    st.markdown("- No external database")
    st.markdown("- Session-only chat history")
    st.markdown("- Local calculations for valuation")
    st.markdown("---")
    st.markdown("### Navigation")
    st.caption("Use the four tabs in the main workspace.")
    st.markdown("---")
    st.caption("Engineering outputs are decision support, not certified inspections, designs, or legal compliance determinations.")

st.markdown(f"""
<div class="hero">
  <h1>🏗️ {APP_NAME}</h1>
  <p>Multimodal site safety • Concrete diagnostics • Project valuation • Weather-aware site assistant</p>
</div>
""", unsafe_allow_html=True)

tab_safety, tab_cracks, tab_planning, tab_assistant = st.tabs([
    "🦺 Site Safety & PPE Audit", "🧱 Crack Diagnostics", "📐 Planning & Valuation", "🌦️ Daily Site Assistant"
])

# ---------------------------- Tab 1 -----------------------------------------
with tab_safety:
    st.subheader("Site Safety & PPE Audit")
    st.write("Upload a site photo to produce a structured, image-informed checklist. Confirm findings onsite.")
    uploaded = st.file_uploader("Construction site photo (JPG / PNG)", type=["jpg", "jpeg", "png"], key="safety_img")
    if uploaded:
        try:
            img = Image.open(uploaded).convert("RGB")
            c1, c2 = st.columns([1, 1.2], gap="large")
            with c1:
                st.image(img, caption="Uploaded site image", use_container_width=True)
            with c2:
                st.markdown('<div class="panel">**Assessment scope**<br>Helmet • high-vis vest • safety footwear • fall protection • visible hazards</div>', unsafe_allow_html=True)
                if st.button("🔎 Analyze PPE & hazards", key="run_safety", type="primary", use_container_width=True):
                    prompt = """Act as a cautious construction-site safety assistant. Inspect the provided image and return ONLY valid JSON with keys:
safety_score (integer 0-100), overall_status (Compliant / Needs Attention / Unsafe / Unable to Determine),
ppe_detection (object with hard_hat, high_visibility_vest, steel_toe_boots, safety_harness; each has detected true/false/null and notes),
hazards (array of objects hazard, severity exactly Low/Medium/High/Critical, remedy),
limitations (string).
Do not claim certainty where the image cannot show details. Mark unknown items null. Consider relevant OSHA workplace safety principles and Indian construction context; IS 456 is a concrete design code, not a PPE standard, so do not claim it defines PPE requirements. Never assert legal compliance from a photo alone. Be concise."""
                    with st.spinner("Reviewing image…"):
                        try:
                            result = gemini_json(prompt, img, api_key)
                            st.session_state["safety_result"] = result
                            st.session_state["safety_demo"] = False
                        except Exception:
                            st.session_state["safety_result"] = safety_demo()
                            st.session_state["safety_demo"] = True
            result = st.session_state.get("safety_result")
            if result:
                if st.session_state.get("safety_demo"):
                    st.warning("Demonstration result shown. Add a valid Gemini API key to analyze uploaded images.")
                score = max(0, min(100, int(result.get("safety_score", 0))))
                m1, m2, m3 = st.columns(3)
                m1.metric("Safety score", f"{score}/100")
                m2.metric("Overall status", str(result.get("overall_status", "Unknown")))
                m3.metric("Hazards identified", len(result.get("hazards", [])))
                st.progress(score / 100)
                st.markdown("#### PPE checklist")
                ppe = result.get("ppe_detection", {})
                cols = st.columns(4)
                for col, (key, label) in zip(cols, [("hard_hat","Hard hat"),("high_visibility_vest","High-vis vest"),("steel_toe_boots","Safety boots"),("safety_harness","Harness")]):
                    item = ppe.get(key, {}) if isinstance(ppe, dict) else {}
                    detected = item.get("detected", None) if isinstance(item, dict) else None
                    status = "Visible" if detected is True else ("Not visible" if detected is False else "Unknown")
                    kind = "green" if detected is True else ("red" if detected is False else "amber")
                    col.markdown(f"**{label}**<br>{pill(status, kind)}", unsafe_allow_html=True)
                    if isinstance(item, dict) and item.get("notes"):
                        col.caption(item["notes"])
                st.markdown("#### Hazards & corrective actions")
                hazards = result.get("hazards", [])
                if hazards:
                    for h in hazards:
                        sev = h.get("severity", "Medium")
                        kind = "red" if sev in ("High", "Critical") else ("amber" if sev == "Medium" else "green")
                        with st.expander(f"{h.get('hazard','Hazard')} — {sev}"):
                            st.markdown(pill(sev, kind), unsafe_allow_html=True)
                            st.write(h.get("remedy", "Have a competent person review this hazard."))
                else:
                    st.success("No hazards were returned; this does not prove the site is hazard-free.")
                if result.get("limitations"):
                    st.caption(result["limitations"])
                safe_download_json(result, "site_safety_audit.json")
        except Exception as exc:
            st.error(f"Unable to read image: {exc}")
    else:
        st.info("Upload a JPG or PNG image to begin.")

# ---------------------------- Tab 2 -----------------------------------------
with tab_cracks:
    st.subheader("Crack Diagnostics & Structural Integrity")
    st.write("Image-based preliminary triage for concrete and wall surfaces.")
    crack_file = st.file_uploader("Concrete / wall surface image (JPG / PNG)", type=["jpg", "jpeg", "png"], key="crack_img")
    if crack_file:
        try:
            crack_img = Image.open(crack_file).convert("RGB")
            left, right = st.columns([1, 1.2], gap="large")
            with left:
                st.image(crack_img, caption="Uploaded surface image", use_container_width=True)
            with right:
                if st.button("🧪 Assess visible defect", key="run_crack", type="primary", use_container_width=True):
                    prompt = """Inspect the surface image and return ONLY valid JSON with keys:
defect_type (one of Hairline, Settlement, Structural Shear, Thermal Expansion, Spalling, Unable to Determine),
estimated_crack_width_mm (number or null; clearly label as rough visual estimate, never imply calibrated measurement),
confidence (Low/Medium/High with caveat), root_causes (array of plausible causes, not definitive), recommended_repairs (array; distinguish monitoring from engineer-prescribed repair), urgency (Monitor / Routine inspection / Prompt engineer review / Restrict access pending urgent inspection), limitations (string).
Consider possibilities such as epoxy injection only when appropriate after engineering assessment, and structural re-grouting only when relevant to the actual defect. Do not diagnose structural safety from an image alone."""
                    with st.spinner("Assessing visible defect…"):
                        try:
                            st.session_state["crack_result"] = gemini_json(prompt, crack_img, api_key)
                            st.session_state["crack_demo"] = False
                        except Exception:
                            st.session_state["crack_result"] = crack_demo()
                            st.session_state["crack_demo"] = True
            result = st.session_state.get("crack_result")
            if result:
                if st.session_state.get("crack_demo"):
                    st.warning("Demonstration result shown; it is not a diagnosis of the uploaded image.")
                a, b, c = st.columns(3)
                a.metric("Defect category", str(result.get("defect_type", "Unknown")))
                width = result.get("estimated_crack_width_mm")
                b.metric("Estimated width", f"{width} mm" if width is not None else "Not estimated")
                c.metric("Urgency", str(result.get("urgency", "Undetermined")))
                st.markdown("#### Potential root causes")
                for cause in result.get("root_causes", []):
                    st.markdown(f"- {cause}")
                st.markdown("#### Recommended next steps")
                for repair in result.get("recommended_repairs", []):
                    st.markdown(f"- {repair}")
                st.info("If a crack is widening, diagonal through a structural member, associated with displacement, or accompanied by falling/spalled concrete, keep people clear and obtain an urgent assessment by a qualified structural engineer.")
                if result.get("limitations"):
                    st.caption(result["limitations"])
                safe_download_json(result, "crack_diagnostics.json")
        except Exception as exc:
            st.error(f"Unable to read image: {exc}")
    else:
        st.info("Upload a close, well-lit photo. Include a scale reference if possible, but do not treat the model's estimate as a measurement.")

# ---------------------------- Tab 3 -----------------------------------------
with tab_planning:
    st.subheader("Planning & Real Estate Valuation")
    st.write("Transparent early-stage estimates; replace default assumptions with a quantity surveyor's bill of quantities and local rates.")
    col1, col2 = st.columns(2)
    with col1:
        structure = st.selectbox("Structure type", ["Residential", "Commercial", "Industrial", "Institutional"])
        sqft = st.number_input("Built-up area (sq ft)", min_value=100, max_value=2_000_000, value=2000, step=100)
        tier = st.selectbox("Location tier", ["Tier 1", "Tier 2", "Tier 3"], help="Indicative city-market tier, not a precise location appraisal.")
    with col2:
        completion = st.slider("Construction completion", 0, 100, 35, 5)
        quality = st.selectbox("Finish level", ["Economy", "Standard", "Premium"], index=1)
        city = st.text_input("City / locality (optional)", placeholder="e.g., Indore")
    rates = {
        "Residential": {"Economy": 1700, "Standard": 2200, "Premium": 3000},
        "Commercial": {"Economy": 2100, "Standard": 2800, "Premium": 3900},
        "Industrial": {"Economy": 1400, "Standard": 1900, "Premium": 2600},
        "Institutional": {"Economy": 1900, "Standard": 2500, "Premium": 3400}
    }
    tier_factor = {"Tier 1": 1.25, "Tier 2": 1.0, "Tier 3": 0.85}[tier]
    construction_rate = rates[structure][quality] * tier_factor
    total_budget = sqft * construction_rate
    incurred = total_budget * completion / 100
    market_factor = {"Tier 1": 1.65, "Tier 2": 1.25, "Tier 3": 1.0}[tier]
    type_factor = {"Residential": 1.0, "Commercial": 1.25, "Industrial": 0.8, "Institutional": 0.9}[structure]
    asset_value = sqft * (construction_rate * 1.12 + 900) * market_factor * type_factor
    # Coarse planning heuristics; not a BOQ.
    cement_bags = sqft * (0.38 if structure != "Industrial" else 0.30)
    steel_kg = sqft * (4.0 if structure in ("Residential", "Institutional") else 5.0)
    m1, m2, m3 = st.columns(3)
    m1.metric("Estimated project budget", inr(total_budget))
    m2.metric("CapEx incurred to date", inr(incurred))
    m3.metric("Indicative asset valuation", inr(asset_value))
    st.progress(completion / 100, text=f"Milestone progress: {completion}% complete")
    st.markdown("#### Material planning indicators")
    x1, x2, x3 = st.columns(3)
    x1.metric("Indicative cement", f"{cement_bags:,.0f} bags")
    x2.metric("Indicative reinforcement steel", f"{steel_kg/1000:,.1f} tonnes")
    x3.metric("Remaining budget", inr(max(0, total_budget - incurred)))
    st.caption(f"Model assumptions: ₹{construction_rate:,.0f}/sq ft construction cost; city/locality: {city or 'not specified'}. Material quantities use broad thumb rules and are not suitable for procurement or structural design.")
    st.warning("Valuation is an illustrative model, not a certified market valuation. Actual cost and value depend on location, specifications, taxes, approvals, site conditions, land value, and current market evidence.")
    st.markdown("#### Conceptual 3D architectural rendering")
    render_prompt = st.text_area("Rendering prompt", value=f"Photorealistic conceptual {structure.lower()} building, {sqft:,.0f} sq ft built-up area, {quality.lower()} finish, contemporary Indian architecture, {city or tier + ' Indian city'}, construction completion stage {completion}%, realistic daylight, architectural visualization, no text, no watermark")
    st.code("Pollinations AI prompt ready. Use it with your preferred image-generation endpoint; availability and terms may change.", language="text")
    st.text_input("Optional Pollinations image URL template", value="https://image.pollinations.ai/prompt/", key="pollinations_base")
    if st.button("Generate rendering URL"):
        import urllib.parse
        base_url = st.session_state.get("pollinations_base", "https://image.pollinations.ai/prompt/")
        url = base_url.rstrip("/") + "/" + urllib.parse.quote(render_prompt)
        st.session_state["render_url"] = url
    if st.session_state.get("render_url"):
        st.markdown(f"[Open conceptual rendering]({st.session_state['render_url']})")
        st.caption("External image service; do not send confidential site plans or sensitive information.")
    plan_report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "inputs": {"structure_type": structure, "built_up_sqft": sqft, "location_tier": tier, "city": city, "completion_percent": completion, "finish_level": quality},
        "assumptions": {"construction_rate_inr_per_sqft": round(construction_rate, 2), "cement_bags_per_sqft": 0.38 if structure != "Industrial" else 0.30, "steel_kg_per_sqft": 4.0 if structure in ("Residential", "Institutional") else 5.0},
        "estimates": {"total_project_budget_inr": round(total_budget, 2), "capex_incurred_inr": round(incurred, 2), "indicative_asset_valuation_inr": round(asset_value, 2), "cement_bags": round(cement_bags), "steel_kg": round(steel_kg)}
    }
    safe_download_json(plan_report, "project_planning_estimate.json")

# ---------------------------- Tab 4 -----------------------------------------
with tab_assistant:
    st.subheader("Daily Site Assistant & Weather-Aware Advisory")
    weather = st.selectbox("Current / forecast weather", ["Normal", "High Wind", "Heavy Rain", "Extreme Heat"])
    alerts = {
        "Normal": ("Routine controls", "Continue only under the approved method statement. Maintain housekeeping, PPE, access routes, and routine inspections."),
        "High Wind": ("High wind precautions", "Pause crane lifts and work at height when wind exceeds equipment/site limits. Secure loose materials, check scaffold conditions, and follow the lift supervisor's stop-work criteria."),
        "Heavy Rain": ("Rain and electrical hazards", "Stop work in flooded or unstable areas. Isolate damaged electrical equipment, protect temporary power connections, inspect excavations and slopes, and reassess access before restarting."),
        "Extreme Heat": ("Heat-stress prevention", "Provide water, shade, rest breaks, acclimatization, and buddy monitoring. Adjust work/rest cycles to site policy and local heat guidance; watch for confusion, collapse, or other heat-illness signs.")
    }
    title, advice = alerts[weather]
    kind = "green" if weather == "Normal" else "red" if weather in ("High Wind", "Heavy Rain") else "amber"
    st.markdown(f'<div class="panel"><h3>{title} {pill(weather, kind)}</h3><p>{advice}</p></div>', unsafe_allow_html=True)
    st.markdown("**Concrete curing reminder:** protect fresh concrete from rapid moisture loss, maintain the curing method and duration specified by the project specification, and avoid placing concrete during conditions outside the approved temperature/rain plan.")
    st.markdown("#### Ask the construction assistant")
    st.caption("Ask about site planning, PPE, concrete defects, construction sequencing, materials, or risk controls. Verify safety-critical advice with the responsible professional.")
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = []
    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    user_q = st.chat_input("Ask a construction engineering question…")
    if user_q:
        st.session_state["chat_messages"].append({"role": "user", "content": user_q})
        with st.chat_message("user"):
            st.markdown(user_q)
        with st.chat_message("assistant"):
            with st.spinner("Preparing guidance…"):
                context = f"Current weather condition: {weather}. Advisory: {advice}\nQuestion: {user_q}\nProvide concise, practical, safety-first construction guidance. State assumptions and recommend qualified professional review for structural, regulatory, or high-risk decisions."
                answer = gemini_chat(st.session_state["chat_messages"][:-1] + [{"role": "user", "content": context}], api_key)
                st.markdown(answer)
        st.session_state["chat_messages"].append({"role": "assistant", "content": answer})
    if st.session_state["chat_messages"]:
        if st.button("Clear conversation"):
            st.session_state["chat_messages"] = []
            st.rerun()

st.markdown("---")
st.caption("Multimodal Construction Intelligence Platform • Prototype capstone • Verify all site-critical decisions with competent professionals.")
