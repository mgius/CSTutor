from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from courses.models import Course
from models import Page
from question.models import MultipleChoiceQuestion
from question.models import CodeQuestion
from home.views import master_rtr

'''
Views file for quiz related views

This file contains methods for creating a quiz and showing a quiz. More methods will be added to this file in time.

@author Evan Kleist
'''

def create_quiz(request):
	''' create_Quiz View
		This view will create a quiz and take the user to the quiz editor screen.
	'''
	print "Create Quiz\n" #TODO
	return master_rtr(request, 'quiz/create-quiz.html', {'courses': Course.objects.all()})

def show_quiz(request, course, pid):
	''' show_Quiz View
		This view displays a quiz on the screen. The user can then answer the
		questions and submit the result
	'''
	quiz = Page.objects.get(slug=pid)
	quiz = quiz.quiz
	quizTitle = quiz.text
	questions = quiz.questions.all().order_by("order")

	return master_rtr(request, 'quiz/viewQuiz.html', {'course':course, 'pid':pid, 'quizTitle':quizTitle, 'questions':questions})

def submitQuiz(request, course_slug, pid):
	return master_rtr(request, 'quiz/submitQuiz.html', {'course':course_slug, 'pid':pid})
