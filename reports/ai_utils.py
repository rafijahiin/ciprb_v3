import os
import json
import requests
from tracker.models import FistulaCase
from mpdsr.models import MPDSREvent


def generate_newsletter_narrative(month, year):
    api_key = os.environ.get('GROQ_API_KEY', '').strip()
    if not api_key:
        return "Error: GROQ_API_KEY not configured. Get a free key at console.groq.com"

    total_deaths = MPDSREvent.objects.count()
    pending_actions = MPDSREvent.objects.filter(action_status='PENDING').count()
    fistula_surgeries = FistulaCase.objects.filter(referral_status='OPERATED').count()
    implemented = MPDSREvent.objects.filter(action_status='IMPLEMENTED').count()

    prompt = f"""You are a senior M&E advisor writing a policy advocacy newsletter for UNFPA Bangladesh's CIPRB-SRHR/RCH programme.

Write a professional 3-paragraph newsletter for {month}/{year} based on this data:
- Fistula surgeries completed: {fistula_surgeries}
- MPDSR deaths reviewed: {total_deaths}
- Corrective actions pending: {pending_actions}
- Actions implemented: {implemented}

Paragraph 1: Programme highlights and fistula campaign progress.
Paragraph 2: MPDSR data-to-action gap analysis and what the numbers mean.
Paragraph 3: Call to action for health system stakeholders.

Tone: professional, evidence-based, action-oriented. Audience: UNFPA CO, MoHFW, implementing partners."""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 800,
                "temperature": 0.7,
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.HTTPError as e:
        return f"Error: Groq API returned {e.response.status_code}. Check your GROQ_API_KEY in Render environment variables. Get a free key at console.groq.com"
    except Exception as e:
        return f"Error generating narrative: {str(e)}"
