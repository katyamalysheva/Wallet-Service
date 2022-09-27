"""
This module tests /registration api

# https://djangostars.com/blog/django-pytest-testing/
# https://dev.to/sherlockcodes/pytest-with-django-rest-framework-from-zero-to-hero-8c4

"""


import pytest

test_data = {
    "username": "test_user",
    "email": "test_user@at.com",
    "password": "test_user",
    "password2": "test_user",
}


@pytest.mark.django_db
def test_registration_method_not_allowed(client):
    """Testing if GET, PUT, PATCH, DELETE are allowed"""
    response = client.get("/register/")
    assert response.status_code == 405

    response = client.put("/register/")
    assert response.status_code == 405

    response = client.patch("/register/")
    assert response.status_code == 405

    response = client.delete("/register/")
    assert response.status_code == 405


@pytest.mark.django_db
def test_registration_post(client):
    """Testing post request"""
    response = client.post("/register/", data=test_data)
    response_body = response.json()
    assert response.status_code == 201
    assert response_body["username"] == "test_user"
    assert response_body["password"] != "test_user"


@pytest.mark.django_db
def test_registration_invalid_email(client):
    """Testing empty or invalid email field in post request"""
    data = test_data.copy()
    data.pop("email")
    response = client.post(
        "/register/",
        data=data,
    )
    assert response.status_code == 201
    data["username"] = "username2"
    data["email"] = ""
    response = client.post(
        "/register/",
        data=data,
    )
    assert response.status_code == 201


@pytest.mark.django_db
def test_registration_invalid_required_fields(client):
    """Testing empty or invalid required fields in post request"""
    fields = [*test_data]
    fields.pop(1)
    for field in fields:
        data = test_data.copy()
        data.pop(field)
        response = client.post(
            "/register/",
            data=data,
        )
        assert response.status_code == 400
        data[field] = ""
        response = client.post(
            "/register/",
            data=data,
        )
        assert response.status_code == 400
