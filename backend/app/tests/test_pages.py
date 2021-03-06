from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from rest_framework import status

from app.services import index_page_service
from app.tests import create_config, create_temp_data, create_admin

HOST = 'http://localhost:8080'

INDEX_URL = reverse('index')


class PublicTests(TestCase):
    def setUp(self):
        self.client = Client()
        create_temp_data()
        create_config()

    @override_settings(DEBUG=True)
    def test_index_page(self):
        res = self.client.get(INDEX_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertContains(res, HOST)
        self.assertNotContains(res, 'username')
        self.assertNotContains(res, 'isStaff')

    def test_index_page_prod(self):
        """Test that prod index page not contains develop urls"""
        index_page_service.get_data(AnonymousUser())
        res = self.client.get(INDEX_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotContains(res, HOST)
        self.assertNotContains(res, 'username')
        self.assertNotContains(res, 'isStaff')


class PrivateTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = create_admin()
        self.client.force_login(self.user)
        create_temp_data()
        create_config()

    def test_index_page(self):
        res = self.client.get(INDEX_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertContains(res, 'username')
        self.assertContains(res, 'isStaff')
