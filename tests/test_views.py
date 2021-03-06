from flask.ext.testing import TestCase
import unittest, os
import gb
import copy
from flask import Flask, json, jsonify
from gb import app, db, session
from gb.models import User,Track

import logging
logging.basicConfig()
LOG = logging.getLogger(__name__)

class TrackTestCase(TestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app

    def setUp(self):
    	app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        # Use in-memory database
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

        # we set self to the app instance
        self.app = app.test_client()
        db.create_all()

        #
        user_header = []

    def tearDown(self):
    	db.session.remove()
        db.drop_all()

    def testGetView(self):
        LOG.info("Testing getting view endpoint /views with GET")
        self.createTestUser()
        self.uploadTestWig()
        self.createTestTrack()
        self.createTestView()

        response = self.app.get('/api/views/1',
            headers=self.user_header
        )
        self.assert200(response)
        
        data = json.loads(response.get_data())
        self.assertEqual(data.get('view_name'), 'TEST-VIEW')
        self.assertEqual(data.get('user_id'), 1)
        self.assertEqual(data.get('track_ids'), [1])

    def testGetDataView(self):
        LOG.info("Testing getting view endpoint /views/data with GET")
        self.createTestUser()
        self.uploadTestWig()
        self.createTestTrack()
        self.createTestView()

        response = self.app.get('/api/views/data/1',
            headers=self.user_header
        )
        self.assert200(response)
        
        data = json.loads(response.get_data())
        self.assertEqual(data.get('view_name'), 'TEST-VIEW')
        self.assertEqual(data.get('user_id'), 1)
        self.assertTrue(data.has_key('view_tracks'))

    def testPutDataView(self):
        LOG.info("Testing updating data view endpoint /views/data with PUT")
        self.createTestUser()
        self.uploadTestWig()
        self.createTestTrack()
        self.createTestView()

        data = self.getTestDataView()
        data_copy = copy.deepcopy(data)

        for view_track in data.get('view_tracks'):
            display_array = view_track.get('display_params')
            display_array['sticky'] = True
            display_array['hidden'] = True
            display_array['y_max'] = 100

        response = self.app.put('/api/views/data/1',
            headers = self.user_header,
            data = json.dumps(data),
            content_type='application/json'
        )

        self.assert200(response)
        self.assertNotEqual(json.loads(response.get_data()),data_copy)

    def testCreateView(self):
        LOG.info("Testing create view endpoint /views with POST")

        # first create a user
        self.createTestUser()
        self.uploadTestWig()
        self.createTestTrack()

        # Send post request
        response = self.app.post('/api/views', 
            data=json.dumps({
                'track_ids': [1], 
                'view_name': 'TEST-VIEW'
            }), 
            content_type='application/json',
            headers=self.user_header)

        self.assert200(response)
        self.assertEqual(json.loads(response.get_data()).get('view_id'),1)
    
    def testUpdateView(self):
        LOG.info("Testing updating view endpoint /views with PUT")

        # first create a user
        self.createTestUser()
        self.uploadTestWig()
        self.createTestTrack()
        self.createAnotherTestTrack()
        self.createTestView()

        view = self.getTestView()

        response = self.app.put('/api/views/1', 
            data=json.dumps({
                'track_ids': [1,2],
                'view_name': 'NEW-NAME'
            }), 
            content_type='application/json',
            headers=self.user_header
        )

        self.assert200(response)

        data = json.loads(response.get_data())
        self.assertEqual(data.get('view_name'), 'NEW-NAME')
        self.assertEqual(data.get('user_id'), 1)
        self.assertEqual(data.get('track_ids'), [1,2])

    def testDeleteView(self):
        LOG.info("Testing delet view endpoint /views with DELETE")
        self.createTestUser()
        self.uploadTestWig()
        self.createTestTrack()
        self.createTestView()

        # delete it
        response = self.app.delete('/api/views/1',
            headers=self.user_header
        )

        # ensure delete happened correctly
        self.assert200(response)
        data = json.loads(response.get_data())
        self.assertEqual(data, {})

        # last make sure it is actually gone
        response = self.app.get('/api/views/1',
            headers=self.user_header
        )

        self.assert404(response)

    def createTestUser(self):
        response = self.app.post('/api/users', 
            data=json.dumps({'username': 'kyle', 'email': 'kyle@email.com','password':'SECRET'}), 
            content_type='application/json')

        response = self.app.post('api/auth',
                                 data=json.dumps({'username':'kyle', 'password':'SECRET'}),
                                 content_type='application/json')

        JSON = json.loads(response.get_data())
        token = str(JSON.get('token'))
        self.user_header = [('Authorization','Bearer ' + token)]

    def createTestTrack(self):
        response = self.app.post('/api/tracks', 
            data=json.dumps({
                'track_name': 'kyles track', 
                'data_type': 'wig',
                'data_id':1,
                'file_name':'mywig.wig'
            }), 
            content_type='application/json',
            headers=self.user_header)

    def createAnotherTestTrack(self):
        response = self.app.post('/api/tracks', 
            data=json.dumps({
                'track_name': 'kyles track', 
                'data_type': 'wig',
                'data_id':2,
                'file_name':'mywig.wig'
            }), 
            content_type='application/json',
            headers=self.user_header)

    def getTestTrack(self):
        response = self.app.get('/api/tracks/1',
            headers=self.user_header
        )
        track = json.loads(response.get_data())
        return track

    def uploadTestWig(self):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        self.app.post('/api/files',
            data=dict(
                file=(open(test_dir+"/../var/shortWig.wig", 'rb'), 'test.wig'),
                type="wig"
            ), 
            follow_redirects=True,
            headers=self.user_header
        )

    def createTestView(self):
        # Send post request
        response = self.app.post('/api/views', 
            data=json.dumps({
                'track_ids': [1], 
                'view_name': 'TEST-VIEW'
            }), 
            content_type='application/json',
            headers=self.user_header
        )

    def getTestView(self):
        response = self.app.get('/api/views/1',
            headers=self.user_header
        )
        view = json.loads(response.get_data())
        return view

    def getTestDataView(self):
        response = self.app.get('/api/views/data/1',
            headers=self.user_header
        )
        self.assert200(response)
        data = json.loads(response.get_data())
        return data

if __name__ == '__main__':
    unittest.main()
