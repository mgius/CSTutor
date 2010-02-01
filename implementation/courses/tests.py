"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client

class SimpleTest(TestCase):
	def setUp(self):
		self.client = Client()

	def test_roster(self):
		response = self.client.get('/roster/')
		self.failUnlessEqual(response.status_code, 200)

	def test_add_user(self):
		'''
		Tests adding users to a course.
		'''
		pass
