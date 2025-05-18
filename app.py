from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai
import os

app = Flask(__name__)

# Configure Gemini LLM
genai.configure(api_key='AIzaSyDIwyRIoy5npx_qEa4p-VKTLSWfUIkymMw')
model = genai.GenerativeModel('gemini-1.5-flash-002')

# Define prompt templates for various queries
PROMPT_TEMPLATES = {
    "flight_status": "You are an airline customer support bot. A customer asked about flight status:\n\nQuestion: {query}\n\nPlease provide a concise and friendly answer.",
    "baggage_inquiry": "You are an airline customer support bot. A customer asked about baggage policies or baggage issues:\n\nQuestion: {query}\n\nPlease provide a helpful and polite response.",
    "ticket_booking": "You are an airline customer support bot. A customer wants to book or inquire about tickets:\n\nQuestion: {query}\n\nPlease guide the customer clearly and politely.",
    "complaints": "You are an airline customer support bot. A customer has a complaint:\n\nComplaint: {query}\n\nApologize sincerely and provide assistance information.",
    "general": "You are an airline customer support bot. The customer asked:\n\nQuestion: {query}\n\nProvide a helpful and friendly answer."
}

# Simple intent detection based on keywords
def detect_intent(message):
    text = message.lower()
    if any(word in text for word in ["flight status", "flight", "delay", "departure", "arrival"]):
        return "flight_status"
    elif any(word in text for word in ["baggage", "luggage", "bag", "carry-on", "lost baggage", "baggage claim"]):
        return "baggage_inquiry"
    elif any(word in text for word in ["book", "booking", "ticket", "reserve", "reservation", "buy ticket"]):
        return "ticket_booking"
    elif any(word in text for word in ["complaint", "problem", "issue", "bad", "poor service", "angry", "frustrated"]):
        return "complaints"
    else:
        return "general"

# Generate response using Gemini LLM
def generate_response(intent, user_message):
    prompt = PROMPT_TEMPLATES[intent].format(query=user_message)
    response = model.generate_content(prompt)
    return response.text.strip()

@app.route("/", methods=['GET', 'POST'])
def whatsapp_bot():
    if request.method == 'GET':
        return "Airline Customer Support WhatsApp bot is running."

    incoming_msg = request.values.get('Body', '').strip()
    resp = MessagingResponse()
    msg = resp.message()

    if not incoming_msg:
        msg.body("Hi! Please type your question or concern related to your flight, baggage, ticket booking, or complaints.")
        return str(resp)

    intent = detect_intent(incoming_msg)
    try:
        answer = generate_response(intent, incoming_msg)
        msg.body(answer)
    except Exception as e:
        msg.body("Sorry, something went wrong while processing your request. Please try again later.")

    return str(resp)

if __name__ == '__main__':
    app.run(debug=True)
