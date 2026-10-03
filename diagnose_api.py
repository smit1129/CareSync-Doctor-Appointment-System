import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))
from backend.app.main import app

def test_api_login():
    client = TestClient(app)
    
    accounts = [
        ("admin@demo.caresync.local", "Admin@12345"),
        ("aarav.mehta@demo.caresync.local", "Doctor@12345"),
        ("smit.gamit@demo.caresync.local", "Patient@12345")
    ]
    
    print("\n=== API LOGIN DIAGNOSTICS ===")
    for email, password in accounts:
        response = client.post(
            "/api/auth/login",
            json={"email": email, "password": password}
        )
        print(f"Login {email}: Status {response.status_code}")
        if response.status_code != 200:
            print(f"  Error: {response.text}")
        else:
            print(f"  Success: Token received")

if __name__ == "__main__":
    test_api_login()
