import simplejson as json
from uuid import uuid4
from time import sleep
import testing.postgresql

import unittest
import kinappserver
from kinappserver import db, stellar, models


USER_ID_HEADER = "X-USERID"

class Tester(unittest.TestCase):
    '''tests the entire spend-scenario: creating an order and then redeeming it'''

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


    def test_book_and_redeem(self):
        """test creating orders"""
        offerid = '0'
        offer = {'offer_id': offerid,
                 'type': 'gift-card',
                 'domain': 'music',
                 'title': 'offer_title',
                 'desc': 'offer_desc',
                 'image_url': 'image_url',
                 'price': 2,
                 'address': 'GCORIYYEQP3ANHFT6XHMBY7VB3RH53WB5KZZHGCEXYRWCEJQZUXPGWQM',
                 'provider': 
                    {'name': 'om-nom-nom-food', 'logo_url': 'http://inter.webs/horsie.jpg'},
                }

        # add an offer
        resp = self.app.post('/offer/add',
                            data=json.dumps({
                            'offer': offer}),
                            headers={},
                            content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        # enable the offer
        resp = self.app.post('/offer/set_active',
                            data=json.dumps({
                            'offer_id': offerid,
                            'is_active': True}),
                            headers={},
                            content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        # register a user
        userid = uuid4()
        resp = self.app.post('/user/register',
            data=json.dumps({
                            'user_id': str(userid),
                            'os': 'android',
                            'device_model': 'samsung8',
                            'device_id': '234234',
                            'time_zone': '+05:00',
                            'token': 'fake_token',
                            'app_ver': '1.0'}),
            headers={},
            content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        # create the first order
        resp = self.app.post('/offer/book',
                    data=json.dumps({
                    'id': offerid}),
                    headers={USER_ID_HEADER: str(userid)},
                    content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data['status'], 'ok')
        self.assertNotEqual(data['order_id'], None)
        orderid1 = data['order_id']
        print('order_id: %s' % orderid1)

        # pay for the order but give a differet address - should fail
        print('setting memo of %s' % orderid1)
        tx_hash_wrong_address = stellar.send_kin('GCKG5WGBIJP74UDNRIRDFGENNIH5Y3KBI5IHREFAJKV4MQXLELT7EX6V', offer['price'], orderid1)
        print('tx_hash: %s' % tx_hash_wrong_address)

        # give it some time to boil
        print('sleeping 2 seconds...')
        sleep(2)

        # try to redeem the goods with the tx_hash - should fail
        print('trying to redeem with the wrong address...')
        resp = self.app.post('/offer/redeem',
                    data=json.dumps({
                    'tx_hash': tx_hash_wrong_address}),
                    headers={USER_ID_HEADER: str(userid)},
                    content_type='application/json')
        self.assertNotEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        print(data)

        # delete the order
        models.delete_order(orderid1)

        # re-create the first order
        resp = self.app.post('/offer/book',
                    data=json.dumps({
                    'id': offerid}),
                    headers={USER_ID_HEADER: str(userid)},
                    content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data['status'], 'ok')
        self.assertNotEqual(data['order_id'], None)
        orderid1 = data['order_id']
        print('order_id: %s' % orderid1)

        # pay for the order - but pay less than expected
        print('setting memo of %s' % orderid1)
        tx_hash_pay_less = stellar.send_kin(offer['address'], offer['price'] - 1, orderid1)
        print('tx_hash: %s' % tx_hash_pay_less)

        # give it some time to boil
        print('sleeping 2 seconds...')
        sleep(2)

        # try to redeem the goods - shuld fail
        print('trying to redeem with underpayed tx...')
        resp = self.app.post('/offer/redeem',
                    data=json.dumps({
                    'tx_hash': tx_hash_pay_less}),
                    headers={USER_ID_HEADER: str(userid)},
                    content_type='application/json')
        self.assertNotEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        print(data)
        
        # delete teh order
        models.delete_order(orderid1)

        # re-create the first order
        resp = self.app.post('/offer/book',
                    data=json.dumps({
                    'id': offerid}),
                    headers={USER_ID_HEADER: str(userid)},
                    content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data['status'], 'ok')
        self.assertNotEqual(data['order_id'], None)
        orderid1 = data['order_id']
        print('order_id: %s' % orderid1)

        # pay for the order - but use an invalid orderid
        print('setting memo of %s' % orderid1)
        tx_hash_other_orderid = stellar.send_kin(offer['address'], offer['price'], "other_order_id")
        print('tx_hash: %s' % tx_hash_other_orderid)

        # give it some time to boil
        print('sleeping 2 seconds...')
        sleep(2)

        # try to redeem the goods - should fail
        print('trying to redeem with unknown order_id...')
        resp = self.app.post('/offer/redeem',
                    data=json.dumps({
                    'tx_hash': tx_hash_other_orderid}),
                    headers={USER_ID_HEADER: str(userid)},
                    content_type='application/json')
        self.assertNotEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        print(data)

        # delete the order
        models.delete_order(orderid1)

        # re-create the first order
        resp = self.app.post('/offer/book',
                    data=json.dumps({
                    'id': offerid}),
                    headers={USER_ID_HEADER: str(userid)},
                    content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data['status'], 'ok')
        self.assertNotEqual(data['order_id'], None)
        orderid1 = data['order_id']
        print('order_id: %s' % orderid1)

        # pay for the order
        print('setting memo of %s' % orderid1)
        tx_hash = stellar.send_kin(offer['address'], offer['price'], orderid1)
        print('tx_hash: %s' % tx_hash)

        # give it some time to boil
        print('sleeping 2 seconds...')
        sleep(2)

        #try to redeem the goods - should work
        resp = self.app.post('/offer/redeem',
                    data=json.dumps({
                    'tx_hash': tx_hash}),
                    headers={USER_ID_HEADER: str(userid)},
                    content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        print(data)


if __name__ == '__main__':
    unittest.main()
