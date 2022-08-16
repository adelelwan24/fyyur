import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

from flaskr import create_app
from models import setup_db, Question, Category

password = os.getenv('PASSS', '')
class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres',password,'localhost:5000', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        print(res)
        data = json.loads(res.data)
        print(data)

        self.assertEqual(res.status_code , 200)
        self.assertTrue(data['categories'])

    # def test_422_get_categories(self):
    #     res = self.client().get('/categories?page=100')
    #     # data = json.loads(res.data)

    #     self.assertEqual(res.status_code , 422)


    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['currentCategory'])

    def test_404_get_questions_requesting_pages_beyond_valid(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['code'], 404)
        self.assertEqual(data['message'] ,'Page not found')



    def test_create_questions(self):
        payload = {
            'question' : 'Are you a robot?',
            'answer' : 'No, I am not a robot',
            'category' : 2,
            'difficulty' : 3}
        res = self.client().post('/questions', json=payload) 
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_search_questions(self):
        payload = {'searchTerm': 'who'}
        res = self.client().post('/questions', json=payload)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['currentCategory'])

    def test_create_question_if_any_of_the_data_is_missing(self):
        payload = {
            'question' : 'Are you a robot?',
            'answer' : 'No, I am not a robot',
            'category' : 2
            }
        res = self.client().post('/questions', json=payload) 
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)

    
    def test_delete_question(self):
        id = Question.query.order_by(desc(Question.id)).first().id
        res = self.client().delete(f'/questions/{id}')
        data = json.loads(res.data)

        q = Question.query.filter(Question.id == id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(q, None)

    def test_404_failed_to_delete_question_doesnot_exist(self):
        res = self.client().delete('/questions/10000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,404 )
        self.assertEqual(data['code'], 404)
        self.assertEqual(data['message'] ,'Page not found')


    def test_get_questions_of_category_by_id(self):
        res = self.client().get('/categories/3/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['currentCategory'])

    def test_404_questions_of_category_by_invalid_id(self):
        res = self.client().get('/categories/231/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)

    def test_get_quizzes(self):
        payload = {
            'previous_questions' : [12,14,13,15],
            'quiz_category' : {'type': 'Art','id' : 3}}
        res = self.client().post('/quizzes', json=payload)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(data['question'])

    def test_422_get_quizzes_with_bad_or_missing_prameters(self):
        payload = {
            'previous_questions' : [1,2,3,4,5,6,7],
            # 'quiz_category' : 23
            }
        res = self.client().post('/quizzes', json=payload)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertTrue(data['message'])
    
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()