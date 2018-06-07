import simplejson as json
import unittest
import uuid
import time

import testing.postgresql

import kinappserver
from kinappserver import db, models, blackhawk


USER_ID_HEADER = "X-USERID"

class Tester(unittest.TestCase):

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

    def test_blackhawk(self):
        """test registration scenarios"""
        # client potal: https://clients.omnicard.com/login



        # get merchant list and merchant data

        #merchants_data = blackhawk.get_merchants_api('8488ed4948746238e314bfc5eee4a1fa')
        #merchants_data = str(merchants_data).encode('utf-8').strip()
        #print(merchants_data)


        #merchant_data = blackhawk.get_merchant_api('8488ed4948746238e314bfc5eee4a1fa', 810)
        #merchant_data = str(merchant_data).encode('utf-8').strip()
        #print(merchant_data)

        resp = self.app.post('/blackhawk/creds/init',
                            data=json.dumps({
                                'account_id': 14334,
                                'username': 'kinitapp@kik.com',
                                'password': 'Kinitapp1!',
                                'digital_signature': 'Kinit App'
                            }),
                            headers={},
                            content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        resp = self.app.post('/blackhawk/creds/refresh-token',
                            headers={},
                            content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        resp = self.app.get('/blackhawk/account/balance',
                            headers={},
                            content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        print(json.loads(resp.data))

        offer = { 'id': '0',
                  'type': 'gift-card',
                  'type_image_url': "https://s3.amazonaws.com/kinapp-static/brand_img/gift_card.png",
                  'domain': 'music',
                  'title': 'offer_title',
                  'desc': 'offer_desc',
                  'image_url': 'image_url',
                  'price': 800,
                  'address': 'the address',
                  'skip_image_test': True,
                  'provider':
                    {'name': 'om-nom-nom-food', 'image_url': 'http://inter.webs/horsie.jpg'},
                }

        resp = self.app.post('/offer/add',
                            data=json.dumps({
                            'offer': offer}),
                            headers={},
                            content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        # enable offer 0
        resp = self.app.post('/offer/set_active',
                            data=json.dumps({
                            'id': offer['id'],
                            'is_active': True}),
                            headers={},
                            content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        # add an instance of goods
        resp = self.app.post('/good/add',
                    data=json.dumps({
                    'offer_id': offer['id'],
                    'good_type': 'code',
                    'value': 'abcd'}),
                    headers={},
                    content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        print(models.list_all_goods())
        print(models.list_all_bh_cards())

        resp = self.app.post('/blackhawk/cards/replenish',
                            headers={},
                            content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        print(json.loads(resp.data))

        resp = self.app.post('/blackhawk/cards/replenish',
                            headers={},
                            content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        print(json.loads(resp.data))


        time.sleep(60)

        resp = self.app.post('/blackhawk/cards/replenish',
                            headers={},
                            content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        print(json.loads(resp.data))


        time.sleep(60)

        resp = self.app.post('/blackhawk/cards/replenish',
                            headers={},
                            content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        print(json.loads(resp.data))


        time.sleep(60)

        resp = self.app.post('/blackhawk/cards/replenish',
                            headers={},
                            content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        print(json.loads(resp.data))

        time.sleep(60)

        resp = self.app.post('/blackhawk/cards/replenish',
                             headers={},
                             content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        print(json.loads(resp.data))

        time.sleep(60)

        resp = self.app.post('/blackhawk/cards/replenish',
                             headers={},
                             content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        print(json.loads(resp.data))

        time.sleep(60)

        resp = self.app.post('/blackhawk/cards/replenish',
                             headers={},
                             content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        print(json.loads(resp.data))

        # print goods
        resp = self.app.get('/good/inventory')
        self.assertEqual(resp.status_code, 200)
        print(json.loads(resp.data))

        print(models.list_all_goods())
        print(models.list_all_bh_cards())

if __name__ == '__main__':
    unittest.main()