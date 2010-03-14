from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from courses.models import Course, Enrollment
from stats.models import Stat
from courses.course import renameCourse, removeCourse
from pages.lesson.models import Lesson
from home.views import master_rtr, custom_403
from pages.lesson.lesson import *
from pages.page import getNextPage, getPrevPage
from django.contrib.auth.decorators import login_required
import urlparse
import re

'''
@author Matthew Tytel
@author Russell Mezzetta
@author Evan Kleist
@author John Hartquist
'''

@login_required
def create_lesson(request, course_slug, page_slug):
	'''
	@author Matthew Tytel

	Creates a new lesson and shows the user the edit page but
	does not save the lesson to the database
	'''
	#enforcing permissions
	try:
		e = Enrollment.objects.get(course__slug = course_slug, user = request.user)
	except Enrollment.DoesNotExist:
		return custom_403(request, "User cannot create a lesson in the course because the user is not enrolled in this course")
	if not e.edit:
		return custom_403(request, "User cannot create a lesson in the course because the user does not have edit permissions on the course")

	if request.method == "POST" and "Save" in request.POST:
		name = request.POST["lessonname"].strip()
		
		#create a lesson (don't save) this will allow the len < 1 case to
		#save the content that the user entered, and display course name
		lesson = CreateLesson(name)
		lesson.workingCopy = lesson.content = request.POST["content"]
		lesson.course = Course.objects.get(slug=course_slug)
		
		if len(name) < 1:
			return master_rtr(request, 'page/lesson/edit_lesson.html', \
				            {'course_slug':course_slug,
								 'page_slug': page_slug,
								 'course':course_slug,
								 'message':'Lesson names must be non-empty',
								 'lesson':lesson, 'new':True})

		if saveNewLesson(request, course_slug, page_slug) == 0:
			return HttpResponseRedirect(reverse('pages.views.show_page', args=[course_slug, lesson.slug]))
		else:
			return master_rtr(request, 'page/lesson/edit_lesson.html', \
				            {'course_slug':course_slug,
								 'page_slug': page_slug,
								 'course':course_slug,
								 'message':'A lesson with that name already exists',
								 'lesson':lesson, 'new':True})
	
	lesson = CreateLesson('')
	return master_rtr(request, 'page/lesson/edit_lesson.html', \
			{'course_slug':course_slug, \
			 'course':course_slug, \
			 'page_slug':page_slug, \
			 'pid':lesson.name, 'new':True})

def show_lesson(request, course_slug, page_slug, lessonPage, preview=False):
	'''
	@author Russell Mezzetta
	This view displays a lesson to the user
	'''
	# To get lessonConent now, you need to retreieve the page from the database, cast it to a lesson, and get the "text" attribute
	#shouldn't have to try/except because previous calls should guarentee the page exists	
	
	#check request method for prev/next button
	if request.method == "POST":
		if "goToNextPage" in request.POST:
			#redirect to the next page
			nextPage = getNextPage(lessonPage)
			if nextPage != None:
				#args = [course_slug, nextPage.slug]
				return HttpResponseRedirect(reverse('pages.views.show_page', args=[course_slug, nextPage.slug]))
		if "goToPrevPage" in request.POST:
			#redirect to the prev page
			prevPage = getPrevPage(lessonPage)
			if prevPage != None:
				#args = [course_slug, prevPage.slug]
				return HttpResponseRedirect(reverse('pages.views.show_page', args=[course_slug, prevPage.slug]))
		if "quitCourse" in request.POST:
			course = Course.objects.get(slug=course_slug)
			return master_rtr(request, 'courses/remove_course.html', {'course':course})
		if "confirmQuitCourse" in request.POST:
			course = Course.objects.get(slug=course_slug)
			if request.POST['confirmQuitCourse'] == "yes":
				#remove user enrollment for course
				if request.user.is_authenticated():
					e = Enrollment.objects.get(user = request.user, course = course)
					e.delete()
					#remove all stats for user in course
					s = Stat.objects.filter(user = request.user, course = course)
					s.delete()
				else:
					if course in request.session['anonCourses']:
						#this may look like extra work but it is necessary to get the
						#lazy session to actually save the data
						anon = request.session['anonCourses']
						anon.remove(course)
						request.session['anonCourses'] = anon
				return HttpResponseRedirect(reverse('home.views.show_homepage'))

	if preview == False:
		content = lessonPage.content
	else:
		content = lessonPage.workingCopy

	title = lessonPage.name
	
	if request.user.is_authenticated():
		try:
			e = Enrollment.objects.get(course__slug=course_slug, user = request.user)
			if e.edit:
				create_enabled = True
			else:
				create_enabled = False
		except Enrollment.DoesNotExist:
			create_enabled = False
	else:
		create_enabled = False

	return master_rtr(request, 'page/lesson/index.html', \
			{'course_slug':course_slug, 'page_slug':page_slug, 
			 'content':content, 'lesson_title':title, 'create_enabled':create_enabled})

@login_required
def edit_lesson(request, course_slug, page_slug):
	'''
	@author Russell Mezzetta
	@author John Hartquist
	This view displays the lesson editing page
	This view is only accessed through edit_page. Therefore permission have already been checked.
	'''
	
	#common dictionary fields
	data={'course_slug':course_slug, 'page_slug':page_slug}
	lesson = Course.objects.get(slug=course_slug).pages.get(slug=page_slug)
	
	try:
		lesson = lesson.lesson
	except Lesson.DoesNotExist:
		print "OH MY! page is not a lesson???"
	data['lesson'] = lesson	

	if request.method == "POST":
		#Saves the working copy of the lesson
		if "Save" in request.POST:
			#save the content of the lesson
			data['lesson'] = saveLessonWorkingCopy(lesson, request.POST['content'])

			#check if the name changed
			if lesson.name != request.POST['lessonname']:
				ret = {}

				if page_slug == course_slug:
					ret = renameCourse(Course.objects.get(slug=course_slug), request.POST['lessonname'])
					if 'course' in ret:
						course_slug = ret['course'].slug
						saveLessonName(lesson, request.POST['lessonname'])
				else:
					ret = saveLessonName(lesson, request.POST['lessonname'])
				#check if saveLessonName returned error message
				if 'message' in ret:
					data['message'] = ret['message']
				#else:
				#	return HttpResponseRedirect(reverse('pages.views.edit_page', args=[course_slug, lesson.slug]))
			
			if request.POST['Save'] == "Save":
				#redirect to this page(redirect b/c name may have changed)
				return HttpResponseRedirect(reverse('pages.views.edit_page', args=[course_slug, lesson.slug]))
			elif request.POST['Save'] == "Save/Preview":
				#redirect to the '/preview' view of this page 
				#(note lesson slug may have changed)
				return HttpResponseRedirect(reverse('pages.views.show_page_preview', args=[course_slug, lesson.slug]))
			else: #request.POST['Save'] == "Save/Publish":
				#data['lesson'] = 
				publishLessonChanges(lesson)
				return HttpResponseRedirect(reverse('pages.views.show_page', args=[course_slug, lesson.slug]))
			#return master_rtr(request, 'page/lesson/edit_lesson.html', data)

		#display confirmation to remove the lesson from the course
		elif "Remove" in request.POST:
			return master_rtr(request, 'page/lesson/remove_lesson.html', data)

		#this gets called after the above "remove" button is clicked and the user
		#is asked to confirm
		elif "confirmRemove" in request.POST:
			if request.POST['confirmRemove'] == 'yes':
				if course_slug == page_slug:#remove the course
					removeCourse(course_slug)
				else:
					removeLesson(request, course_slug, page_slug)
				return HttpResponseRedirect(reverse('home.views.show_homepage'))
			else:
				return master_rtr(request, 'page/lesson/edit_lesson.html', data)
		
		#redirects to the move_page view
		elif "Move" in request.POST:
			return HttpResponseRedirect(reverse('pages.views.move_page', args=[course_slug, page_slug]))
		
		#Publishes the workingCopy
		elif "Publish" in request.POST:
			#save any changes made to working copy before saving the same changes 
			#to the published copy.
			lesson.workingCopy = request.POST['content']
			data['lesson'] = publishLessonChanges(lesson)
			return master_rtr(request, 'page/lesson/edit_lesson.html', data)

		#Revert the workingCopy to the published copy
		elif "Revert" in request.POST:
			data['lesson'] = revertLessonChanges(lesson)
			return master_rtr(request, 'page/lesson/edit_lesson.html', data)

	return master_rtr(request, 'page/lesson/edit_lesson.html', data)
