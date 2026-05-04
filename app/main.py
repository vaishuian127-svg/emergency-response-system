from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.llm_analyzer import analyze_accident, generate_emergency_plan, rank_hospitals_by_accident_type
from app.hospital_finder import find_nearby_hospitals
from app.email_service import send_dispatcher_email_async

# ─── App Setup ─────────────────────────────────────────────
app = FastAPI(
    title="Emergency Response System API",
    description="LLM-Based Emergency Response Optimization System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request Model ──────────────────────────────────────────
class AccidentRequest(BaseModel):
    report: str
    location: str
    radius_km: int = 5


# ─── Routes ─────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "message": "Emergency Response System API is running",
        "version": "1.0.0",
        "endpoints": [
            "POST /analyze",
            "POST /hospitals",
            "GET /health"
        ]
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API is running fine"}


@app.post("/analyze")
def analyze_emergency(data: AccidentRequest):
    if not data.report.strip():
        raise HTTPException(status_code=400, detail="Accident report cannot be empty")
    if not data.location.strip():
        raise HTTPException(status_code=400, detail="Location cannot be empty")

    try:
        analysis = analyze_accident(data.report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Analysis failed: {str(e)}")

    # ─── Smart radius auto-expansion ────────────────────────
    hospitals = []
    lat, lon = None, None
    actual_radius = data.radius_km
    expanded = False

    try:
        hospitals, lat, lon = find_nearby_hospitals(data.location, data.radius_km)

        # If coordinates not found at all, raise clear error
        if lat is None or lon is None:
            raise HTTPException(
                status_code=400,
                detail=f"Could not find location: '{data.location}'. Please try a more specific location name e.g. 'Tumkur, Karnataka' instead of 'SIT main road, tumkur'."
            )

        # Auto-expand radius if no hospitals found
        if not hospitals:
            retry_radii = [25, 35, 50, 75, 100]
            for r in retry_radii:
                if r <= data.radius_km:
                    continue
                hospitals, lat, lon = find_nearby_hospitals(data.location, r)
                if hospitals:
                    actual_radius = r
                    expanded = True
                    break

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hospital search failed: {str(e)}")

    # Rank hospitals by accident type and specialties, but do NOT truncate the list
    if hospitals:
        hospitals = rank_hospitals_by_accident_type(hospitals, analysis)

    try:
        plan = generate_emergency_plan(analysis, hospitals)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plan generation failed: {str(e)}")

    # Send email to dispatcher in the background
    send_dispatcher_email_async(
        analysis=analysis,
        hospitals=hospitals,
        location=data.location,
        lat=lat,
        lon=lon
    )

    return {
        "success": True,
        "analysis": analysis,
        "hospitals": hospitals,
        "emergency_plan": plan,
        "location_coords": {
            "lat": lat,
            "lon": lon
        },
        "radius_used": actual_radius,
        "radius_expanded": expanded,
        "radius_requested": data.radius_km
    }


@app.post("/hospitals")
def get_hospitals(data: AccidentRequest):
    try:
        hospitals, lat, lon = find_nearby_hospitals(data.location, data.radius_km)
        return {
            "success": True,
            "location": data.location,
            "hospitals": hospitals,
            "total_found": len(hospitals),
            "coords": {"lat": lat, "lon": lon}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))