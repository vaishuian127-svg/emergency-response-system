import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import threading
from dotenv import load_dotenv

load_dotenv()

def send_dispatcher_email_async(analysis: dict, hospitals: list, location: str, lat: float, lon: float):
    """
    Sends an email to the dispatcher in a separate thread so it doesn't block the API response.
    """
    thread = threading.Thread(
        target=_send_dispatcher_email_sync,
        args=(analysis, hospitals, location, lat, lon)
    )
    thread.start()

def _send_dispatcher_email_sync(analysis: dict, hospitals: list, location: str, lat: float, lon: float):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    dispatcher_email = os.getenv("DISPATCHER_EMAIL") # Can be the same as sender_email for testing

    if not sender_email or not sender_password or not dispatcher_email:
        print("Email credentials not fully set in .env. Skipping email dispatch.")
        return

    # Create the email message
    msg = MIMEMultipart("alternative")
    severity = analysis.get('severity', 'UNKNOWN')
    msg['Subject'] = f"🚨 URGENT: {severity} Emergency reported at {location}"
    msg['From'] = f"Emergency Response System <{sender_email}>"
    msg['To'] = dispatcher_email

    # Format hospital list for email
    top_hospitals_html = ""
    for h in hospitals[:3]: # Show top 3 hospitals
        top_hospitals_html += f"<li><b>{h['name']}</b> ({h.get('distance_km', '?')} km away) - {h.get('type', 'Hospital')}</li>"

    if not top_hospitals_html:
        top_hospitals_html = "<li>No nearby hospitals found.</li>"

    # HTML Body for a clean, professional look
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <div style="border: 2px solid #d9534f; padding: 20px; border-radius: 10px; max-width: 600px;">
            <h2 style="color: #d9534f; margin-top: 0;">🚨 EMERGENCY DISPATCH ALERT</h2>
            
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;"><b>Location:</b></td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">{location}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;"><b>Coordinates:</b></td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;"><a href="https://www.google.com/maps/search/?api=1&query={lat},{lon}">View on Google Maps</a></td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;"><b>Severity:</b></td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee; color: red; font-weight: bold;">{severity}</td>
                </tr>
            </table>
            
            <h3 style="background-color: #f8f9fa; padding: 10px; border-left: 4px solid #337ab7;">Accident Details</h3>
            <ul style="margin-bottom: 20px;">
                <li><b>Accident Type:</b> {analysis.get('accident_type', 'N/A')}</li>
                <li><b>Estimated Victims:</b> {analysis.get('victims', 'N/A')}</li>
                <li><b>Ambulances Needed:</b> {analysis.get('ambulances_needed', 'N/A')}</li>
                <li><b>Services Needed:</b> {', '.join(analysis.get('services_needed', []))}</li>
            </ul>

            <h3 style="background-color: #f8f9fa; padding: 10px; border-left: 4px solid #f0ad4e;">Immediate Actions Advised</h3>
            <p style="padding-left: 20px; border-left: 2px solid #ccc;"><i>{analysis.get('immediate_actions', 'N/A')}</i></p>

            <h3 style="background-color: #f8f9fa; padding: 10px; border-left: 4px solid #5cb85c;">Nearest Recommended Hospitals</h3>
            <ul>
                {top_hospitals_html}
            </ul>

            <hr style="border: 0; border-top: 1px solid #eee; margin-top: 30px;">
            <p style="font-size: 11px; color: #888; text-align: center;">This is an automated dispatch from the Emergency Response System Simulation.</p>
        </div>
      </body>
    </html>
    """
    
    part = MIMEText(html, "html")
    msg.attach(part)

    try:
        # Connect to Gmail SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Secure the connection
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, dispatcher_email, msg.as_string())
        server.quit()
        print(f"✅ Successfully sent dispatch email to {dispatcher_email}")
    except Exception as e:
        print(f"❌ Failed to send dispatch email: {e}")
