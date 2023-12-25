from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import sqlite3
import os
from dotenv import load_dotenv
from textblob import TextBlob

app = Flask(__name__)
CORS(app)
load_dotenv()

# Database setup
# def init_db():
#     conn = sqlite3.connect('chatbot.db')
#     c = conn.cursor()
#     c.execute('''CREATE TABLE IF NOT EXISTS chat_history (user_id TEXT, prompt TEXT, response TEXT)''')
#     conn.commit()
#     conn.close()
#
# init_db()

my_api_key = os.environ.get('OPENAI_API_KEY')


def analyze_sentiment(text):
    testimonial = TextBlob(text)
    polarity = testimonial.sentiment.polarity  # -1 to 1 where -1 is negative and 1 is positive
    return polarity


def chat_with_openai(user_id, conversation):

    user_prompt = conversation[-1]

    sentiment_score = analyze_sentiment(user_prompt['text'])
    sentiment = ""

    empathetic_prefix = ""
    if sentiment_score >= 0.6:
        empathetic_prefix = "The user is ecstatic! Keep up the positive energy."
        sentiment = "Very Happy"
    elif 0.2 <= sentiment_score < 0.6:
        empathetic_prefix = "Awesome, the user is feeling great. Keep him happy!"
        sentiment = "Happy"
    elif 0.1 <= sentiment_score < 0.2:
        empathetic_prefix = "The user seems content. Perhaps there's room for even more joy?"
        sentiment = "Slightly Happy"
    elif -0.1 < sentiment_score < 0.1:
        empathetic_prefix = "The user is feeling fine. Try to make him more happy."
        sentiment = "Neutral"
    elif -0.4 < sentiment_score <= -0.1:
        empathetic_prefix = "The user seems a bit down. Encourage them to share more."
        sentiment = "Slightly Unhappy"
    elif -0.6 < sentiment_score <= -0.4:
        empathetic_prefix = "The user is quite unhappy. Offer support and a listening ear."
        sentiment = "Unhappy"
    else:  # sentiment_score <= -0.6
        empathetic_prefix = "The user clearly feels very sad, tell him he should take a hot bubble bath."
        sentiment = "Very Unhappy"

    # conn = sqlite3.connect('chatbot.db')
    # c = conn.cursor()
    # c.execute("SELECT response FROM chat_history WHERE user_id = ?", (user_id,))
    # past_conversation = [row[0] for row in c.fetchall()]
    # conn.close()
    messages = []
    if len(conversation) <= 1:
        messages.append({
            'role': 'system',
            'content': 'You are a helpful assistant.'
        })
    # messages.extend([{'role': 'assistant', 'content': message} for message in past_conversation])
    for message in conversation:
        print(message['sender'], message['text'])
        messages.append({
            'role': message['sender'],
            'content': message['text']
        })

    if empathetic_prefix:
        messages.append({'role': 'system', 'content': empathetic_prefix})

    api_key = my_api_key
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    data = {
        'model': 'gpt-3.5-turbo',
        'messages': messages
    }

    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        chat_response = result['choices'][0]['message']['content']

        # conn = sqlite3.connect('chatbot.db')
        # c = conn.cursor()
        # c.execute("INSERT INTO chat_history (user_id, prompt, response) VALUES (?, ?, ?)", (user_id, user_prompt['text'], chat_response))
        # conn.commit()
        # conn.close()

        return chat_response, sentiment_score, sentiment
    else:
        return {'error': response.json()}


@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_id = data.get('userId')
    prompt = data.get('prompt')
    response, sentiment_score, sentiment = chat_with_openai(user_id, prompt)
    return jsonify({'response': response, 'sentiment_score': sentiment_score, 'sentiment': sentiment})


if __name__ == '__main__':
    app.run(debug=True)
