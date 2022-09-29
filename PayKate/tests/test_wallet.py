"""Modeule for testing /wallets and /wallets/<str:name> api"""


import pytest
from django.contrib.auth.models import User
from WalletService.models import Wallet


@pytest.fixture
def user():
    """User fixture"""

    user, created = User.objects.get_or_create(username="username")
    if created:
        user.set_password("test_user")
        user.save()
    return user


@pytest.fixture
def user2():
    """Second user fixture"""

    user, created = User.objects.get_or_create(username="username2")
    if created:
        user.set_password("test_user")
        user.save()
    return user


class TestWalletApi:
    """Class for tasting /wallets api"""

    @pytest.mark.django_db
    def test_wallets_get_post(self, user, client):
        """Testing get and post requests"""

        response = client.post("/wallets/")
        assert response.status_code == 403

        client.force_login(user)
        for currency, bonus in Wallet.BONUS.items():
            response = client.post(
                "/wallets/",
                data={
                    "type": "Visa",
                    "currency": currency,
                },
            )
            response_body = response.json()
            assert response.status_code == 201
            assert response_body["type"] == "Visa"
            assert response_body["currency"] == currency
            assert float(response_body["balance"]) == bonus

        response = client.get("/wallets/")
        response_body = response.json()
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_wallets_post_invalid_fields(self, user, client):
        """Testing post response if fields are invalid"""

        client.force_login(user)
        response = client.post(
            "/wallets/",
            data={
                "type": "Abrakadabr",
                "currency": "USD",
            },
        )
        assert response.status_code == 400

        response = client.post(
            "/wallets/",
            data={
                "type": "Mastercard",
                "currency": "Abr",
            },
        )
        assert response.status_code == 400

    @pytest.mark.django_db
    def test_wallets_creation_more_then_allowed(self, user, client):
        """Testing if user is acle to create more wallets then he is allowed to"""
        data = {"type": "Visa", "currency": "USD"}
        client.force_login(user)
        for i in range(Wallet.MAX_USER_WALLETS):
            response = client.post("/wallets/", data=data)

        response = client.post("/wallets/", data=data)
        assert response.status_code == 400

    @pytest.mark.django_db
    def test_wallet_method_not_allowed(self, client, user):
        """Testing if PUT, PATCH are allowed"""

        client.force_login(user)
        response = client.put("/wallets/")
        assert response.status_code == 405

        response = client.patch("/wallets/")
        assert response.status_code == 405


class TestWalletDetailApi:
    """Class to test /wallets/<str:name> api"""

    data = {
        "name": "FBH7ESKD",
        "type": "Visa",
        "currency": "USD",
        "balance": "3.00",
    }

    @pytest.mark.django_db
    def test_wallets_detail_get(self, user, user2, client):
        """Testing permission to view details for wallet with specific name"""

        Wallet.objects.create(**self.data, user=user)
        client.force_login(user2)
        response = client.get("/wallets/FBH7ESKD/")
        assert response.status_code == 404

        client.force_login(user)
        response = client.get("/wallets/FBH7ESKD/")
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_wallets_detail_delete(self, user, user2, client):
        """Testing permission to delete wallet with specific name"""

        Wallet.objects.create(**self.data, user=user)
        client.force_login(user2)
        response = client.delete("/wallets/FBH7ESKD/")
        assert response.status_code == 404

        client.force_login(user)
        response = client.get("/wallets/FBH7ESKD/")
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_wallet_method_not_allowed(self, client, user):
        """Testing if PUT, PATCH are not allowed"""

        Wallet.objects.create(**self.data, user=user)
        client.force_login(user)
        response = client.put("/wallets/FBH7ESKD/")
        assert response.status_code == 405

        response = client.patch("/wallets/FBH7ESKD/")
        assert response.status_code == 405
