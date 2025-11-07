from html import escape
from .schema import DAYS

def _render_workout_row(day):
    focus = escape(day.get("focus",""))
    ex_html = []
    for ex in day.get("exercises", []):
        name = escape(str(ex.get("name","")))
        sets = escape(str(ex.get("sets","")))
        reps = escape(str(ex.get("reps","")))
        rest = ex.get("rest_sec", None)
        rest_str = f" — rest {rest}s" if rest else ""
        ex_html.append(f"<li>{name}: {sets} × {reps}{rest_str}</li>")
    return f"""
      <tr>
        <td class="day">{escape(day.get("day",""))}</td>
        <td class="focus">{focus}</td>
        <td><ul class="ex-list">{''.join(ex_html)}</ul></td>
      </tr>
    """

def _render_diet_row(day):
    meals_html = []
    for m in day.get("meals", []):
        name = escape(str(m.get("name","")))
        notes = m.get("notes","")
        notes = f" — {escape(str(notes))}" if notes else ""
        meals_html.append(f"<li>{name}{notes}</li>")
    return f"""
      <tr>
        <td class="day">{escape(day.get("day",""))}</td>
        <td><ul class="meal-list">{''.join(meals_html)}</ul></td>
      </tr>
    """

def render_plan_tables(plan_dict: dict):
    workout = plan_dict.get("workout_plan", [])
    diet = plan_dict.get("diet_plan", [])
    notes = plan_dict.get("notes","")

    wrows = "".join(_render_workout_row(d) for d in workout)
    drows = "".join(_render_diet_row(d) for d in diet)

    workout_html = f"""
    <table class="plan-table">
      <thead>
        <tr><th>Day</th><th>Focus</th><th>Exercises (sets × reps / time)</th></tr>
      </thead>
      <tbody>
        {wrows}
      </tbody>
    </table>
    """

    diet_html = f"""
    <table class="plan-table">
      <thead>
        <tr><th>Day</th><th>Meals</th></tr>
      </thead>
      <tbody>
        {drows}
      </tbody>
    </table>
    """

    return workout_html, diet_html
