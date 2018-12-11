from django.test import TestCase

import json
from django.urls import reverse
from rest_framework.views import status
from rest_framework.test import APITestCase, APIClient
from ..models import User


class TestUsers(APITestCase):

    def setUp(self):
        self.client = APIClient()
