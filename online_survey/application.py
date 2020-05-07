#!flask/bin/python
from .flaskrun import flaskrun
from flask import Flask, session, request, render_template, redirect, make_response, flash, send_file
from flask_debugtoolbar import DebugToolbarExtension
from .models import Question, Answer, Survey, Response, ResponseSet
from .database import db_session, init_db
import os
from io import BytesIO


application = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'surveys.db')
application.config['SECRET_KEY'] = b'1234' 
# application.config['DEBUG'] = True
# application.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


debug = DebugToolbarExtension(application)

# init_db()
@application.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@application.route("/select-survey")
@application.route("/")
def show_pick_survey_form():
    # start page: select a survey or create one 
    db_surveys = Survey.query.all()
    print(f"type of surveys = {type(db_surveys)}")
    print(f"{db_surveys}")
    
    return render_template("pick-survey.html", surveys=db_surveys)


@application.route("/", methods=["POST", "GET"])
def pick_survey():

    """Select a survey."""

    survey_id = request.form['survey-code']
    survey = Survey.query.filter_by(id=session.get('survey_id', None)).first()
    session['survey'] = survey
    session['survey_id'] = survey.id
    session['survey_name'] = survey.survey
    print(f"SURVEY ID >> {survey_id}\t SURVEY NAME >> {session.get('survey_name')}")
    return render_template("survey_start.html",
                        survey_name=survey.survey, instruction=survey.instruction)
    if request.form['name'] == 'create_survey':
        return redirect('/create-survey')

'''

Create Survey

'''
@application.route("/create-survey", methods=["POST"])
def create_survey():
    """ Create a page to start creating a survey on """
    return render_template("create-survey.html")

@application.route("/name-survey", methods=["POST", "GET"])
def name_survey():
    """ Give survey name and instructions """
    session['survey_name'] = request.form['survey_name']
    instruction = request.form['survey_instruction']
    
    _survey = Survey(session.get('survey_name'), instruction)
    db_session.add(_survey)
    db_session.commit()
    session['survey_id'] = _survey.id
    print(f"\t\tCREATE SURVEY: {session.get('survey_name')} ID: {_survey.id}")
    ##return "something"

    return redirect('/create-question')

@application.route("/create-question")
def create_question():
    """Go to create a question page """
    return render_template("add-question.html", survey_name = session.get('survey_name', None))

@application.route("/add-question", methods=["POST", "GET"])
def add_question():
    """ Create Questions and give them options """
    survey_name = session.get('survey_name', None)
    survey_id = session.get('survey_id', None)
    question = request.form['question']
    
    db_question = Question(survey_id, question)
    db_session.add(db_question)
    db_session.commit()

    option1 = request.form['op1']
    db_answer1 = Answer(db_question.id, option1)
    option2 = request.form['op2']
    db_answer2 = Answer(db_question.id, option2)
    option3 = request.form['op3']
    db_answer3 = Answer(db_question.id, option3)
    option4 = request.form['op4']
    db_answer4 = Answer(db_question.id, option4)

    db_session.add(db_answer1)
    db_session.add(db_answer2)
    db_session.add(db_answer3)
    db_session.add(db_answer4)
    db_session.commit()
    print(f"Survey - {survey_name}\n\tQuestion - {question}\n\tOptions - [{option1}, {option2}, {option3}, {option4}]")
    
    if request.form['next']:
        return render_template("add-question.html", survey_name = session.get('survey_name', None))
    else:
        return redirect('/post-survey')

@application.route("/post-survey", methods=["POST", "GET"])
def post_survey():
    """ Now activate the survey and make it available on the main selection page"""
    db_survey = Survey.query.filter_by(id=session.get('survey_id', None)).first()
    db_survey.active = True
    db_session.commit()

    return redirect("/")


'''

Take Survey

'''

@application.route("/begin", methods=["POST"])
def start_survey():
    ''' Generate ResponseID and Set Up '''
    session['survey_id'] = request.form['survey_id']
    response_set = ResponseSet(session.get('survey_id'))
    db_session.add(response_set)
    db_session.commit()

    session['response_set_id'] = response_set.id
    print("AAAAAAAAAAAAAAAAAAAAA OH MY GOD")
    questions, _, _ = get_survey_from_db(session.get('survey_id'))
    question_ids = [q.id for q in questions]
    question_ids.sort()
    session['question_ids'] = question_ids
    session['counter'] = 0
    return redirect("/questions/" + str(question_ids[0]))

@application.route("/answer", methods=["POST"])
def handle_question():
    """Save response and redirect to next question."""
    answer_id = request.form['answer']
    response = Response(
        session.get('response_set_id'),
        session.get('question_ids')[session['counter']],
        answer_id,
    )
    db_session.add(response)
    db_session.commit()
    session['counter'] += 1
    if (session['counter'] == len(session['question_ids'])):
        return redirect("/complete")
    else:
        return redirect(f"/questions/{session['question_ids'][session['counter']]}")


@application.route("/questions/<int:qid>")
def show_question(qid):
    """Display current question."""

    survey_id = session['survey_id']
    question = Question.query.filter_by(survey_id=survey_id, id=qid).first()
    answers = Answer.query.filter_by(question_id=question.id).all()

    # WHY DID I WRITE THIS?
    # if (not '''NO RESPONSES HAVE BEEN GIVEN YET'''):
    #     # trying to access question page too soon
    #     return redirect("/")

    return render_template("question.html", question_num=session['counter'], question=question, answers=answers)


@application.route("/complete")
def list_responses():
    """List Responses and Go back"""
    return render_template("completion.html")

@application.route("/download_survey", methods=["POST"])
def download_survey():
    print("DOWNLOADING SURVEY")
    survey_id = int(request.form["survey_id"])
    survey_name = Survey.query.filter_by(id=survey_id).first().survey
    questions, answers_per_question, responses = get_survey_from_db(survey_id)
    survey_file = ""
    survey_file_title = f"Survey '{survey_name}'"
    survey_file += survey_file_title + "\n"
    for question in questions:
        print(f"QID: {question.id}")
        survey_file += question.question + ":\n"
        for a in answers_per_question:
            if a[0].question_id == question.id:
                answers = a
            else:
                print(f"ASETID: {a[0].question_id}")
        for answer in answers:
            print(f"AID: {answer.id}")
            survey_file += "\t" + answer.answer + ": "
            response_counter = 0
            for response in responses:
                if response.question_id == question.id and response.answer_id == answer.id:
                    response_counter += 1
                else:
                    print(response.question_id, response.answer_id)
            survey_file += str(response_counter) + "\n"
    
    print(survey_file)
    return send_file(BytesIO(survey_file.encode("UTF-8")), attachment_filename=survey_file_title + ".txt")
    return redirect("/")


'''

Utils

'''


def get_survey_from_db(survey_id):
    db_questions = Question.query.filter_by(survey_id=survey_id).all()
    db_answers = []
    db_responses = []
    for question in db_questions:
        db_answers.append(Answer.query.filter_by(question_id=question.id).all())
    response_sets = ResponseSet.query.filter_by(survey_id=survey_id).all()
    for response_set in response_sets:
        db_responses += Response.query.filter_by(response_set=response_set.id).all()
    return db_questions, db_answers, db_responses

if __name__ == '__main__':
    flaskrun(application)
