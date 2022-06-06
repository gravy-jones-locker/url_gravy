import short_url

from fastapi.testclient import TestClient
from url_gravy import queries

def configure_test_queries():
    for attr in dir(queries):
        if not attr.endswith('SQL'):
            continue
        query = getattr(queries, attr).replace('urls', 'urls_test')
        setattr(queries, attr, query)

configure_test_queries()  # Insert 'urls_test' table name into all queries

from config import AUTO_SUFFIX_LEN, BASE_URL
from url_gravy.database import Database
from url_gravy.webapp import app
from url_gravy.shortener import Shortener

TEST_SUFFIX = short_url.encode_url(342234, AUTO_SUFFIX_LEN)
TEST_DB_ROW = {"suffix": TEST_SUFFIX, "target": "https://google.com"}
TEST_PARAMS = {"suffix": "google_pls", "target": "https://google.com"}

db = Database()

class TestEndpoints:

    def setup_class(self):
        self.client = TestClient(app)
    
    def teardown_method(self):
        db.delete_records()

    def test_shortening(self):
        resp = self.client.post('/shorten_url', json=TEST_PARAMS)
        assert resp.status_code == 200
        assert resp.json() == {"short_url": BASE_URL + '/google_pls'}

    def test_duplicate_shortening(self):
        db.create_record(**TEST_PARAMS)
        resp = self.client.post('/shorten_url', json=TEST_PARAMS)
        assert resp.status_code == 400
        assert resp.json()["detail"] == 'This suffix is not available'

    def test_bad_suffix_shortening(self):
        resp = self.client.post('/shorten_url', json=TEST_DB_ROW)
        assert resp.status_code == 400
        assert resp.json()["detail"] == 'This suffix is not available'

    def test_redirection(self):
        db.create_record('google_pls', 'https://google.com')
        resp = self.client.get('/google_pls', allow_redirects=False)
        assert resp.status_code == 303
        assert resp.headers['Location'] == 'https://google.com'

class TestShortener:

    def setup_method(self):
        db.create_record(**TEST_DB_ROW)
    
    def teardown_method(self):
        db.delete_records()

    def test_user_validation(self):
        assert Shortener().validate_user_suffix('!$*&^%$') is True
        long_val = 'g' * (AUTO_SUFFIX_LEN + 1)
        assert Shortener().validate_user_suffix(long_val) is True
        suffix = short_url.encode_url(789087, AUTO_SUFFIX_LEN)
        assert Shortener().validate_user_suffix(suffix) is False
    
    def test_suffix_generation(self):
        last_id = db.get_last_record()["id"]
        suffix = short_url.encode_url(last_id+1, AUTO_SUFFIX_LEN)
        assert Shortener().generate_suffix() == suffix
    
    def test_duplicate_detection(self):
        assert Shortener().update_db(**TEST_DB_ROW) is False
