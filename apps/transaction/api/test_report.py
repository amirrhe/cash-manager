# tests.py
from datetime import date
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken
from apps.users.models import CustomUser
from apps.transaction.models import Transaction


class CategoryExpenseReportViewTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword')
        self.login_url = reverse('login')
        self.report_url = reverse('category_wise_expense_report')

    def get_access_token(self):
        response = self.client.post(
            self.login_url,
            data={'username': 'testuser', 'password': 'testpassword'},
            format='json'
        )
        access_token = response.data['access']
        return AccessToken(token=access_token)

    def create_transaction(self, amount, category, year, month):
        transaction = Transaction.objects.create(
            user=self.user,
            amount=amount,
            transaction_type='expense',
            category=category,
            created=date(year, month, 1)
        )
        return transaction

    def test_category_expense_report(self):
        access_token = self.get_access_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(access_token))

        self.create_transaction(50, 'Food', year=2023, month=7)
        self.create_transaction(100, 'Rent', year=2023, month=7)
        self.create_transaction(30, 'Food', year=2023, month=8)
        self.create_transaction(70, 'Utilities', year=2023, month=8)
        self.create_transaction(40, 'Food', year=2023, month=9)

        report_data = {
            'month': 7,
            'year': 2023,
        }
        response = self.client.post(self.report_url, data=report_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['month'], 7)
        self.assertEqual(response.data['year'], 2023)
        self.assertEqual(response.data['category_expenses']['Food'], 120)
        self.assertEqual(response.data['category_expenses']['Rent'], 100)

    def test_category_expense_report_with_invalid_month(self):
        access_token = self.get_access_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(access_token))

        report_data = {
            'month': 13,
            'year': 2023,
        }
        response = self.client.post(self.report_url, data=report_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('month', response.data)
        self.assertEqual(response.data['month'][0].code, 'max_value')

    def test_category_expense_report_with_invalid_year(self):
        access_token = self.get_access_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(access_token))

        report_data = {
            'month': 7,
            'year': -100,
        }
        response = self.client.post(self.report_url, data=report_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('year', response.data)
        self.assertEqual(response.data['year'][0].code, 'min_value')


class MonthlySummaryReportViewTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword')
        self.login_url = reverse('login')
        self.report_url = reverse('monthly_summary_report')

    def get_access_token(self):
        response = self.client.post(
            self.login_url,
            data={'username': 'testuser', 'password': 'testpassword'},
            format='json'
        )
        access_token = response.data['access']
        return AccessToken(token=access_token)

    def create_transaction(self, amount, transaction_type, year, month):
        transaction = Transaction.objects.create(
            user=self.user,
            amount=amount,
            transaction_type=transaction_type,
            created=date(year, month, 1)
        )
        return transaction

    def test_monthly_summary_report(self):
        access_token = self.get_access_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(access_token))

        self.create_transaction(100, 'income', year=2023, month=7)
        self.create_transaction(50, 'income', year=2023, month=7)
        self.create_transaction(30, 'expense', year=2023, month=7)
        self.create_transaction(70, 'expense', year=2023, month=7)
        self.create_transaction(40, 'income', year=2023, month=8)

        report_data = {
            'month': 7,
            'year': 2023,
        }
        response = self.client.post(self.report_url, data=report_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['month'], 7)
        self.assertEqual(response.data['year'], 2023)
        self.assertEqual(response.data['total_income'], 190)
        self.assertEqual(response.data['total_expense'], 100)
        self.assertEqual(response.data['net_cash_flow'], 90)

    def test_monthly_summary_report_with_invalid_month(self):
        access_token = self.get_access_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(access_token))

        report_data = {
            'month': 13,
            'year': 2023,
        }
        response = self.client.post(self.report_url, data=report_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('month', response.data)
        self.assertEqual(response.data['month'][0].code, 'max_value')

    def test_monthly_summary_report_with_invalid_year(self):
        access_token = self.get_access_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(access_token))

        report_data = {
            'month': 7,
            'year': -100,
        }
        response = self.client.post(self.report_url, data=report_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('year', response.data)
        self.assertEqual(response.data['year'][0].code, 'min_value')
