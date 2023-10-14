from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests

# Initialize Flask app
app = Flask(__name__)

# Configuration for SQLite database
DATABASE_URI = "sqlite:///iultina_quiz.db"
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy instance
db = SQLAlchemy(app)

# Define Question model
class Question(db.Model): 
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)  # Use ID from the API 
    question_text = db.Column(db.String(500)) 
    answer_text = db.Column(db.String(200)) 
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    added_date = db.Column(db.DateTime, default=datetime.utcnow)  # Дата добавления вопроса в БД

# API endpoint to get questions
API_URL = "https://jservice.io/api/random?count=" 
@app.route('/api/questions', methods=['POST'])
def get_question(): 
    data = request.json 
    questions_num = data.get('questions_num') 
    if not questions_num: 
        return jsonify({"error": "questions_num is required"}), 400 

    questions = [] 
    while len(questions) < questions_num: 
        response = requests.get(API_URL + "1") 
        question_data = response.json()[0] 
        exists = Question.query.get(question_data["id"])
        if not exists:
            creation_date_str = question_data['created_at']
            creation_date = datetime.fromisoformat(creation_date_str.replace('Z', '+00:00'))
            new_question = Question(
                id=question_data["id"], 
                question_text=question_data["question"], 
                answer_text=question_data["answer"], 
                creation_date=creation_date 
            ) 
            db.session.add(new_question) 
            questions.append(new_question)

    db.session.commit() 

    last_question = Question.query.order_by(Question.added_date.desc()).offset(1).first() 
    if last_question: 
        return jsonify({ 
            "id": last_question.id, 
            "question": last_question.question_text, 
            "answer": last_question.answer_text, 
            "created_at": last_question.creation_date 
        }) 
    else: 
        return jsonify({}), 200 

# Run the app
if __name__ == '__main__': 
    with app.app_context(): 
        db.create_all() 
    app.run(debug=True)
