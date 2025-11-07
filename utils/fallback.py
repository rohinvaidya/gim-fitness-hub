from .schema import DAYS

def _pick_training_indices(days_per_week: int):
    # Simple, readable schedules
    patterns = {
        1: [2],                      # Wed
        2: [1,4],                    # Tue, Fri
        3: [0,2,4],                  # Mon, Wed, Fri
        4: [0,2,4,6],                # Mon, Wed, Fri, Sun
        5: [0,1,3,4,5],              # Mon, Tue, Thu, Fri, Sat
        6: [0,1,2,4,5,6],            # Mon–Wed, Fri–Sun (Thu rest)
    }
    return patterns.get(max(1, min(6, days_per_week)), [0,2,4])

def _volume_and_rest_by_age(age: int):
    if age >= 55:
        return (4, (75, 150))  # ~4 exercises, slightly longer rests
    if age >= 45:
        return (5, (60, 120))
    return (6, (45, 90))

def _exercises_for_goal(goal: str):
    goal = goal.lower()
    common = {
        "push": ["Push-ups", "Incline DB Press", "Overhead Press", "Dips (assisted)"],
        "pull": ["Bent-over Row", "Lat Pulldown", "Seated Row", "Face Pull"],
        "legs": ["Squat", "Lunge", "Romanian Deadlift", "Step-ups", "Hip Thrust"],
        "full": ["Goblet Squat", "Push-ups", "DB Row", "RDL", "Plank", "Farmer Carry"],
        "yoga": ["Sun Salutation", "Warrior Flow", "Triangle/Trikonasana", "Bridge", "Pigeon", "Savasana"],
        "cardio": ["Jump Rope", "Mountain Climbers", "Burpees (low-impact as needed)", "Cycling", "Fast Walk"],
        "core": ["Plank", "Side Plank", "Dead Bug", "Bird-dog", "Hollow Hold"]
    }
    if goal == "strength":
        splits = [
            ("Upper Strength", ["Overhead Press", "Incline DB Press", "Bent-over Row", "Lat Pulldown", "Face Pull", "Plank"]),
            ("Lower Strength", ["Squat", "Romanian Deadlift", "Lunge", "Hip Thrust", "Calf Raise", "Side Plank"])
        ]
    elif goal == "hypertrophy":
        splits = [
            ("Push", common["push"]),
            ("Pull", common["pull"]),
            ("Legs", common["legs"])
        ]
    elif goal == "yoga":
        splits = [("Yoga Flow", common["yoga"])]
    elif goal == "weight_loss":
        splits = [("Full Body Circuit", common["full"] + ["Core Finisher"])]
    else:
        splits = [("Full Body", common["full"])]
    return splits

def _diet_templates(diet_type: str):
    diet_type = diet_type.lower()
    if diet_type == "vegan":
        return [
            "Tofu scramble + whole-grain toast",
            "Quinoa bowl + roasted veggies + chickpeas",
            "Hummus wrap + salad",
            "Soy yogurt + berries + nuts",
            "Lentil soup + sourdough"
        ]
    if diet_type == "non_veg":
        return [
            "Egg omelet + whole-grain toast",
            "Chicken breast + rice + veggies",
            "Greek yogurt + berries + granola",
            "Tuna salad wrap",
            "Salmon + quinoa + greens"
        ]
    # vegetarian default
    return [
        "Paneer/Tofu stir-fry + rice",
        "Dal + roti/rice + salad",
        "Greek yogurt bowl + fruit + nuts",
        "Chickpea salad + olive oil",
        "Veggie omelet (or tofu) + toast"
    ]

def _rep_scheme(goal: str, age: int):
    if goal == "strength":
        return "4-6"
    if goal == "hypertrophy":
        return "8-12"
    if goal == "weight_loss":
        return "30-45s"
    if goal == "yoga":
        return "45-60m"
    return "8-12"

def generate_fallback_plan(goal: str, days_per_week: int, diet_type: str, age: int):
    days_idx = _pick_training_indices(days_per_week)
    volume, rest_range = _volume_and_rest_by_age(age)
    splits = _exercises_for_goal(goal)
    reps = _rep_scheme(goal, age)
    rest_low, rest_high = rest_range

    workout_plan = []
    diet_plan = []
    meal_pool = _diet_templates(diet_type)

    # rotate through splits for training days
    split_i = 0

    for i, day in enumerate(DAYS):
        if i in days_idx:
            focus, ex_list = splits[split_i % len(splits)]
            split_i += 1
            # trim/extend to volume
            ex_trimmed = (ex_list + ex_list)[0:volume]
            exercises = []
            for name in ex_trimmed:
                sets = 4 if goal == "strength" else (3 if goal in ("hypertrophy","general") else 3)
                rest_sec = (rest_high + rest_low)//2 if goal in ("strength","hypertrophy") else 45
                if goal == "yoga":
                    # yoga as duration only
                    exercises.append({"name": name, "sets": 1, "reps": reps, "rest_sec": None})
                else:
                    exercises.append({"name": name, "sets": sets, "reps": reps, "rest_sec": rest_sec})
            workout_plan.append({"day": day, "focus": focus, "exercises": exercises})
        else:
            # rest / active recovery
            workout_plan.append({
                "day": day,
                "focus": "Rest/Active Recovery",
                "exercises": [{"name": "Walk 30–45 min or gentle mobility", "sets": 1, "reps": "30-45m", "rest_sec": None}]
            })

        # Diet: 4 items per day
        meals = []
        for m in meal_pool[0:4]:
            notes = "aim ~25–35g protein" if "yogurt" in m.lower() or "paneer" in m.lower() or "chicken" in m.lower() or "tofu" in m.lower() or "salmon" in m.lower() or "eggs" in m.lower() else "whole foods, hydrate"
            meals.append({"name": m, "notes": notes})
        diet_plan.append({"day": day, "meals": meals})

    notes = (
        "Hydrate 2–3L/day. Warm up 5–10 min. "
        "Progress gradually; deload if joints feel tender. "
        "Protein ~1.6–2.2 g/kg/day (adjust for age). Sleep 7–9h."
    )
    return {"workout_plan": workout_plan, "diet_plan": diet_plan, "notes": notes}
