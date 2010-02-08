"""
This file contains tests for the courses package. 
All the tests get run by the django test runner.

@author Jon Inloes
@author Mark Gius
@author James Pearson
"""

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from courses.models import Course
from courses.models import Enrollment

class CourseTests(TestCase):
	''' 
		Unit Tests on backend Course functions
		@author Mark Gius
	'''
	def setUp(self):
		'''
			Sets up environment for CourseTests
		'''
		pass

	def test_CreateCourse(self):
		'''
			Tests CreateCourse function.

			Verifies that course is created, and the specified user is
			enrolled in the course
		'''
		pass
	
	def test_addPage(self):
		'''
			Tests addPage function

			Verifies that the page is successfully added to the course
		'''
		pass

	def test_addUser(self):
		''' Tests for addUser function

			 Tests adding a user of various levels of permission levels
		'''
		pass
	
	def test_removeUser(self):
		''' 
			Tests ability to remove users from a course
		'''
		pass
	
	def test_remove(self):
		'''
			Tests function to remove a course and it's associated pages,
			enrollments, and stats from the database
		'''
		pass

class CourseViewTests(TestCase):
	''' 
		Unit Tests on Course Views.  Tests use an emulated Web Client
		to simulate a user making requests via the web interface

		Test fixtures include two courses, one private and one public, and
		a set of users.  One user who is enrolled in the private course,
		one user who is enrolled in the public course, and one user who
		is enrolled in neither.

		@author Jon Inloes
		@author Mark Gius
	'''

	fixtures = ['CourseViewTests']

	def setUp(self):
		'''
		Sets up the tests
		'''
		self.client = Client()
		self.slug = 'gene-fishers-cpe102-fall-08'
	
	def testCourse(self):
		statusCode = self.client.get('/%s/' % self.slug).status_code
		self.failUnlessEqual(statusCode, 200, "Oopsie!  We got a status code of %s. :/" % statusCode)
		
		statusCode = self.client.get('/not-a-class/').status_code
		self.failUnlessEqual(statusCode, 200, "Oh my!  Our status code was %s." % statusCode)

	def testRoster(self):
		'''
		Tests that redirection to the roster page works

		Case no.        Inputs                                       Expected Output    	Remark
		1               url = /gene-fishers-cpe102-fall-08/roster/   302                	302 is a found code
		2               url = /badclass/roster/	                   500            		500 is an internal server error
		'''

		slug = '/gene-fishers-cpe102-fall-08/'
		
		response = self.client.get(slug + 'roster/')
		self.failUnlessEqual(response.status_code, 302)

		#slug = '/badclass/'
		#response = self.client.get(slug + 'roster/')
		#self.failUnlessEqual(response.status_code, 500)


	def testEnrollUser(self):
		'''
		Tests enrolling a user in a course through the view

		Case no.        Inputs                                     Expected Output    Remark
		1               url=/gene-fishers-cpe102-fall-08/roster/
		                username = jinloes                         true               true as in the user 
		                                                                              exists in enrollment list
		'''
		username = 'jinloes'

		self.client.post('/' + self.slug + '/roster/adduser/', {'username': username, 'command': 'add'})
		enrollment = Enrollment.objects.get(user__username__exact=username, course__slug__exact=self.slug)
		self.assertEquals(enrollment.user.username, username)

	def testUpdateRoster(self):
		'''
		Tests the updating the roster
		Case no.        Inputs                  Expected Output              Remark
		1.              edit = {jinloes}        enrollment.edit = True
		                manage = {jinloes}      enrollment.manage = True
		                stats = {}              enrollment.stats = False
		2.              edit = {}               enrollment.edit = False
		                manage = {}             enrollment.manage = False
		                stats = {}              enrollment.stats = False
		'''
		pass

	def testPrivacy(self):
		'''
		Tests that a user who is enrolled can access a private course, and a 
		student who is not enrolled cannot access a private course
		'''
		pass
	
# I don't know why, but for some reason join_course_request is returning a 
# 302.  Why?
#	def testPrivateEnrollment(self):
#		'''
#		Tests that a user who is not enrolled can request access to a 
#		private course
#
#		After the user has enrolled in the course, verify that they cannot view
#		the course.  
#
#		After verifying that they cannot view the course, grant them view 
#		permission and verify that they can view the course
#		'''
#		user = User.objects.get(username='PageViewsEnrollmentUser')
#		privateCourse = Course.objects.get(slug='PageViewsPrivateCourse')
#
#      # attempt to enroll in the course
#		response = self.client.post('/submit_join_course_request', \
#				                      {'courseid':privateCourse.id})
#
#      # check for 200 OK and text pending
#		self.assertContains(response, "pending")
#
#      # verify that the enrollmment exists and that the user has no view 
#      # permission
#		enrollment = Enrollment.objects.get(user=user, course=privateCourse)
#
#		assertEquals(enrollment.view, False)
