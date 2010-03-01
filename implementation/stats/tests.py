'''
Unit tests for functions in the Stats module

@author Andrew J. Musselman
'''

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from courses.models import Course
from stats.models import Stat
from pages.models import Page
from stat import *

class StatsTests(TestCase):
	'''
	This class runs test for Stats functions

	'''
	fixtures = ['StatTest']

	def setUp(self):
		'''
		Sets up the envrioment for StatsTests
		'''
		pass

	def test_addStat(self):
		'''
		Tests the add stat function.
		@precondition The user and quiz must exist, 
		and the user must be enrolled in the course that has the quiz
		@precondition.
		@postcondition A new stat is added for the given data
		'''
		user = User.objects.get(username = 'fakeuser')
		quiz = Page.objects.get(pk = '4') #sample quiz 
		course = Course.objects.get(pk = '1')  
		score = 0 #A score of 0 is always safe
		testStat = Stat.CreateStat(course,quiz,user,score)
		#Test to see if the returned stat is correct
		self.assertEquals(testStat.course, course)
		self.assertEquals(testStat.page , quiz)
		self.assertEquals(testStat.user , user)
		self.assertEquals(testStat.score , score)
		self.assertEquals(testStat.maxscore , 3)

		#And test the that it's in the database
		dbTestStat = Stat.objects.get(id=testStat.id)
		self.assertEquals(dbTestStat,testStat)
	
	def test_removeUserStats(self):
		user = User.objects.get(username = 'fakeuser')
		#First we insert it into the database.
		quiz = Page.objects.get(pk = '4') #sample quiz 
		course = Course.objects.get(pk = '1')  
		score = 0 #A score of 0 is always safe
		testStat = Stat.CreateStat(course,quiz,user,score)

		#Make sure it's happned
		dbTestStat = Stat.objects.get(id=testStat.id)
		self.assertEquals(dbTestStat,testStat)

		#Now remove it from the database
		dropAllUserStats(user)
		#self.assertRaises(DoesNotExist,Stat.objects.get(user=user))
		#FIXME

	def test_getBestCourseStats(self):
		'''
		Tests the getBestCourseStats function.
		The fixture should include a course with a pair of users and a pair
		of quizes. Each user has taken the quiz three times, so there should
		be a grand total of 6 stats in the DB (2 users * 3 tries).
		This should get the BEST score, not the latest from each try. So, it
		should return a total of 2 results.
		@precondition The course must exist. There may or may not be any stats
		in it. (I'll test that functionality in another test).
		@postcondition The function returns a list of the best stat each user
		has posted in each quiz.
		'''
		course = Course.objects.get(pk = '4')
		statsList = getBestCourseStats(course)
		#First, the list should give me only two results
		#self.assertEquals(len(statsList),2)
		# THIS TEST IS NOT FINISHED!!! FIXME
		#Test disabled, I may not even need this code. 
	
	def test_NumGetQuizBestAggregates(self):
		'''
		Tesets the getBestQuizBestAggregates. This function is supposed to 
		calculate the aggregates of the best results of each user on each
		quiz. It returns a list of dictionaries, one for each quiz, that 
		describes various aggrigates of the best user scores.
		'''
		course = Course.objects.get(pk = '4')
		aggregatesList = getQuizBestAggregates(course);
		#There there are two quiz in the test database for this course. So,
		# there should only be one element in the list.
		self.assertEquals(len(aggregatesList),2)
		

	def test_avgGetBesqQuizAggregates(self):
		'''
		Tests the getQuizBestAggregates function. This particular
		test checks the value of the returned average for each quiz. 
		'''
		course = Course.objects.get(pk = '4')
		aggregatesList = getQuizBestAggregates(course)

		#Now, we loop though the quizes 
		for aggregates in aggregatesList:
			if(aggregates['page_slug'] == 'test_class_no01_quiz'):
				#Quiz no 1, which should have an average of 10
				#Since each student in the test data has a best result of
				#10
				self.assertEquals(aggregates['result_avg'],10)
			elif(aggregates['page_slug'] == 'test_class_no01_quiz2'):
				#Quiz no 2, which should have an average of 5
				self.assertEquals(aggregates['result_avg'],10)
	

	def test_numGetBestUserAggregates(self):
		'''
		Tests the per-user aggregates function. This particular test
		checks that the proper number of results is returned
		'''
		course = Course.objects.get(pk = '4')
		aggregatesList = getUserBestAggregates(course) 

		#There are two users with stats results in this course.
		self.assertEquals(len(aggregatesList),2)
		
