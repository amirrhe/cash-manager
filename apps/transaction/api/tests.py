# tests.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.transaction.models import Transaction
from apps.users.models import CustomUser


class TransactionIntegrationTestCase(APITestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.register_url = reverse('register')
        self.transaction_create_url = reverse('create_transaction')
        self.transaction_list_url = reverse('transaction_list')
        self.transaction_retrieve_url = reverse('transaction_retrive', kwargs={'pk': 1})

    def register_user(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword',
            'confirm_password': 'testpassword'
        }
        response = self.client.post(self.register_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def login_user(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.post(self.login_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data['access']

    def create_transaction(self, access_token):
        data = {
            'amount': 100,
            'transaction_type': 'income',
            'category': 'Salary',
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = self.client.post(self.transaction_create_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_login_and_create_transaction(self):
        self.register_user()
        access_token = self.login_user()
        self.create_transaction(access_token)

        user = CustomUser.objects.get(username='testuser')
        self.assertEqual(user.balance, 100)

    def test_update_transaction_with_balance_change(self):
        self.register_user()
        access_token = self.login_user()
        self.create_transaction(access_token)

        transaction = Transaction.objects.first()
        transaction_update_url = reverse('transaction_update', kwargs={'pk': transaction.id})

        updated_data = {
            'amount': 150,
            'transaction_type': 'income',
            'category': 'Updated Category'
        }

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = self.client.patch(transaction_update_url, data=updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        transaction.refresh_from_db()
        self.assertEqual(transaction.amount, updated_data['amount'])
        self.assertEqual(transaction.transaction_type, updated_data['transaction_type'])
        self.assertEqual(transaction.category, updated_data['category'])

        user = CustomUser.objects.get(username='testuser')
        self.assertEqual(user.balance, 150)

    def test_list_transactions_with_authentication(self):
        self.register_user()
        access_token = self.login_user()
        self.create_transaction(access_token)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = self.client.get(self.transaction_list_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_transaction_with_authentication(self):
        self.register_user()
        access_token = self.login_user()
        self.create_transaction(access_token)

        transaction = Transaction.objects.first()
        transaction_retrieve_url = reverse('transaction_retrive', kwargs={'pk': transaction.id})

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = self.client.get(transaction_retrieve_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], transaction.id)
        self.assertEqual(response.data['amount'], transaction.amount)
        self.assertEqual(response.data['transaction_type'], transaction.transaction_type)
        self.assertEqual(response.data['category'], transaction.category)
