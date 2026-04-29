import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def analyze_accident(report: str):
    """
    Takes a natural language accident report.
    Returns structured data extracted by the LLM.
    """

    prompt = f"""
You are an emergency response AI assistant.
Analyze the following accident report and extract information. The report will be in English. Understand the context accurately.

Accident Report:
\"{report}\"

Return ONLY a valid JSON object with exactly these fields:
{{
  "location_description": "the place mentioned in the report",
  "accident_type": "type of accident eg vehicle collision fire medical emergency",
  "victims": 0,
  "severity": "one of: LOW, MEDIUM, HIGH, CRITICAL",
  "services_needed": ["ambulance"],
  "ambulances_needed": 1,
  "immediate_actions": "brief one sentence instruction for first responders",
  "summary": "one paragraph summary of the situation",
  "required_hospital_type": "one of: trauma_center, burn_unit, cardiac_center, pediatric, general, poison_control, orthopedic, neurology, maternity, multi_specialty",
  "required_specialties": ["list of medical specialties needed eg trauma surgery ICU burns cardiology pediatrics neurology orthopedics"]
}}

Severity guide:
- LOW: minor injuries, no unconscious victims
- MEDIUM: multiple injuries, one unconscious
- HIGH: serious injuries, multiple unconscious, heavy traffic
- CRITICAL: fatalities likely, mass casualties, fire or explosion

Required hospital type guide:
- trauma_center: vehicle collisions, falls, stab/gunshot wounds, crush injuries
- burn_unit: fire accidents, chemical burns, electrical burns
- cardiac_center: heart attack, chest pain, cardiac arrest
- pediatric: accidents involving children under 12
- poison_control: poisoning, drug overdose, chemical exposure
- orthopedic: bone fractures, joint injuries
- neurology: head injuries, stroke, seizures, unconscious victims
- maternity: pregnancy complications, childbirth emergencies
- multi_specialty: multiple injury types, mass casualties
- general: minor injuries, basic medical care

Return ONLY the JSON. No explanation. No markdown. No extra text.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are an emergency response AI. Always respond with valid JSON only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    raw = response.choices[0].message.content.strip()

    # Clean markdown if model wraps response in it
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    result = json.loads(raw)
    return result


# ─── Hospital type keyword matching ─────────────────────────
HOSPITAL_TYPE_KEYWORDS = {
    "trauma_center": [
        "trauma", "emergency", "accident", "casualty", "surgery",
        "surgical", "general hospital", "district hospital", "medical college",
        "government", "multi specialty", "multispecialty"
    ],
    "burn_unit": [
        "burn", "plastic surgery", "skin", "reconstructive"
    ],
    "cardiac_center": [
        "cardiac", "cardiology", "heart", "cardio", "cardiovascular"
    ],
    "pediatric": [
        "children", "child", "paediatric", "pediatric", "kids", "infant", "neonatal"
    ],
    "poison_control": [
        "poison", "toxicology", "detox", "overdose"
    ],
    "orthopedic": [
        "orthopedic", "orthopaedic", "bone", "fracture", "joint", "spine"
    ],
    "neurology": [
        "neuro", "neurology", "brain", "stroke", "spine", "neurological"
    ],
    "maternity": [
        "maternity", "obstetric", "gynecology", "gynaecology", "women",
        "lady", "mother", "delivery", "antenatal"
    ],
    "multi_specialty": [
        "multi", "multispecialty", "super specialty", "superspecialty",
        "apollo", "fortis", "manipal", "narayana", "columbia", "aster",
        "sakra", "sparsh", "rainbow", "medanta", "care hospital"
    ],
    "general": [
        "clinic", "health center", "primary", "phc", "community"
    ]
}


def score_hospital_for_accident(hospital: dict, required_type: str, required_specialties: list) -> int:
    """
    Scores a hospital based on how well it matches the accident type.
    Higher score = better match.
    """
    score = 0
    name = hospital.get("name", "").lower()
    h_type = hospital.get("type", "").lower()

    # Check if hospital name matches required type keywords
    keywords = HOSPITAL_TYPE_KEYWORDS.get(required_type, [])
    for kw in keywords:
        if kw in name:
            score += 10

    # Check required specialties in hospital name
    for specialty in required_specialties:
        if specialty.lower() in name:
            score += 8

    # Government hospitals get bonus for trauma/general emergencies
    if required_type in ["trauma_center", "general", "multi_specialty"]:
        if h_type == "Government" or "government" in name or "govt" in name:
            score += 5
        if "district" in name or "taluk" in name or "general hospital" in name:
            score += 5

    # Multi-specialty hospitals are good fallback for any accident
    multi_keywords = HOSPITAL_TYPE_KEYWORDS["multi_specialty"]
    for kw in multi_keywords:
        if kw in name:
            score += 3

    # Closer hospitals get a distance bonus
    distance = hospital.get("distance_km", 999)
    if distance <= 2:
        score += 6
    elif distance <= 5:
        score += 4
    elif distance <= 10:
        score += 2

    return score


def rank_hospitals_by_accident_type(hospitals: list, analysis: dict) -> list:
    """
    Ranks hospitals based on accident type and required specialties.
    Adds a 'match_score' and 'best_match' flag to each hospital.
    """
    required_type = analysis.get("required_hospital_type", "general")
    required_specialties = analysis.get("required_specialties", [])

    if not hospitals:
        return hospitals

    # Score each hospital
    for hospital in hospitals:
        hospital["match_score"] = score_hospital_for_accident(
            hospital, required_type, required_specialties
        )

    # Sort by score descending, then by distance
    hospitals.sort(key=lambda h: (-h["match_score"], h["distance_km"]))

    # Mark the top hospital as best match and top 10
    if hospitals:
        for i, h in enumerate(hospitals):
            h["best_match"] = (i == 0)
            h["top_10"] = (i < 10)

    # Sort back by distance so the nearest hospitals are presented in order
    hospitals.sort(key=lambda h: h["distance_km"])

    return hospitals


def generate_emergency_plan(analysis: dict, hospitals: list):
    """
    Takes structured analysis + nearby hospitals.
    Returns a full human-readable emergency response plan.
    """

    hospital_text = ""
    for i, h in enumerate(hospitals[:10]): # send top 10 closely located for the prompt to avoid context overflow, UI still shows all
        hospital_text += f"{i+1}. {h['name']} ({h['type']}) — {h['distance_km']} km away\n"

    if not hospital_text:
        hospital_text = "No hospitals found nearby. Contact emergency services immediately."

    prompt = f"""
You are an emergency response coordinator AI.

Accident Analysis:
- Type: {analysis.get('accident_type')}
- Severity: {analysis.get('severity')}
- Victims: {analysis.get('victims')}
- Location: {analysis.get('location_description')}
- Services needed: {', '.join(analysis.get('services_needed', []))}
- Ambulances needed: {analysis.get('ambulances_needed')}

Nearby Hospitals (sorted by closest distance):
{hospital_text}

Generate a clear, professional emergency response plan with these sections:
1. Situation Summary
2. Immediate Actions (numbered steps)
3. Recommended Hospital and why it is suitable for this type of accident
4. Ambulance Dispatch Instructions
5. Safety Precautions at scene

Write in a clear, professional tone.
Note: This is a simulation project — no real services will be contacted.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a professional emergency response coordinator."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.4
    )

    return response.choices[0].message.content.strip()