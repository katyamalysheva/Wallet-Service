"""Module for testing
    /transactions,
    /transactions/<int:id>,
    /transactions/<str:wallet_name> APIs
"""

import pytest
from django.contrib.auth.models import User
from WalletService.models import Transaction, Wallet
from WalletService.serializers import TransactionSerializer, WalletSerializer


@pytest.fixture()
def user1():
    """User fixture"""

    user, created = User.objects.get_or_create(username="username1")
    if created:
        user.set_password("test_user")
        user.save()
    wallets = [
        {
            "name": "U1RUS1",
            "type": "Visa",
            "balance": 100,
            "currency": "RUS",
        },
        {
            "name": "U1RUS2",
            "type": "Visa",
            "balance": 100,
            "currency": "RUS",
        },
        {
            "name": "U1USD1",
            "type": "Visa",
            "balance": 100,
            "currency": "USD",
        },
        {
            "name": "U1EUR1",
            "type": "Visa",
            "balance": 100,
            "currency": "EUR",
        },
    ]
    for wallet in wallets:
        Wallet.objects.create(**wallet, user=user)

    return user


@pytest.fixture
def user2():
    """Second user fixture"""

    user, created = User.objects.get_or_create(username="username2")
    if created:
        user.set_password("test_user")
        user.save()

    wallets = [
        {
            "name": "U2RUS1",
            "type": "Visa",
            "balance": 100,
            "currency": "RUS",
        },
        {
            "name": "U2USD1",
            "type": "Visa",
            "balance": 100,
            "currency": "USD",
        },
        {
            "name": "U2USD2",
            "type": "Visa",
            "balance": 100,
            "currency": "USD",
        },
        {
            "name": "U2EUR1",
            "type": "Visa",
            "balance": 100,
            "currency": "EUR",
        },
    ]
    for wallet in wallets:
        Wallet.objects.create(**wallet, user=user)

    return user


@pytest.fixture()
def create_transactions(user1, user2):
    """Fixture to create transactions"""
    transactions = [
        {"sender": "U1RUS1", "receiver": "U2RUS1", "transfer_amount": 10},
        {"sender": "U2USD1", "receiver": "U1USD1", "transfer_amount": 10},
        {"sender": "U2EUR1", "receiver": "U1EUR1", "transfer_amount": 10},
        {"sender": "U2USD1", "receiver": "U2USD2", "transfer_amount": 10},
    ]

    for transaction in transactions:
        Transaction.objects.create(
            sender=Wallet.objects.get(name=transaction["sender"]),
            receiver=Wallet.objects.get(name=transaction["receiver"]),
            transfer_amount=transaction["transfer_amount"],
        )


class TestTransactionApi:
    """Class to test /transaction api"""

    @pytest.mark.django_db
    def test_transaction_create_invalid_wallets(self, client, user1):
        """Testing creation of a transaction with invalid wallets"""

        response = client.post("/transactions/")
        assert response.status_code == 403

        client.force_login(user1)
        response = client.post(
            "/transactions/",
            data={"receiver": "NoWallet", "sender": "U1RUS1", "transfer_amount": 10},
        )
        assert response.status_code == 404

        response = client.post(
            "/transactions/",
            data={"receiver": "U2RUS2", "sender": "NoWallet", "transfer_amount": 10},
        )
        assert response.status_code == 404

    @pytest.mark.django_db
    def test_transaction_create_with_not_users_sender_wallet(
        self, client, user1, user2
    ):
        """Testing user permision to create a transaction
        only if sender wallet is a current user wallet"""

        client.force_login(user1)
        response = client.post(
            "/transactions/",
            data={"receiver": "U1RUS1", "sender": "U2RUS1", "transfer_amount": 10},
        )
        assert response.status_code == 403

    @pytest.mark.django_db
    def test_transaction_create_not_eq_currency(self, client, user1):
        """Transaction can be procced only if wallets currencies are equal"""

        client.force_login(user1)
        response = client.post(
            "/transactions/",
            data={"receiver": "U1USD1", "sender": "U1RUS1", "transfer_amount": 10},
        )
        assert response.status_code == 400

        client.force_login(user1)
        response = client.post(
            "/transactions/",
            data={"receiver": "U1RUS2", "sender": "U1RUS1", "transfer_amount": 10},
        )
        assert response.status_code == 201

    @pytest.mark.django_db
    def test_transaction_create_transfer_amount_exceeds_balance(self, client, user1):
        """Test if transaction fails when sender doesn't have enough funds"""

        client.force_login(user1)
        response = client.post(
            "/transactions/",
            data={"receiver": "U1RUS2", "sender": "U1RUS1", "transfer_amount": 1000},
        )
        assert response.status_code == 400

    @pytest.mark.django_db
    def test_transaction_create_fee_check(self, client, user1, user2):
        """Testing balances after transaction and fee calculation"""

        client.force_login(user1)
        response = client.post(
            "/transactions/",
            data={"receiver": "U1RUS2", "sender": "U1RUS1", "transfer_amount": 10},
        )
        assert response.status_code == 201

        sender = Wallet.objects.get(name="U1RUS1")
        serializer = WalletSerializer(sender)
        assert float(serializer.data["balance"]) == 90

        receiver = Wallet.objects.get(name="U1RUS2")
        serializer = WalletSerializer(receiver)
        assert float(serializer.data["balance"]) == 110

        response = client.post(
            "/transactions/",
            data={"receiver": "U2USD1", "sender": "U1USD1", "transfer_amount": 10},
        )
        assert response.status_code == 201

        sender = Wallet.objects.get(name="U1USD1")
        serializer = WalletSerializer(sender)
        assert float(serializer.data["balance"]) == 90 - (Transaction.DEFAULT_FEE * 10)

        receiver = Wallet.objects.get(name="U1RUS2")
        serializer = WalletSerializer(receiver)
        assert float(serializer.data["balance"]) == 110

    @pytest.mark.django_db
    def test_transaction_get(self, client, user1, create_transactions):
        """Testing get request"""

        response = client.get("/transactions/")
        assert response.status_code == 403

        client.force_login(user1)
        response = client.get("/transactions/")
        transactions = response.json()
        assert response.status_code == 200

        user_wallets = user1.wallet_set.all()
        serializer_wallets = WalletSerializer(user_wallets, many=True)
        user_wallets_names = [wallet["name"] for wallet in serializer_wallets.data]
        for transaction in transactions:
            statement = (
                transaction["sender"] in user_wallets_names
                or transaction["receiver"] in user_wallets_names
            )
            assert statement

    @pytest.mark.django_db
    def test_wallet_method_not_allowed(self, client, user1):
        """Testing if PUT, PATCH, DELETE are not allowed"""

        client.force_login(user1)
        response = client.put("/transactions/")
        assert response.status_code == 405

        response = client.patch("/transactions/")
        assert response.status_code == 405

        response = client.delete("/transactions/")
        assert response.status_code == 405


class TestTransactionIdDetailApi:
    """Class to test /transaction/<int:id>"""

    @pytest.mark.django_db
    def test_transaction_id_get(self, client, user1, create_transactions):
        """Testing get request"""

        user1_wallet = Wallet.objects.get(name="U1RUS1")
        serializer_transaction = TransactionSerializer(
            user1_wallet.sender.all().first()
        )
        id = serializer_transaction.data["id"]

        response = client.get(f"/transactions/{id}/")
        assert response.status_code == 403

        client.force_login(user1)
        response = client.get(f"/transactions/{id}/")
        assert response.status_code == 200

        # this user2 wallet doesn't have transactions to user1 wallet
        user2_wallet = Wallet.objects.get(name="U2USD2")
        serializer_transaction = TransactionSerializer(
            user2_wallet.receiver.all().first()
        )
        id = serializer_transaction.data["id"]

        response = client.get(f"/transactions/{id}/")
        assert response.status_code == 404

    @pytest.mark.django_db
    def test_transaction_method_not_allowed(self, client, user1, create_transactions):
        """Testing if DELETE, POST, PUT, PATCH are not allowed"""

        client.force_login(user1)
        response = client.put("/transactions/15/")
        assert response.status_code == 405

        response = client.patch("/transactions/15/")
        assert response.status_code == 405

        response = client.delete("/transactions/15/")
        assert response.status_code == 405

        response = client.post("/transactions/14/", data={"sender": "U1RUS1"})
        assert response.status_code == 405


class TestTransactionOfWalletApi:
    @pytest.mark.django_db
    def test_transaction_wallet_get(self, client, user1, create_transactions):
        """Testing get request"""

        user1_wallet_name = "U1RUS1"
        response = client.get(f"/transactions/{user1_wallet_name}/")
        assert response.status_code == 403

        client.force_login(user1)
        response = client.get(f"/transactions/{user1_wallet_name}/")
        response_transactions = response.json()
        assert response.status_code == 200

        user1_wallet = Wallet.objects.get(name=user1_wallet_name)
        serialized_wallet_sender_transactions = TransactionSerializer(
            user1_wallet.sender.all(), many=True
        )

        serialized_wallet_receive_transactions = TransactionSerializer(
            user1_wallet.receiver.all(), many=True
        )

        for transaction in response_transactions:
            statement = (
                transaction in serialized_wallet_sender_transactions.data
                or transaction in serialized_wallet_receive_transactions
            )
            assert statement

        user2_wallet_name = "U2RUS1"
        response = client.get(f"/transactions/{user2_wallet_name}/")
        assert response.status_code == 404

    @pytest.mark.django_db
    def test_transaction_method_not_allowed(self, client, user1, create_transactions):
        """Testing if DELETE, POST, PUT, PATCH are not allowed"""

        client.force_login(user1)

        wallet = "U1RUS1"
        response = client.put(f"/transactions/{wallet}/")
        assert response.status_code == 405

        response = client.patch(f"/transactions/{wallet}/")
        assert response.status_code == 405

        response = client.delete(f"/transactions/{wallet}/")
        assert response.status_code == 405

        response = client.post(f"/transactions/{wallet}/")
        assert response.status_code == 405
