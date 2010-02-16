
from django.shortcuts import render_to_response
from courses.models import Course
from pages.lesson.models import Lesson
from home.views import master_rtr
from pages.lesson.lesson import *
import urlparse
import re

'''
@author Matthew Tytel
@author Russell Mezzetta
@author Evan Kleist
@author John Hartquist
'''

def create_lesson(request, course_slug, pid = ""):
	'''
	@author Matthew Tytel

	Creates a new lesson and shows the user the edit page but
	does not save the lesson to the database
	'''
	if request.method == "POST" and "Save" in request.POST:
		saveNewLesson(request, course_slug, pid)
		return master_rtr(request, 'page/lesson/save_lesson.html', \
				            {'course_slug':course_slug, 
								 'page_slug': pid, 
								 'course':course_slug, 'pid':pid})
	
	lesson = CreateLesson('')
	return master_rtr(request, 'page/lesson/edit_lesson.html', \
			{'course_slug':course_slug,
			 'pid':lesson.name, 'content':lesson.content, 'new':True})

def show_lesson(request, course, page_slug):
  # To get lessonConent now, you need to retreieve the page from the database, cast it to a lesson, and get the "text" attribute
	#shouldn't have to try/except because previous calls should guarentee the page exists	
	content = Lesson.objects.get(slug=page_slug).content
	return master_rtr(request, 'page/lesson/index.html', \
			{'course':course, 'course_slug':course, \
			 'page_slug':page_slug, 'pid':page_slug, 'content':content})

def edit_lesson(request, course, page_slug):
	print "EDIT"
	if request.method == "POST":
		if "Save" in request.POST:
			saveLesson(request, course, page_slug)
			return master_rtr(request, 'page/lesson/save_lesson.html', \
					{'course':course, 'course_slug':course, \
					 'page_slug':page_slug, 'pid':page_slug})
		elif "Remove" in request.POST:
			removeLesson(request, course, page_slug)
			return master_rtr(request, 'page/lesson/remove_lesson.html', \
					{'course': course, 'course_slug':course, \
					 'page_slug':page_slug, 'pid':page_slug})
	
	content = Lesson.objects.get(slug=page_slug).content
	return master_rtr(request, 'page/lesson/edit_lesson.html', \
			{'course':course, 'course_slug':course, \
			 'page_slug':page_slug, 'pid':page_slug, 'content':content})
