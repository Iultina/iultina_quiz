from datetime import datetime

import requests
from flask import jsonify, request

from app import app, db
from app.models import Question
from typing import Any, Dict, List, Optional, Tuple, Union

from flask.wrappers import Response

API_URL = 'https://jservice.io/api/random?count='


@app.route('/api/questions', methods=['POST'])
def get_question() -> Union[Response, Tuple[Dict[str, Any], int]]:
    '''Получает вопросы и сохраняет их в базе данных.'''
    data: Dict[str, Any] = request.json
    questions_num: Optional[int] = data.get('questions_num')
    if not questions_num:
        return jsonify({'error': 'questions_num is required'}), 400

    questions: List[Dict[str, Any]] = []
    while len(questions) < questions_num:
        response: Response = requests.get(API_URL + '1')
        question_data: Dict[str, Any] = response.json()[0]
        exists: Optional[Question] = Question.query.get(question_data['id'])
        if not exists:
            creation_date_str: str = question_data['created_at']
            creation_date: datetime = (
                datetime.fromisoformat(
                    creation_date_str.replace('Z', '+00:00')
                )
            )
            new_question: Question = Question(
                id=question_data['id'],
                question_text=question_data['question'],
                answer_text=question_data['answer'],
                creation_date=creation_date
            )
            db.session.add(new_question)
            questions.append(new_question)

    db.session.commit()

    last_question: Optional[Question] = (
        Question.query.order_by(Question.added_date.desc()).offset(1).first()
    )
    if last_question:
        return jsonify({
            'id': last_question.id,
            'question': last_question.question_text,
            'answer': last_question.answer_text,
            'created_at': last_question.creation_date
        })
    else:
        return jsonify({}), 200
