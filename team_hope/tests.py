import datetime

from django.test import TestCase
from django.urls import reverse



# Initial tests created with GitHub Copilot
class RestaurantRoutesTestCase(TestCase):
    def test_team_hope_page_loads(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
