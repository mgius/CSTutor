'''
Models file for course related classes

Contains the Overall "Course" class, plus the Classes that are primarily
contained within a Course, such as Page, Quiz, Lesson, and Roster.

SVN Commit Info:
$Id$
'''
from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

# Create your models here.

class Course(models.Model):
	''' 
	Top level model for sets of lessons

	A course is a set of zero or more pages.  A course is either public or
	private, and contains a roster of authorized users.  Every course has a
	landing page. 
	'''
	slug = models.SlugField(unique = True)
	name = models.CharField(max_length = 255)
	
	def __unicode__(self):
		''' Returns the Course's name.'''
		return self.name
from courses.course import *

class Enrollment(models.Model):
	''' Model for an Enrollment in a Course

		 An enrollment ties a User to a Course and manages their permissions
		 on that course.

		 In the case of a Public Course, enrollments should only be made when
		 a user needs permission beyond view.  

		 In the case of a Private course, an enrollment relationship is necessary
		 to allow the user to view the course.
	'''
	user = models.ForeignKey(User)
	course = models.ForeignKey(Course, related_name='roster')
   # removed by mgius.  I believe we were going for implied view?
   #view = models.BooleanField
	edit = models.BooleanField(default = False)
	stats = models.BooleanField(default = False)
	manage = models.BooleanField(default = False)

	@staticmethod
	def CreateEnrollment(user, course, \
	                     edit=False, stats=False, manage=False):
		''' Creates a new Enrollment in a course

			 Takes in a user, course, and the three permission bits and
			 sets returns an unsaved enrollment object.
		'''
		return Enrollment(user=user, course=course, \
		                  edit=edit, stats=stats, manage=manage)
