from app.email_service import send_dispatcher_email_async
from dotenv import load_dotenv
import time

load_dotenv()

print("Testing email dispatch...")
send_dispatcher_email_async(
    analysis={"severity": "TEST", "accident_type": "Test", "victims": 0, "services_needed": []},
    hospitals=[],
    location="Test Location",
    lat=0.0,
    lon=0.0
)

# Wait a moment for the thread to finish
time.sleep(5)
print("Test complete.")
