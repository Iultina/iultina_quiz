from datetime import datetime

from app import db


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    question_text = db.Column(db.String(500))
    answer_text = db.Column(db.String(200))
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    added_date = db.Column(db.DateTime, default=datetime.utcnow)
