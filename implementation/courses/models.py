'''
Models file for course related classes

Contains the Overall "Course" class, plus the Classes that are primarily
contained within a Course, such as Page, Quiz, Lesson, and Roster.

SVN Commit Info:
$Id$
'''
from django.db import models
from django.contrib.auth.models import User

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

	@staticmethod
	def CreateCourse(name_, user_, slugstring_=None):
		''' Creates a new course

			 Takes in the name of the course and a user object, and an optional
			 slug string. Creates a new course, enrolls the user in the course and 
			 assigns all permissions to them.  Returns the course after saving it
			 it.  Have to save it so that enrollment gets an id to link to

			 TODO: Slugstring needs to be autogenerated.  Currently isn't
		'''
		if slugstring_ == None:
			slugstring_ = name_

		newcourse = Course(name=name_, slug=slugstring_)
		newcourse.save()

		newcourse.addUser(user_, True, True, True)

		return newcourse
		
	def addUser(self, user_, edit_=False, stats_=False, manage_=False):
		''' Adds a User to a course 
			 
			 Takes in a user, and optional boolean values for edit, stats, and
			 manage permission, in that order. Creates a new enrollment for that
			 user and permission level and adds it to the Course.  Returns the 
			 enrollment after saving it to the database
		'''
		enrollment = Enrollment.CreateEnrollment(user_, self, \
		                                         edit_, stats_, manage_)
		enrollment.save()
		return enrollment

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
	def CreateEnrollment(user_, course_, \
	                     edit_=False, stats_=False, manage_=False):
		''' Creates a new Enrollment in a course

			 Takes in a user, course, and the three permission bits and
			 sets returns an unsaved enrollment object.
		'''
		return Enrollment(user=user_, course=course_, \
		                  edit=edit_, stats=stats_, manage=manage_)
