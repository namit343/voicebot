import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import openai
import tempfile
import base64

# Load environment variables from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

# --- Personal Answers Dictionary ---
MY_ANSWERS = {
    "life story": (
        "My name is Namit Dasappanavar, I’m 22 years old and currently based in Navi Mumbai. "
        "I grew up in Karnataka and am passionate about technology, AI, and making a positive impact through innovation. "
        "I recently graduated from VIT Vellore with a B.Tech in Information Technology."
    ),
    "superpower": (
        "My #1 superpower is my ability to learn new technologies rapidly and apply them creatively to solve real-world problems."
    ),
    "areas to grow": (
        "I want to improve my public speaking, deepen my AI expertise, and learn more about product management and leadership."
    ),
    "misconception": (
        "People sometimes think I’m quiet, but I’m actually very observant and thoughtful, and I contribute deeply to team discussions."
    ),
    "boundaries": (
        "I push my boundaries by setting ambitious goals, seeking feedback, and constantly challenging myself with new projects and technologies."
    ),
    "why home.llc": (
        "I want to join Home.LLC because I’m excited about the intersection of AI and real-world impact, and I believe my skills in agentic AI and cloud platforms can contribute meaningfully to your mission."
    ),
    "proudest achievement": (
        "One of my proudest achievements was leading a team to develop a Deep Q-Network model for optimizing urban traffic signals, which significantly reduced congestion and emissions in simulations."
    ),
    "greatest strength": (
        "My greatest strength is my ability to stay calm and focused under pressure, which helps me deliver high-quality results even in challenging situations."
    ),
    "biggest weakness": (
        "I sometimes take on too many tasks at once, but I've learned to prioritize better and delegate when necessary."
    ),
    "team environment": (
        "My ideal team environment is collaborative, supportive, and encourages open communication and knowledge sharing."
    ),
    "handle failure": (
        "I treat failure as a learning opportunity. I reflect on what went wrong, seek feedback, and use those lessons to improve myself and my work."
    ),
    "motivation": (
        "I'm motivated by the opportunity to solve meaningful problems, learn continuously, and work with talented people who challenge me to grow."
    ),
    "outside work": (
        "Outside of work, I enjoy reading about new tech trends, playing chess, and exploring new places in and around Navi Mumbai."
    ),
    # Add more as you see fit!
}

def find_personal_answer(user_text):
    user_text_lower = user_text.lower()
    for key, answer in MY_ANSWERS.items():
        if key in user_text_lower:
            return answer
    return None

@app.route('/ask', methods=['POST'])
def ask():
    try:
        audio_file = request.files['audio']
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp:
            audio_file.save(temp.name)
            temp.flush()
            with open(temp.name, "rb") as af:
                transcript = openai.audio.transcriptions.create(
                    file=af,
                    model="whisper-1"
                )
            user_text = transcript.text

        # --- Use personal answer if available ---
        personal_answer = find_personal_answer(user_text)
        if personal_answer:
            answer = personal_answer
        else:
            # --- System prompt tailored to Namit Dasappanavar ---
            system_prompt = (
                "You are Namit Dasappanavar, a 22-year-old AI enthusiast and recent Information Technology graduate from VIT Vellore, currently based in Navi Mumbai. "
                "You have experience in AI, agentic systems, cloud platforms, and have led technical teams and projects, including optimizing urban traffic with deep reinforcement learning. "
                "Respond to interview questions as yourself: be concise, honest, and highlight your strengths, growth areas, and unique experiences from your education, leadership roles, and technical projects. "
                "Make sure your answers reflect your passion for technology, learning, and real-world impact."
            )
            chatgpt_response = openai.chat.completions.create(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text}
                ]
            )
            answer = chatgpt_response.choices[0].message.content

        # --- Text-to-Speech (TTS) ---
        tts_response = openai.audio.speech.create(
            model="tts-1",
            voice="onyx",
            input=answer
        )
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tts_file:
            tts_file.write(tts_response.content)
            tts_file.flush()
            with open(tts_file.name, "rb") as f:
                audio_base64 = base64.b64encode(f.read()).decode('utf-8')

        return jsonify({
            "transcript": user_text,
            "answer": answer,
            "audio_base64": audio_base64
        })

    except Exception as e:
        print("Error in /ask:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
