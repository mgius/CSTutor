'''
Contains operations for Courses

@author: Matthew Tytel
@author: Mark Gius

'''
from courses.models import *
from courses.enrollment import *
from pages.lesson.models import Lesson
from pages.models import Page

def CreateCourse(name, user, private, slug=None):
	''' Creates a new course

		 Takes in the name of the course and a user object, and an optional
		 slug string. Creates a new course, enrolls the user in the course and 
		 assigns all permissions to them.  Returns the course after saving it
		 it.  Have to save it so that enrollment gets an id to link to
	'''
	# check for empty string (or default value)
	if not slug:
		slug = slugify(name)

	newcourse = Course(name=name, slug=slug, private=private)
	newcourse.save()

	addUser(newcourse, user, True, True, True, True)

	# Create the new landing page

	newpage = Lesson(course=newcourse, slug=slug, name=name, left=1, right=2,\
			           content="Landing page for " + slug +\
						          "<br />Your content here")
	newpage.save()

	return newcourse

def renameCourse(course, newName):
	''' Renames a course
	'''
	if len(newName.strip()) < 1:
		return {'message':"Name change failed: name must be non-empty"}

	#check that the newLessonName doesn't already exist in this course
	newSlug = slugify(newName)

	#search the pages in the course to see if the slug is unique
	courseExists = Course.objects.filter(slug=newSlug).count()
	if courseExists:
		return {'message':"Name change failed. A course with that name already exists"}

	pageExists = Page.objects.filter(course=course).filter(slug=newSlug).count()
	if pageExists:
		return {'message':"Name change failed. A page with that name already exists in this course"}
	
	course.name = newName
	course.slug = newSlug
	course.save()
	return {'course':course}

def addUser(self, user, view = True, edit=False, stats=False, manage=False):
	''' Adds a User to a course 
	
	    Takes in a user, and optional boolean values for edit, stats, and
	    manage permission, in that order. Creates a new enrollment for that
	    user and permission level and adds it to the Course.  

		 Returns the  enrollment after saving it to the database, 
		 or None if the user was already enrolled

		 @author Mark Gius
	'''
   # test for user/course enrollment already
	try:
		Enrollment.objects.get(user=user, course=self)
	except Enrollment.DoesNotExist:
		enrollment = CreateEnrollment(user, self, \
		                              view, edit, stats, manage)
		enrollment.save()
		return enrollment
	# Enrollment already exists
	return None

def removeUser(self, user):
	'''
		Removes the specified user from the course

		@author ?
	'''
	#print 'removing a user'
	try:
		Enrollment.objects.get(user=user, course=self).delete()
	except:
		print 'remove failed'	
	return None

def removeCourse(course_slug):
	'''
	@author Russell Mezzetta
	Removes this course and all of its pages, statistics, and enrollments
	from the database
	@pre course_slug is a string
	@post if course_slug points to a valid course, it will be removed from the database along with all related objects.
	'''
	try:
		c = Course.objects.get(slug=course_slug)
		c.delete()
		return c
	except Course.DoesNotExist:
		return None

def setPrivate(self):
	self.private = True
	self.save()


# Everything below here is probably supposed to be in views.py -mgius
# commented out by mgius on 2/16/10
#def removeCourse(request):
#	'''
#	Removes a specified course from existence
#
#	This operation returns an http response for viewing the deletion of the course
#	'''
#	pass
#
#
#def setPrivate(request):
#	'''
#	Set's the class to public/private depending on what is specified
#
#	This operation returns an http response for viewing the privacy change
#	'''
#	pass
#
#def search(request):
#	'''
#	Searches a specified class for a page
#
#	This operation returns an http response for viewing the search results
#	'''
#	pass
#
#def importCourse(request):
#	'''
#	Imports specified information into a Course
#
#	This operation returns an http response for viewing the import
#	'''
#	pass
#
#def exportCourse(request):
#	'''
#	Exports the specified Course
#
#	This operation returns an http response with the export data
#	'''
#	pass
