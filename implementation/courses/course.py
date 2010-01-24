'''
course.py file for page related operations.

Contains operations for Courses

@author: Matthew Tytel

'''
from courses.models import *
from include.inject import inject, injectstatic

@injectstatic(Course)
def CreateCourse(name, user, slug=None):
	''' Creates a new course

		 Takes in the name of the course and a user object, and an optional
		 slug string. Creates a new course, enrolls the user in the course and 
		 assigns all permissions to them.  Returns the course after saving it
		 it.  Have to save it so that enrollment gets an id to link to

		 TODO: Also needs to create a "default" landing page
	'''
	# check for empty string (or default value)
	if not slug:
		slug = slugify(name)

	newcourse = Course(name=name, slug=slug)
	newcourse.save()

	newcourse.addUser(user, True, True, True)

	return newcourse

@inject(Course)
def addPage(self, newPage, parentPage = None, order = None):
	'''
	Adds a page to this course

	If no parent is provided, insert under the "course" page as the last page.

	If no order is provided, insert it as the last page under the parent

	This operation saves the page to the database, and then returns the new
	page.
	'''
	pass
		
@inject(Course)
def addUser(self, user, edit=False, stats=False, manage=False):
	''' Adds a User to a course 
	
	    Takes in a user, and optional boolean values for edit, stats, and
	    manage permission, in that order. Creates a new enrollment for that
	    user and permission level and adds it to the Course.  Returns the 
	    enrollment after saving it to the database
	'''
  	enrollment = Enrollment.CreateEnrollment(user, self, \
                                            edit, stats, manage)
	enrollment.save()
	return enrollment

@inject(Course)
def remove(self):
	'''
		Removes this course and all of its pages, statistics, and enrollments
		from the database (TODO: or doesn't remove them from the database?)
	'''
	pass

@inject(Course)
def removePage(self, page, updateLinks = True):
	'''
	Removes the specified page from the specified course

	To remove a page, the specified page is loaded, its next and prev pages
	are linked and the page is dropped from the database (or not....)

	this operation returns ???
	'''
	pass


@inject(Course)
def setPrivate(self):
	self.private = True
	self.save()


# Everything below here is probably supposed to be in views.py -mgius


def removeCourse(request):
	'''
	Removes a specified course from existence

	This operation returns an http response for viewing the deletion of the course
	'''
	pass


def setPrivate(request):
	'''
	Set's the class to public/private depending on what is specified

	This operation returns an http response for viewing the privacy change
	'''
	pass

def search(request):
	'''
	Searches a specified class for a page

	This operation returns an http response for viewing the search results
	'''
	pass

def importCourse(request):
	'''
	Imports specified information into a Course

	This operation returns an http response for viewing the import
	'''
	pass

def exportCourse(request):
	'''
	Exports the specified Course

	This operation returns an http response with the export data
	'''
	pass


