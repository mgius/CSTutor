'''
Views file for quiz related views

This file contains methods for creating a quiz and showing a quiz. More methods will be added to this file in time.

@author Evan Kleist
'''

from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404
from courses.models import Course
from models import Page
from models import Quiz
from quiz import *
from question.models import MultipleChoiceQuestion
from question.models import CodeQuestion
from question.question import *
from home.views import master_rtr
from pages.page import insertChildPage

def create_quiz(request, course_slug, page_slug):
	''' create_Quiz View
		This view will create a quiz and take the user to the quiz editor screen.
	'''
	page_slug = safeSlug(page_slug)
	
	if request.method == "POST" and "Create Quiz" in request.POST:
		course = Course.objects.get(slug=course_slug)
		name = request.POST['name']
		newQuiz = Quiz(course=course, name=name, slug=slugify(name), text=name, upToDate=True)
		#what the heck was this line here for?
		#newQuizWorkingCopy = Quiz(course=course, name=name, slug=(newQuiz.slug + "_workingCopy"), text=name)
		insertChildPage(newQuiz, Page.objects.get(slug=page_slug))
		newQuiz = Quiz.objects.get(slug=newQuiz.slug)
		workingCopy = Quiz(course=newQuiz.course, name=newQuiz.name, slug=(newQuiz.slug + "_workingCopy"), text=newQuiz.name, left=0, right=0)
		workingCopy.save()
		return HttpResponseRedirect('/course/' + course_slug + '/page/' + newQuiz.slug + '/edit/')
	else:
		return master_rtr(request, 'page/quiz/create-quiz.html')

def show_quiz(request, course, page_slug):
	''' show_Quiz View
		This view displays a quiz on the screen. The user can then answer the
		questions and submit the result

		If the user is trying to view the working_copy, they are shown the
		regular copy instead. This is to prevent a student from looking
		at unpublished quizzes
	'''
	page_slug = safeSlug(page_slug)

	quiz = Quiz.objects.get(slug=page_slug)
	quizTitle = quiz.text
	questions = quiz.questions.all().order_by("order")
	return master_rtr(request, 'page/quiz/viewQuiz.html', \
			            {'course':course, 'course_slug':course, \
							 'quizTitle':quizTitle, \
							 'page_slug':page_slug, 'questions':questions})

def delete_quiz(request, course_slug, page_slug):
	''' delete_quiz View
		This view confirms deletion of a quiz. The user can then choose
		 to delete the quiz or cancel
	'''
	page_slug = safeSlug(page_slug)
	quiz = Quiz.objects.get(slug=page_slug)

	return master_rtr(request, 'page/quiz/delete_quiz.html', \
			            {'course':course_slug, 'course_slug':course_slug, 'page_slug':page_slug, 'quiz':quiz})

def add_path(request, course_slug, page_slug):
	''' add_path View
		This view allows you to add a path to the quiz. The user can then choose
		 to save the path or cancel
	'''
	page_slug = safeSlug(page_slug)
	quiz = Quiz.objects.get(slug=page_slug)
	course = Course.objects.get(slug=course_slug)
	allPages = course.pages.all()
	pages = []
	for p in allPages:
		if (p.slug == safeSlug(p.slug)):
			pages.append(p)

	return master_rtr(request, 'page/quiz/path.html', \
			            {'course_slug':course_slug, 'page_slug':page_slug, 'pages':pages})


def remove_question(request, course_slug, page_slug, qNum):
	''' remove_question View
		This view confirms deletion of a question. The user can then choose
		 to delete the question or cancel
	'''
	page_slug = safeSlug(page_slug)
	quiz = Quiz.objects.get(slug=page_slug)
	question = quiz.questions.get(order=qNum)

	return master_rtr(request, 'page/quiz/remove_question.html', \
			            {'course':course_slug, 'course_slug':course_slug, 'page_slug':page_slug, 'question':question})

def submitQuiz(request, course_slug, page_slug):
	''' submitQuiz View
		This view will submit a quiz and create a statistic in the database. It will give the user
		their score and then direct the user to the appropriate path
	'''
	page_slug = safeSlug(page_slug)

	# Make sure the course actually exists in the database
	try:
		course = Course.objects.get(slug=course_slug)
	except Course.DoesNotExist:
		raise Http404

	# Make sure the quiz actually exists in the database
	try:
		quiz = Quiz.objects.get(slug=page_slug)
	except Quiz.DoesNotExist:
		raise Http404

	maxScore = len(quiz.questions.all())
	score = 0
	percentage = 100

	if (request.method == "POST"):
		score = scoreQuiz(quiz, request, course_slug, page_slug)
	else:
		return master_rtr(request, 'page/denied.html', {'course':course_slug, 'loggedIn':False})

	if (not (maxScore == 0)):
		percentage = round(float(score) / float(maxScore), 2) * 100
			
	return master_rtr(request, 'page/quiz/submitQuiz.html', \
			{'course':course_slug, 'course_slug':course_slug, \
			 'page_slug':page_slug, 'pid':page_slug, 'score':score, 'maxScore':maxScore, 'percentage':percentage})

def edit_quiz(request, course_slug, page_slug):
	''' edit_quiz View
		This view allows an instructor or other priviledged user to edit a quiz. The instructor can add, modify,
		or remove questions and other quiz attributes. The modified quiz is then submitted to the database.

		Note 1) Pressing "New Multiple Choice Question" will discard any changes made to the quiz, returning it 
				to its previous state but with a new multiple choice question appended at the end
	'''
	page_slug = safeSlug(page_slug)
	# Make sure the course actually exists in the database
	try:
		course = Course.objects.get(slug=course_slug)
	except Course.DoesNotExist:
		raise Http404

	# Make sure the quiz actually exists in the database
	try:
		quiz = Quiz.objects.get(slug=(page_slug))
		workingCopy = Quiz.objects.get(slug=(page_slug + "_workingCopy"))
	except Quiz.DoesNotExist:
		raise Http404

	pages = Course.objects.get(slug=course_slug).pages.all()
	questions = workingCopy.questions.all().order_by("order")
	prerequisites = workingCopy.prerequisites.all()
	paths = workingCopy.paths.all()
	prereqs = []
	errors = []

	for p in prerequisites:
		prereqs.append(p.requiredQuiz.slug)

	if (request.method == "POST"):
		if "Save" in request.POST:
			r = saveQuiz(request, course_slug, page_slug)
			page_slug = safeSlug(r["quiz_slug"])
			errors = r["errors"]
			if (len(errors) == 0):
				return HttpResponseRedirect(reverse('pages.views.show_page', args=[course_slug, page_slug]))

		elif "Cancel" in request.POST:
			return HttpResponseRedirect(reverse('pages.views.show_page', args=[course_slug, page_slug]))

		elif "Delete" in request.POST:
			return delete_quiz(request, course_slug, page_slug)
		elif "ConfirmDelete" in request.POST:
			removeQuiz(quiz)
			return HttpResponseRedirect(reverse('courses.views.show_course', args=[course_slug]))

		elif "Move" in request.POST:
			return HttpResponseRedirect(reverse('pages.views.move_page', args=[course_slug, page_slug]))

		elif "NewMultQuestion" in request.POST:
			addMultipleChoiceQuestion(workingCopy)
			return HttpResponseRedirect(request.path)

		elif "NewCodeQuestion" in request.POST:
			addCodeQuestion(workingCopy)
			return HttpResponseRedirect(request.path)

		elif "Publish" in request.POST:
			r = saveQuiz(request, course_slug, page_slug)
			errors = r["errors"]
			if (len(errors) == 0):
				workingCopy = Quiz.objects.get(slug=(page_slug + "_workingCopy"))
				publishQuiz(workingCopy)
				return HttpResponseRedirect(reverse('pages.views.show_page', args=[course_slug, page_slug]))

		elif "Revert" in request.POST:
			revertQuiz(workingCopy)
			return HttpResponseRedirect(reverse('pages.views.show_page', args=[course_slug, page_slug]))

		elif "AddPath" in request.POST:
			return add_path(request, course_slug, page_slug)
		elif "SubmitPath" in request.POST:
			addPath(workingCopy, request, course_slug)
			return HttpResponseRedirect(request.path)

		for q in questions:
			if ("removeQuestion%s" % q.order) in request.POST:
				return remove_question(request, course_slug, page_slug, q.order)
			if ("confirmRemoveQuestion%s" % q.order) in request.POST:
				removeQuestion(q)
				reorderQuestions(workingCopy)
				return HttpResponseRedirect(request.path)
			if (isMultipleChoiceQuestion(q)):
				q = q.multiplechoicequestion
				if ("addAnswer%s" % q.order) in request.POST:
					addAnswer(q)
					return HttpResponseRedirect(request.path)
				for a in q.answers.all():
					if ("removeAnswerQ%sA%s" % (q.order, a.order)) in request.POST:
						removeAnswer(q, a)
						return HttpResponseRedirect(request.path)

	return master_rtr(request, 'page/quiz/edit_quiz.html', {'course_slug':course_slug, 'page_slug':page_slug, 'pages':pages, 'quiz':workingCopy, 'questions':questions, 'prereqs':prereqs, 'errors':errors, 'paths':paths})
