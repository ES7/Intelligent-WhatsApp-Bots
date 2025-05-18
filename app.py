from flask import Flask, request
from flask import send_from_directory
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import re
import os

app = Flask(__name__)

# Configure Gemini
genai.configure(api_key='YOUR_API_KEY_HERE')
model = genai.GenerativeModel('gemini-1.5-flash-002')

# Extract YouTube video ID
def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

# Summarize using Gemini
def summarize_text(text):
    prompt = "Summarize this YouTube video transcript in simple points:\n\n" + text
    response = model.generate_content(prompt)
    return response.text

def save_summary_to_file(summary, video_id):
    filename = f"{video_id}_summary.txt"
    filepath = os.path.join("summaries", filename)
    os.makedirs("summaries", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(summary)
    return filepath


@app.route("/", methods=['GET', 'POST'])
def whatsapp_bot():
    if request.method == 'GET':
        return "WhatsApp bot is running."

    # POST method (from Twilio webhook)
    incoming_msg = request.values.get('Body', '').strip()
    resp = MessagingResponse()
    msg = resp.message()

    # Your existing logic here...
    if "youtube.com" in incoming_msg or "youtu.be" in incoming_msg:
        video_id = extract_video_id(incoming_msg)
        if not video_id:
            msg.body("❌ Invalid YouTube link. Please try again.")
            return str(resp)

        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            full_text = " ".join([t['text'] for t in transcript])
            summary = summarize_text(full_text)
            
            # Save to file
            filepath = save_summary_to_file(summary, video_id)
            # Host it on your ngrok server
            file_url = request.host_url + f"summaries/{video_id}_summary.txt"
            msg.body(f"✅ Summary ready! Download here:\n{file_url}")
            
            # msg.body("✅ Video Summary:\n" + summary)
        except Exception as e:
            msg.body("⚠️ Failed to fetch transcript. It might be disabled or unavailable.")
    else:
        msg.body("📌 Please send a valid YouTube video link.")

    return str(resp)

@app.route('/summaries/<path:filename>')
def serve_summary_file(filename):
    return send_from_directory(os.path.join(os.getcwd(), 'summaries'), filename)

if __name__ == '__main__':
    app.run(debug=True)
