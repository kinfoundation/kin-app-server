from time import sleep
import unittest
import uuid

import simplejson as json
import testing.postgresql

import kinappserver
from kinappserver import db


USER_ID_HEADER = "X-USERID"


class Tester(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        #overwrite the db name, dont interfere with stage db data
        self.postgresql = testing.postgresql.Postgresql()
        kinappserver.app.config['SQLALCHEMY_DATABASE_URI'] = self.postgresql.url()
        kinappserver.app.testing = True
        self.app = kinappserver.app.test_client()
        db.drop_all()
        db.create_all()


    def tearDown(self):
        self.postgresql.stop()

    def test_task_results(self):
        """test storting task reults"""

        # add a task
        task0 = {
          'id': '0', 
          'title': 'do you know horses?',
          'desc': 'horses_4_dummies',
          'type': 'questionnaire',
          'price': 1,
          'skip_image_test': True,
          'min_to_complete': 2,
          'start_date': '2013-05-11T21:23:58.970460+00:00',
          'tags': ['music', 'crypto', 'movies', 'kardashians', 'horses'],
          'provider': 
            {'name': 'om-nom-nom-food', 'image_url': 'http://inter.webs/horsie.jpg'},
          'items': [
            {
             'id': '435',
             'text': 'what animal is this?',
             'type': 'textimage',
                 'results': [
                        {'id': '235',
                         'text': 'a horse!',
                         'image_url': 'cdn.helllo.com/horse.jpg'},
                            {'id': '2465436',
                         'text': 'a cat!',
                         'image_url': 'cdn.helllo.com/kitty.jpg'},
                         ],
            }]
        }




        resp = self.app.post('/task/add',
                            data=json.dumps({
                            'task': task0}),
                            headers={},
                            content_type='application/json')
        self.assertEqual(resp.status_code, 200)


        userid = uuid.uuid4()

        # register an android with a token
        resp = self.app.post('/user/register',
                            data=json.dumps({
                            'user_id': str(userid),
                            'os': 'android',
                            'device_model': 'samsung8',
                            'device_id': '234234',
                            'time_zone': '05:00',
                            'token': 'fake_token',
                            'app_ver': '1.0'}),
                            headers={},
                            content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        db.engine.execute("""update public.push_auth_token set auth_token='%s' where user_id='%s';""" % (str(userid), str(userid)))

        resp = self.app.post('/user/auth/ack',
                             data=json.dumps({
                                 'token': str(userid)}),
                             headers={USER_ID_HEADER: str(userid)},
                             content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        # using sql, insert task results for task_id 0
        db.engine.execute("""insert into public.user_task_results values('%s','%s','%s');""" % (str(userid), '0', json.dumps({'a': '1'})))

        # get the user's current tasks
        headers = {USER_ID_HEADER: userid}
        resp = self.app.get('/user/tasks', headers=headers)
        data = json.loads(resp.data)
        print('data: %s' % data)
        self.assertEqual(resp.status_code, 200)
        print('next task id: %s' % data['tasks'][0]['id'])
        print('next task start date: %s' % data['tasks'][0]['start_date'])
        self.assertEqual(data['tasks'][0]['id'], '0')


        # send task results
        resp = self.app.post('/user/task/results',
                            data=json.dumps({
                            'id': '0',
                            'address': 'GCYUCLHLMARYYT5EXJIK2KZJCMRGIKKUCCJKJOAPUBALTBWVXAT4F4OZ',
                            'results': {'2234': 'werw', '5345': '345345'},
                            'send_push': False
                            }),
                            headers={USER_ID_HEADER: str(userid)},
                            content_type='application/json')
        print('post task results response: %s' % json.loads(resp.data))
        self.assertEqual(resp.status_code, 200)



if __name__ == '__main__':
    unittest.main()