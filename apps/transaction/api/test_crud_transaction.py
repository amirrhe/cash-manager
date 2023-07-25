from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import CustomUser
from apps.transaction.models import Transaction


class TransactionCreateViewTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword')
        self.login_url = reverse('login')
        self.transaction_create_url = reverse('create_transaction')
        self.valid_data = {
            'amount': 100,
            'transaction_type': 'income',
            'category': 'Salary',
        }
        self.invalid_data = {
            'amount': 100,
            'transaction_type': 'expense',
            'category': 'Groceries',
        }

    def get_access_token(self):
        response = self.client.post(
            self.login_url,
            data={
                'username': 'testuser',
                'password': 'testpassword'},
            format='json')
        return response.data['access']

    def test_create_transaction_with_invalid_data(self):
        access_token = self.get_access_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = self.client.post(self.transaction_create_url, data=self.invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Transaction.objects.count(), 0)

        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, 0)

    def test_create_transaction_with_negative_balance(self):
        access_token = self.get_access_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

        self.user.balance = 1
        self.user.save()

        self.valid_data['transaction_type'] = 'expense'
        self.valid_data['amount'] = 100

        response = self.client.post(self.transaction_create_url, data=self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data[0]), 'Insufficient balance.')

        self.assertEqual(Transaction.objects.count(), 0)
        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, 1)

    def test_create_transaction_without_authentication(self):
        response = self.client.post(self.transaction_create_url, data=self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Transaction.objects.count(), 0)


class TransactionListViewTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword')
        self.login_url = reverse('login')
        self.transaction_list_url = reverse('transaction_list')

    def get_access_token(self):
        response = self.client.post(
            self.login_url,
            data={
                'username': 'testuser',
                'password': 'testpassword'},
            format='json')
        return response.data['access']

    def test_list_transactions_with_authentication(self):
        access_token = self.get_access_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

        Transaction.objects.create(user=self.user, amount=100, transaction_type='income', category='Salary')
        Transaction.objects.create(user=self.user, amount=50, transaction_type='expense', category='Groceries')

        response = self.client.get(self.transaction_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        for transaction in response.data:
            self.assertEqual(transaction['user'], self.user.id)

    def test_list_transactions_without_authentication(self):
        response = self.client.get(self.transaction_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")
        self.assertEqual(len(response.data), 1)

    def test_list_transactions_for_another_user(self):
        another_user = CustomUser.objects.create_user(username='anotheruser', password='anotherpassword')

        Transaction.objects.create(user=self.user, amount=100, transaction_type='income', category='Salary')
        Transaction.objects.create(user=another_user, amount=50, transaction_type='expense', category='Groceries')

        access_token = self.get_access_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

        response = self.client.get(self.transaction_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user'], self.user.id)

    def test_list_transactions_with_filter(self):
        Transaction.objects.create(user=self.user, amount=100, transaction_type='income', category='Salary')
        Transaction.objects.create(user=self.user, amount=50, transaction_type='expense', category='Groceries')
        Transaction.objects.create(user=self.user, amount=200, transaction_type='income', category='Bonus')

        access_token = self.get_access_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

        response = self.client.get(self.transaction_list_url, {'transaction_type': 'income'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        for transaction in response.data:
            self.assertEqual(transaction['transaction_type'], 'income')

        response = self.client.get(self.transaction_list_url, {'category': 'Salary'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['category'], 'Salary')


class TransactionRetrieveViewTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword')
        self.transaction = Transaction.objects.create(
            user=self.user,
            amount=100,
            transaction_type='income',
            category='Salary'
        )
        self.login_url = reverse('login')
        self.transaction_create_url = reverse('create_transaction')
        self.transaction_retrieve_url = reverse('transaction_retrive', kwargs={'pk': self.transaction.id})

    def get_access_token(self):
        response = self.client.post(
            self.login_url,
            data={'username': 'testuser', 'password': 'testpassword'},
            format='json'
        )
        return response.data['access']

    def test_retrieve_transaction_with_authentication(self):
        access_token = self.get_access_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

        response = self.client.get(self.transaction_retrieve_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.transaction.id)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['amount'], self.transaction.amount)
        self.assertEqual(response.data['transaction_type'], self.transaction.transaction_type)
        self.assertEqual(response.data['category'], self.transaction.category)

    def test_retrieve_transaction_without_authentication(self):
        response = self.client.get(self.transaction_retrieve_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_nonexistent_transaction(self):
        access_token = self.get_access_token()
        url = reverse('transaction_retrive', kwargs={'pk': 9999})

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_transaction_of_other_user(self):
        other_user = CustomUser.objects.create_user(username='otheruser', password='testpassword')
        transaction_obj = Transaction.objects.create(
            user=other_user,
            amount=200,
            transaction_type='expense',
            category='Groceries'
        )

        access_token = self.get_access_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        url = reverse('transaction_retrive', kwargs={'pk': transaction_obj.id})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TransactionUpdateViewTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword')
        self.transaction = Transaction.objects.create(
            user=self.user,
            amount=100,
            transaction_type='income',
            category='Salary'
        )
        self.login_url = reverse('login')
        self.transaction_update_url = reverse('transaction_update', kwargs={'pk': self.transaction.id})

    def get_access_token(self):
        response = self.client.post(
            self.login_url,
            data={'username': 'testuser', 'password': 'testpassword'},
            format='json'
        )
        return response.data['access']

    def test_update_transaction_with_authentication(self):
        access_token = self.get_access_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

        updated_data = {
            'amount': 150,
            'category': 'Updated Category'
        }

        response = self.client.patch(self.transaction_update_url, data=updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.amount, updated_data['amount'])
        self.assertEqual(self.transaction.category, updated_data['category'])

    def test_update_transaction_without_authentication(self):
        updated_data = {
            'amount': 150,
            'category': 'Updated Category'
        }

        response = self.client.patch(self.transaction_update_url, data=updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.transaction.refresh_from_db()
        self.assertNotEqual(self.transaction.amount, updated_data['amount'])
        self.assertNotEqual(self.transaction.category, updated_data['category'])

    def test_update_transaction_of_other_user(self):
        other_user = CustomUser.objects.create_user(username='otheruser', password='testpassword')
        transaction_obj = Transaction.objects.create(
            user=other_user,
            amount=200,
            transaction_type='expense',
            category='Groceries'
        )

        access_token = self.get_access_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        url = reverse('transaction_update', kwargs={'pk': transaction_obj.id})

        updated_data = {
            'amount': 300,
            'category': 'Updated Category'
        }

        response = self.client.patch(url, data=updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        transaction_obj.refresh_from_db()
        self.assertNotEqual(transaction_obj.amount, updated_data['amount'])
        self.assertNotEqual(transaction_obj.category, updated_data['category'])

    def test_update_transaction_with_balance_change(self):
        access_token = self.get_access_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

        updated_data = {
            'amount': 150,
            'transaction_type': 'income',
            'category': 'Updated Category'
        }

        initial_balance = self.user.balance
        response = self.client.patch(self.transaction_update_url, data=updated_data, format='json')
        updated_transaction = Transaction.objects.get(id=self.transaction.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_transaction.amount, updated_data['amount'])
        self.assertEqual(updated_transaction.transaction_type, updated_data['transaction_type'])
        self.assertEqual(updated_transaction.category, updated_data['category'])
        self.assertEqual(updated_transaction.user.balance, initial_balance +
                         (updated_data['amount'] - self.transaction.amount))

    def test_update_transaction_with_invalid_data(self):
        access_token = self.get_access_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

        invalid_data = {
            'amount': -50,
            'transaction_type': 'invalid_type',
        }

        response = self.client.patch(self.transaction_update_url, data=invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('transaction_type', response.data)
        self.assertEqual(
            response.data['transaction_type'][0],
            '"invalid_type" is not a valid choice.')

    def test_update_nonexistent_transaction(self):
        access_token = self.get_access_token()

        url = reverse('transaction_update', kwargs={'pk': 9999})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

        updated_data = {
            'amount': 150,
            'category': 'Updated Category'
        }

        response = self.client.patch(url, data=updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TransactionDeleteViewTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword')
        self.transaction = Transaction.objects.create(
            user=self.user,
            amount=100,
            transaction_type='income',
            category='Salary'
        )
        self.user.balance += 100
        self.user.save()
        self.login_url = reverse('login')
        self.transaction_delete_url = reverse('transaction_delete', kwargs={'pk': self.transaction.id})

    def get_access_token(self):
        response = self.client.post(
            self.login_url,
            data={'username': 'testuser', 'password': 'testpassword'},
            format='json'
        )
        return response.data['access']

    def test_delete_transaction_with_authentication(self):
        access_token = self.get_access_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

        response = self.client.delete(self.transaction_delete_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Transaction.objects.filter(id=self.transaction.id).exists())

    def test_delete_transaction_without_authentication(self):
        response = self.client.delete(self.transaction_delete_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Transaction.objects.filter(id=self.transaction.id).exists())

    def test_delete_transaction_of_other_user(self):
        other_user = CustomUser.objects.create_user(username='otheruser', password='testpassword')
        transaction_obj = Transaction.objects.create(
            user=other_user,
            amount=200,
            transaction_type='expense',
            category='Groceries'
        )

        access_token = self.get_access_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        url = reverse('transaction_delete', kwargs={'pk': transaction_obj.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Transaction.objects.filter(id=transaction_obj.id).exists())

    def test_delete_nonexistent_transaction(self):
        access_token = self.get_access_token()
        url = reverse('transaction_delete', kwargs={'pk': 9999})

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_transaction_and_adjust_balance(self):
        access_token = self.get_access_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

        initial_balance = self.user.balance
        response = self.client.delete(self.transaction_delete_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Transaction.objects.filter(id=self.transaction.id).exists())

        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, initial_balance - self.transaction.amount)

    def test_delete_transaction_without_authentication_adjust_balance(self):
        initial_balance = self.user.balance
        response = self.client.delete(self.transaction_delete_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Transaction.objects.filter(id=self.transaction.id).exists())

        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, initial_balance)

    def test_delete_transaction_of_other_user_adjust_balance(self):
        other_user = CustomUser.objects.create_user(username='otheruser', password='testpassword')
        transaction_obj = Transaction.objects.create(
            user=other_user,
            amount=200,
            transaction_type='expense',
            category='Groceries'
        )

        access_token = self.get_access_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        url = reverse('transaction_delete', kwargs={'pk': transaction_obj.id})

        initial_balance = self.user.balance
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Transaction.objects.filter(id=transaction_obj.id).exists())

        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, initial_balance)
