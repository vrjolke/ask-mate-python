from flask import Flask, render_template, request, redirect, url_for

import data_manager
from connection import import_database

app = Flask(__name__)


@app.route('/')
@app.route('/question')
def index():
    return redirect('/list')


@app.route('/list')
def route_list():
    questions = connection.import_database("question")
    data_manager.convert_unix_timestamp(questions)
    data_manager.sort_data(questions, "submission_time", 'desc')
    return render_template('list.html', questions=questions)

@app.route('/form')
def route_form():
    return render_template('form.html')


@app.route('/list', methods=['POST'])
def route_save_question():
    return redirect('/')



@app.route("/question/<int:question_id>")
def route_question(question_id):
    every_question = import_database("question")
    every_answer = import_database("answer")

    current_answers = data_manager.get_answers_for_question(question_id, every_answer)
    current_question = every_question[question_id]

    return render_template('question.html', question_id=question_id,
                           question=current_question, answers=current_answers)


if __name__ == '__main__':
    app.static_folder = 'static'
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )
