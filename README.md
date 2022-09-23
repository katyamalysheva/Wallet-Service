# Wallet-Service
Pet app. Provides the ability to create new wallets and proceed transactions between them. Transactions are available only for wallets with the same currnecy.

API endpoints:

<ul>POST /register - creates a new user. Needs username, email, password and password2  </ul>

<ul>GET /wallets - shows all user wallets.</ul>
<ul>POST /wallets - creates a new wallet. Needs type (Visa, Mastercard) and currency (USD, EUR, RUB).</ul>
<ul>GET /wallets/str:wallet_name - shows the details if wallet with name=wallet_name.</ul>
<ul>DELETE /wallets/str:wallet_name - allows to delete a wallet with name=walley_name.</ul>

<ul>GET /transactions - shows all the transactions for current user.</ul>
<ul>POST /transactions - creates a new transaction. Needs name of receiver wallet, sender wallet and transfer amount.</ul>
<ul>GET /transactions/int:transaction_id - shows the details of a transaction with id=transaction_id.</ul>
<ul>GET /transactions/str:wallet_name - shows all transactions connected with a current user</ul>


Stack: Python, Django, DRF, Django ORM, PostgreSQL

Usefull resourses:
<br>https://django.fun/tutorials/autentifikaciya-polzovatelya-s-pomoshyu-django-rest-framework-i-veb-tokenov-json/
