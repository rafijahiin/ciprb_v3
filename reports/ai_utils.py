import os
import json
import urllib.request
from tracker.models import FistulaCase
from mpdsr.models import MPDSREvent


def generate_newsletter_narrative(month, year):
    api_key = os.environ.get('GROQ_API_KEY')
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
Paragraph 2: MPDSR data-to-action gap — what the numbers mean and why it matters.
Paragraph 3: Call to action for health system stakeholders.

Tone: professional, evidence-based, action-oriented. Audience: UNFPA, MoHFW, implementing partners."""

    try:
        payload = json.dumps({
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 800,
            "temperature": 0.7,
        }).encode('utf-8')

        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            return result['choices'][0]['message']['content']

    except Exception as e:
        return f"Error generating narrative: {str(e)}"
