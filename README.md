# Intelligent-WhatsApp-Bots

## Code Explaination:
Import all the necessary files, then initialze the Flask App.
```python
app = Flask(__name__)
```
This line initializes a new Flask web application. `__name__` tells Flask where to look for resources like templates and static files.

### Configure the Gemini API
```python
genai.configure(api_key='YOUR_API_KEY_HERE')
model = genai.GenerativeModel('gemini-1.5-flash-002')
```
Set your API key so that your application can authenticate and use Google’s Gemini model. Load the **Gemini 1.5 Flash model** (an efficient, fast model) which you'll use later to summarize the text.

### Function to Extract Video URL
```python
def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None
```
- This function extracts the video ID from a YouTube link. YouTube videos have a unique 11-character ID.
- Whether the URL is in the format: **`https://www.youtube.com/watch?v=AbCd1234EfGh`**  or  **`https://youtu.be/AbCd1234EfGh`**.
- The regular expression searches for the 11-character ID after `v=` or a `/`.
- To fetch a transcript via the `YouTubeTranscriptApi`, you must supply just the **video ID**, not the whole URL.

### Function for Summarization
```python
def summarize_text(text):
    prompt = "Summarize this YouTube video transcript in simple points:\n\n" + text
    response = model.generate_content(prompt)
    return response.text
```
- This function sends the transcript text to Google Gemini with a prompt asking it to summarize the video in simple bullet points.
- It makes a call to Gemini and returns the summarized result. `response.text` gives us the clean text of the summary.

### Function to Save the File as `.txt`
```python
def save_summary_to_file(summary, video_id):
    filename = f"{video_id}_summary.txt"
    filepath = os.path.join("summaries", filename)
    os.makedirs("summaries", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(summary)
    return filepath
```
- This function creates a `.txt` file with the summary so that the user can download it from a link. `video_id_summary.txt` helps keep filenames unique per video. The summaries folder is automatically created if it doesn't already exist using `os.makedirs()`. The summary content is then written to the file using UTF-8 encoding.
- Twilio doesn't support long messages well. So instead of pasting a long summary in WhatsApp, you give the user a link to download it.

### Flask Routes & WhatsApp Bot Logic
```python
@app.route("/", methods=['GET', 'POST'])
def whatsapp_bot():
    if request.method == 'GET':
        return "WhatsApp bot is running."
```
- This defines the main route (/) of your Flask app.
- If the server is accessed via browser (GET request), it simply returns a plain message: "WhatsApp bot is running."
- This is useful to check if your app is online.

### WhatsApp Message Handling (POST request from Twilio)
```python
incoming_msg = request.values.get('Body', '').strip()
resp = MessagingResponse()
msg = resp.message()
```
- `incoming_msg` gets the actual text message sent by the user on WhatsApp.
- `MessagingResponse()` is part of Twilio’s library. It builds a response back to the user.
- `msg = resp.message()` is where you prepare your reply.

### Check for YouTube Link
```python
if "youtube.com" in incoming_msg or "youtu.be" in incoming_msg:
```
Checks if the message includes a YouTube link.

### Extract & Validate Video ID
```python
video_id = extract_video_id(incoming_msg)
if not video_id:
    msg.body("Invalid YouTube link. Please try again.")
    return str(resp)
```
- Uses your earlier `extract_video_id()` function.
- If a valid video ID isn’t found, it sends an error message.

### Fetch Transcript, Summarize & Send Back
```python
transcript = YouTubeTranscriptApi.get_transcript(video_id)
full_text = " ".join([t['text'] for t in transcript])
summary = summarize_text(full_text)
```
- Fetches the full transcript using the video ID.
- Joins all transcript lines into one string.
- Sends it to Gemini to get the summary.

### Save and Share the Summary
```python
filepath = save_summary_to_file(summary, video_id)
file_url = request.host_url + f"summaries/{video_id}_summary.txt"
msg.body(f"Summary ready! Download here:\n{file_url}")
```
- Saves the summary using your earlier `save_summary_to_file()` function.
- Constructs a download link using your Flask app's current URL + file path.
- Sends the user a link to download the `.txt` file.

### Catch Transcript Errors
```python
except Exception as e:
    msg.body("Failed to fetch transcript. It might be disabled or unavailable.")
```
- The transcript is not available (some videos disable captions),
- Or there’s a network or API issue.

### Handle Invalid Inputs
```python
else:
    msg.body("Please send a valid YouTube video link.")
```
If the message doesn’t contain a YouTube link, the user is informed to send a valid one.

### Return the Response
```python
return str(resp)
```
This sends the prepared response message back to Twilio → which sends it to WhatsApp.

### File Serving Route
```python
@app.route('/summaries/<path:filename>')
def serve_summary_file(filename):
    return send_from_directory(os.path.join(os.getcwd(), 'summaries'), filename)
```
- This route lets you serve the saved `.txt` file when the user clicks the link.
- It looks for the file in the `summaries/` directory and serves it for download.

### App Start
```python
if __name__ == '__main__':
    app.run(debug=True)
```
- Starts the Flask development server when you run the script.
- `debug=True` allows you to see errors more clearly during development.


For futher detail read my medium article: **[WhatsApp Bot for YouTube Video Summarization](https://medium.com/@sayedebad.777/whatsapp-bot-for-youtube-video-summarization-0509dca41906)**.
