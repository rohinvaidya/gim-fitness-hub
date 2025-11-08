# Gym & Diet Plan — Claude-powered (Python + Flask)

One-page app that generates a **7-day workout** and **diet plan** from:
- **Goal** (weight_loss, strength, hypertrophy, yoga, general)
- **Days per week** (1–6 training days)
- **Diet type** (vegetarian, vegan, non_veg)
- **Age** (years)

Backend calls **Claude (Haiku by default)** once and returns **tabular HTML**. If the AI response is invalid/unavailable, a **rule-based fallback** instantly generates a decent plan.

## Team
Sanskar Vidyarthi
Rohin Vaidya
Andy Diep

## Quickstart

```bash
git clone <this repo> gymdiet-assistant
cd gymdiet-assistant
cp .env.example .env  # add your ANTHROPIC_API_KEY
python -m venv .venv && . .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
