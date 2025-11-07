import os, json, traceback
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

try:
    import anthropic
except Exception:
    anthropic = None

from utils.prompt import SYSTEM_PROMPT, build_user_prompt
from utils.schema import Plan, validate_plan_dict
from utils.render import render_plan_tables
from utils.fallback import generate_fallback_plan

load_dotenv()

app = Flask(__name__)

# Anthropic client (optional if you only want fallback)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")
CLAUDE_TEMPERATURE = float(os.getenv("CLAUDE_TEMPERATURE", "0.2"))

client = None
if ANTHROPIC_API_KEY and anthropic is not None:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/api/plan")
def api_plan():
    data = request.get_json(force=True)
    goal = (data.get("goal") or "general").strip().lower()
    days_per_week = int(data.get("days_per_week") or 3)
    diet_type = (data.get("diet_type") or "vegetarian").strip().lower()
    age = int(data.get("age") or 30)

    plan_dict = None
    ai_error = None
    used_ai = False           
    reason = None 

    # Try Claude once
    if client:
        try:
            user_prompt = build_user_prompt(goal, days_per_week, diet_type, age)
            msg = client.messages.create(
                model=CLAUDE_MODEL,
                temperature=CLAUDE_TEMPERATURE,
                max_tokens=1800,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            # Claude SDK returns a list of content blocks
            text = ""
            for block in msg.content:
                if getattr(block, "type", "") == "text" or isinstance(block, dict) and block.get("type")=="text":
                    text = block.text if hasattr(block, "text") else block.get("text","")
                    break

            # Expect strict JSON per system prompt
            plan_dict = json.loads(text)
            plan_dict = validate_plan_dict(plan_dict)  # normalize/order
            used_ai = True
        except Exception as e:
            ai_error = f"{type(e).__name__}: {e}"
            reason = "ai_error"
            plan_dict = None
    else:
        reason = "no_anthropic_client"   # <— no AI configured

    # Fallback if no AI or invalid response
    if not plan_dict:
        plan_dict = generate_fallback_plan(goal, days_per_week, diet_type, age)

    # Render tabular HTML for the UI
    workout_html, diet_html = render_plan_tables(plan_dict)
    notes = plan_dict.get("notes", "")

    return jsonify({
        "workout_html": workout_html,
        "diet_html": diet_html,
        "notes": notes,
        "ai_error": ai_error,  # exposed for debugging in hackathon demo
        "used_ai": used_ai,                          
        "source": "ai" if used_ai else "fallback",   
        "reason": ai_error or reason                 
    })

if __name__ == "__main__":
    # For hackathon dev only; use a WSGI server for prod.
    app.run(debug=True)
