import logging
import google.generativeai as genai
from config import settings

log = logging.getLogger("uvicorn")

# Configure Gemini
try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-pro")
except Exception as e:
    log.error(f"Failed to configure Gemini: {e}")
    model = None

async def generate_risk_analysis(session_data: dict, events_summary: dict) -> str:
    """
    Calls Google Gemini Flash to generate a brief safety summary of the driving session.
    """
    if not model:
        log.warning("Gemini model not initialized. Returning fallback summary.")
        return _fallback_summary(session_data.get("critical_events", 0))

    duration_mins = "Unknown"
    start = session_data.get("start_time")
    end = session_data.get("end_time")
    if start and end:
        duration_mins = round((end - start).total_seconds() / 60, 1)

    prompt = f"""You are a driver safety analyst. Analyze this driving session:
- Duration: {duration_mins} minutes
- Total drowsiness events: {session_data.get('total_events', 0)}
- Critical events: {session_data.get('critical_events', 0)}
- Average drowsiness score: {session_data.get('avg_drowsiness_score', 0):.2f}

Event State breakdown:
- ALERT: {events_summary.get('ALERT', 0)}
- MILD: {events_summary.get('MILD', 0)}
- DROWSY: {events_summary.get('DROWSY', 0)}
- CRITICAL: {events_summary.get('CRITICAL', 0)}

Biometrics average during events:
- Average EAR: {events_summary.get('avg_ear', 0):.3f}
- Average blink rate: {events_summary.get('avg_blink_rate', 0):.1f} bpm

Provide: 
1) Overall risk level (LOW/MEDIUM/HIGH/CRITICAL)
2) A 2-3 sentence safety assessment
3) One specific recommendation for the driver.
Keep the total response under 100 words.
"""

    log.info("Requesting Gemini risk analysis...")
    try:
        # We must use generate_content_async since this is a FastAPI async route
        response = await model.generate_content_async(prompt)
        text = response.text.strip()
        log.info("Gemini risk analysis generated successfully.")
        return text
    except Exception as e:
        log.error(f"Gemini API error: {e}")
        return _fallback_summary(session_data.get("critical_events", 0))

def _fallback_summary(critical_count: int) -> str:
    if critical_count > 5:
        return "CRITICAL RISK: Multiple critical drowsiness events detected. Immediate rest is mandatory before driving again."
    elif critical_count > 0:
        return "HIGH RISK: Driver experienced severe drowsiness. A break is strongly recommended."
    else:
        return "LOW RISK: Analysis API unavailable, but no critical events were recorded during the trip."
