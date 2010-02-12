'''
Views file for quiz related views

This file contains methods for creating a quiz and showing a quiz. More methods will be added to this file in time.

@author Evan Kleist
'''

from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from courses.models import Course
from models import Page
from models import Quiz
from quiz import *
from question.models import MultipleChoiceQuestion
from question.models import CodeQuestion
from home.views import master_rtr

def create_quiz(request, course_slug):
	''' create_Quiz View
		This view will create a quiz and take the user to the quiz editor screen.
	'''
	print "Create Quiz\n" #TODO
	return master_rtr(request, 'quiz/create-quiz.html', {'courses': Course.objects.all()})

def show_quiz(request, course, page_slug):
	''' show_Quiz View
		This view displays a quiz on the screen. The user can then answer the
		questions and submit the result
	'''
	quiz = Quiz.objects.get(slug=page_slug)
	quizTitle = quiz.text
	questions = quiz.questions.all().order_by("order")

	return master_rtr(request, 'quiz/viewQuiz.html', \
			            {'course':course, 'course_slug':course, \
							 'pid':page_slug, 'quizTitle':quizTitle, \
							 'page_slug':page_slug, 'questions':questions})

def submitQuiz(request, course_slug, page_slug):
	''' submitQuiz View
		This view will submit a quiz and create a statistic in the database. It will give the user
		their score and then direct the user to the appropriate path
	'''
	return master_rtr(request, 'quiz/submitQuiz.html', \
			{'course':course_slug, 'course_slug':course_slug, \
			 'page_slug':page_slug, 'pid':page_slug})

def edit_quiz(request, course_slug, page_slug):
	''' edit_quiz View
		This view allows an instructor or other priviledged user to edit a quiz. The instructor can add, modify,
		or remove questions and other quiz attributes. The modified quiz is then submitted to the database.

		Note 1) Pressing "New Multiple Choice Question" will discard any changes made to the quiz, returning it 
				to its previous state but with a new multiple choice question appended at the end
	'''
	quiz = Quiz.objects.get(slug=page_slug)
	if (request.method == "POST"):
		if "Save" in request.POST:
			page_slug = saveQuiz(request, course_slug, page_slug)
			if (page_slug == -1):
				print "Bad question ordering!"
			else:
				return HttpResponseRedirect(reverse('pages.views.show_page',\
																args=[course_slug, page_slug]))

		if "Cancel" in request.POST:
			return HttpResponseRedirect(reverse('pages.views.show_page',\
															args=[course_slug, page_slug]))

		if "Delete" in request.POST:
			removeQuiz(request, course_slug, pid)
			return HttpResponseRedirect(reverse('pages.views.show_page',\
															args=[course_slug, page_slug]))

		if "NewMultQuestion" in request.POST:
			addMultipleChoiceQuestion(request, course_slug, page_slug)
			return HttpResponseRedirect(reverse('pages.views.show_page',\
															args=[course_slug, page_slug]))

	pages = Course.objects.get(slug=course_slug).pages.all()
	questions = quiz.questions.all().order_by("order")
	return master_rtr(request, 'quiz/edit_quiz.html', \
			{'course':course_slug, 'course_slug':course_slug, \
			 'pid':page_slug, 'pages':pages, 'quiz':quiz, 'questions':questions})
