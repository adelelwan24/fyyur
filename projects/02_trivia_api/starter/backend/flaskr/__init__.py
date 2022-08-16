import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import  or_ , desc
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Header','Content-Type,Authorization,true')
    response.headers.add('Access-Control_Allow-Methods' ,'GET,POST,DELETE,PATCH,OPTIONS')
    return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    cats = Category.query.all()
    if cats is None or len(cats) == 0:
      abort(422)
    data = {}
    for cat in cats:
      data[cat.id] = cat.type
    result = {}
    result['categories'] = data
    return jsonify(result)

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions')
  def get_questions():
    page = request.args.get('page', 1 , type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = Question.query.order_by(desc('id')).all()
  
    # try:
    ques = [q.format() for q in questions]
    selection = ques[start:end]

    # print(ques,'\n', selection)

    if len(selection)  == 0:
      abort(404)
      
    data = {}
    data['questions'] = selection
    data['totalQuestions'] = Question.query.count()

    cats = Category.query.all()
    categories = {}
    for cat in cats:
      categories[cat.id] = cat.type
    data['categories'] = categories
    data['currentCategory'] = 'All'    # didn't solve yet
    
      
    return jsonify(data)


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    selected = Question.query.filter(Question.id == id ).one_or_none()

    if selected == None:
      abort(404)

    try:
      selected.delete()
      return jsonify({'success' : True})
    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''


  @app.route('/questions', methods=['POST'])
  def create_questions():
    body = request.get_json()

    question = body.get('question',None)
    answer = body.get('answer', None)
    category = body.get('category', None)
    difficulty = body.get('difficulty', None)

    search = body.get('searchTerm', None)

    if search:
      selection = Question.query.join(
        Category, Question.category == Category.id).order_by(Question.id).filter(or_(
        Question.question.ilike('%{}%'.format(search)), 
        Category.type.ilike('%{}%'.format(search)))).all()

      questions = [selected.format() for selected in selection]

      totalQuestions = Question.query.count()
      currentCategory = 'All'
      return jsonify({
        'questions': questions ,
        'totalQuestions': totalQuestions,
        'currentCategory' : currentCategory})
    else:
      try:
        if question == None or answer == None or category == None or difficulty == None:
          abort(422)
        Q = Question(question=question,answer=answer,category=category, difficulty=difficulty)
        Q.insert()
        return jsonify({'success' : True})
      except:
        abort(422)



  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:catId>/questions')
  def questions_of_category(catId):
    selection = Question.query.filter(Question.category == catId).all()

    if len(selection) == 0:
      abort(404)
    questions = [selected.format() for selected in selection]
    return jsonify({
      'questions' : questions,
      'totalQuestions' : Question.query.count(),
      'currentCategory' : 'All'
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  
  @app.route('/quizzes', methods=['POST'])
  def get_quizz():
    body = request.get_json()

    try:
      pre = body.get('previous_questions', [])
      categoryObject = body.get('quiz_category', 0)
      category = categoryObject['id']

      if category == 0:
        question = Question.query.filter(Question.id.notin_(pre)).first()
      else:
        question = Question.query.filter(
          Question.category == category).filter(Question.id.notin_(pre)).first()

      if question == None:
        question = False
      else:
        question = question.format()

      return jsonify({
        'question' : question
      })
    except:
      abort(422)


  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def error_handler_404(error):
    return jsonify({
      'code' : 404,
      'message' : 'Page not found'
      }), 404

  @app.errorhandler(422)
  def error_handler_422(error):
    return jsonify({'code' : 422,
    'message' : 'Unprocessable Entity',
    }), 422

  @app.errorhandler(500)
  def error_handler_500(error):
    return jsonify({'code' : 500,
    'message' : 'Server side error',
    }), 404

  return app

    