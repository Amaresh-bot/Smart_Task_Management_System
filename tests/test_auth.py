import unittest
from app import create_app
from app.extensions import db
from app.models.user import User

class TestAuthModule(unittest.TestCase):
    def setUp(self):
        """
        Executes before every test.
        Sets up the test client and initializes an in-memory SQLite database.
        """
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Build test tables
        db.create_all()

    def tearDown(self):
        """
        Executes after every test.
        Cleans up active database sessions and drops tables.
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_registration_success(self):
        """Tests successful registration with valid inputs."""
        payload = {
            "username": "tester",
            "password": "securepassword123"
        }
        response = self.client.post("/api/auth/register", json=payload)
        data = response.get_json()
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["user"]["username"], "tester")
        
        # Verify persistence in DB
        user = User.query.filter_by(username="tester").first()
        self.assertIsNotNone(user)

    def test_registration_validation_checks(self):
        """Tests username and password length constraints."""
        # Username too short
        res1 = self.client.post("/api/auth/register", json={"username": "te", "password": "password"})
        self.assertEqual(res1.status_code, 400)
        
        # Password too short
        res2 = self.client.post("/api/auth/register", json={"username": "tester", "password": "123"})
        self.assertEqual(res2.status_code, 400)

    def test_registration_duplicate_username(self):
        """Tests that duplicate usernames are rejected."""
        # Create initial user
        user = User(username="tester")
        user.set_password("securepassword")
        db.session.add(user)
        db.session.commit()
        
        # Attempt to register duplicate username
        payload = {
            "username": "tester",
            "password": "anotherpassword"
        }
        response = self.client.post("/api/auth/register", json=payload)
        data = response.get_json()
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["status"], "error")
        self.assertIn("already taken", data["message"])

    def test_login_success(self):
        """Tests successful login with correct credentials."""
        # Register user
        user = User(username="tester")
        user.set_password("mypassword")
        db.session.add(user)
        db.session.commit()
        
        # Authenticate
        payload = {
            "username": "tester",
            "password": "mypassword"
        }
        response = self.client.post("/api/auth/login", json=payload)
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "success")
        
        # Verify session state via /api/auth/me
        me_response = self.client.get("/api/auth/me")
        me_data = me_response.get_json()
        self.assertEqual(me_response.status_code, 200)
        self.assertEqual(me_data["status"], "authenticated")

    def test_login_invalid_credentials(self):
        """Tests that invalid logins are rejected with a 401 error."""
        # Test non-existent user
        response = self.client.post("/api/auth/login", json={"username": "fake", "password": "fake"})
        self.assertEqual(response.status_code, 401)
        
        # Test wrong password
        user = User(username="tester")
        user.set_password("correctpass")
        db.session.add(user)
        db.session.commit()
        
        response = self.client.post("/api/auth/login", json={"username": "tester", "password": "wrongpassword"})
        self.assertEqual(response.status_code, 401)

    def test_logout(self):
        """Tests that logging out clears session flags."""
        # Register and Login
        user = User(username="tester")
        user.set_password("mypassword")
        db.session.add(user)
        db.session.commit()
        
        self.client.post("/api/auth/login", json={"username": "tester", "password": "mypassword"})
        
        # Logout (returns 302 redirect)
        logout_response = self.client.post("/api/auth/logout")
        self.assertEqual(logout_response.status_code, 302)
        
        # Verify state is unauthenticated
        me_response = self.client.get("/api/auth/me")
        self.assertEqual(me_response.status_code, 401)

if __name__ == "__main__":
    unittest.main()
