from fastapi.testclient import TestClient
from main import app 
from database import LocalSession
from models import GlobalBlackList

client = TestClient(app)
access_token = ""

def test_search_user_unauthenticated():
    response = client.post("/search/phone/", json={"phone": "8569321"})
    assert response.status_code == 401
    print("Passed 1/7")

def test_login_user():
    global access_token 
    response = client.post("/login/", json={"phone": "9623457120", "password": "testpassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    access_token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {access_token}"
    print("Passed 2/7")

def test_login_invalid_credentials():
    response = client.post("/login/", json={"phone": "9623457120", "password": "invalidpassword"})
    assert response.status_code == 401
    print("Passed 3/7")

def test_search_user_authenticated():
    response = client.post("/search/phone/", headers={"Authorization": f"Bearer {access_token}"}, json={"phone": "8569321"})
    assert response.status_code == 200
    print("Passed 4/7")


def test_search_user_by_phone():
    global access_token
    with LocalSession() as session:
        test_phone = "1234567891"
        test_entry = GlobalBlackList(phone=test_phone, name="Test User", spam=False, spam_reports=0)
        session.add(test_entry)
        session.commit()

        response = client.post("/search/phone/", headers={"Authorization": f"Bearer {access_token}"}, json={"phone": test_phone})
        assert response.status_code == 200
        assert response.json() == [{"phone": test_phone, "name": "Test User", "spam": False, "spam_reports": 0}]
        print("Passed 5/7")

def test_search_user_by_phone_length():
    response = client.post("/search/phone/", headers={"Authorization": f"Bearer {access_token}"}, json={"phone": "1234"})
    assert response.status_code == 400
    print("Passed 6/7")

def test_search_user_by_phone_not_found():
    response = client.post("/search/phone/", headers={"Authorization": f"Bearer {access_token}"}, json={"phone": "9999999999"})
    assert response.status_code == 404
    print("Passed 7/7")
