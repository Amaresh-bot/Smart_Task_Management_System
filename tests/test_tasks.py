import unittest
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.task import Task

class TestTasksModule(unittest.TestCase):
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
        
        # Create a pre-registered test user
        self.user = User(username="tasktester")
        self.user.set_password("securepassword")
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        """
        Executes after every test.
        Cleans up active database sessions and drops tables.
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login_client(self):
        """Helper to authenticate the client for protected task actions."""
        self.client.post("/api/auth/login", json={
            "username": "tasktester",
            "password": "securepassword"
        })

    def test_unauthorized_access_redirect(self):
        """Tests that unlogged clients are blocked from fetching tasks."""
        # Attempt to access protected dashboard view without logging in
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 302)  # Redirects to login view

    def test_task_create_success(self):
        """Tests that an authenticated user can create tasks."""
        self.login_client()
        
        payload = {
            "title": "Complete Internship Project",
            "description": "Build full stack smart task manager with Flask and PostgreSQL",
            "priority": "HIGH",
            "status": "IN_PROGRESS"
        }
        response = self.client.post("/api/tasks", json=payload)
        data = response.get_json()
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["task"]["title"], "Complete Internship Project")
        
        # Verify persistence in SQLite
        task = Task.query.filter_by(title="Complete Internship Project").first()
        self.assertIsNotNone(task)
        self.assertEqual(task.priority, "HIGH")

    def test_task_create_validation_checks(self):
        """Tests validation checks on task creation inputs."""
        self.login_client()
        
        # Empty title input
        response = self.client.post("/api/tasks", json={"title": "", "priority": "LOW"})
        self.assertEqual(response.status_code, 400)
        
        # Invalid priority enum value
        response = self.client.post("/api/tasks", json={"title": "Test Title", "priority": "URGENT"})
        self.assertEqual(response.status_code, 400)

    def test_get_user_tasks(self):
        """Tests retrieving only tasks belonging to the logged-in user."""
        self.login_client()
        
        # Create sample task
        task = Task(
            title="Read Documentation",
            description="Explore Pandas APIs",
            priority="LOW",
            status="PENDING",
            user_id=self.user.id
        )
        db.session.add(task)
        db.session.commit()
        
        response = self.client.get("/api/tasks")
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["tasks"][0]["title"], "Read Documentation")

    def test_task_update_success(self):
        """Tests editing task attributes successfully."""
        self.login_client()
        
        # Create task
        task = Task(
            title="Old Task Title",
            description="Old Description",
            priority="LOW",
            status="PENDING",
            user_id=self.user.id
        )
        db.session.add(task)
        db.session.commit()
        
        payload = {
            "title": "New Task Title",
            "status": "COMPLETED",
            "priority": "HIGH"
        }
        response = self.client.put(f"/api/tasks/{task.id}", json=payload)
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["task"]["title"], "New Task Title")
        self.assertEqual(data["task"]["status"], "COMPLETED")
        self.assertEqual(data["task"]["priority"], "HIGH")

    def test_task_delete_success(self):
        """Tests deleting a task successfully."""
        self.login_client()
        
        # Create task
        task = Task(
            title="Task to Delete",
            priority="LOW",
            status="PENDING",
            user_id=self.user.id
        )
        db.session.add(task)
        db.session.commit()
        
        response = self.client.delete(f"/api/tasks/{task.id}")
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "success")
        
        # Verify deletion in database using Session.get (modern SQLAlchemy 2.0 style)
        deleted_task = db.session.get(Task, task.id)
        self.assertIsNone(deleted_task)

    def test_get_analytics_success(self):
        """Tests the analytics calculation endpoint with sample tasks."""
        self.login_client()
        
        # Add some sample tasks to calculate analytics
        task1 = Task(title="Task 1", priority="HIGH", status="COMPLETED", user_id=self.user.id)
        task2 = Task(title="Task 2", priority="LOW", status="PENDING", user_id=self.user.id)
        db.session.add_all([task1, task2])
        db.session.commit()
        
        response = self.client.get("/api/tasks/analytics")
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "success")
        self.assertIn("analytics", data)
        self.assertEqual(data["analytics"]["total_tasks"], 2)
        self.assertEqual(data["analytics"]["completed_tasks"], 1)
        self.assertEqual(data["analytics"]["pending_tasks"], 1)
        self.assertEqual(data["analytics"]["completion_rate"], 50.0)

if __name__ == "__main__":
    unittest.main()
