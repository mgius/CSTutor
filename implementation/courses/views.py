'''
	Functions in this file allow an instructor to create a course, add users to the course, search for user names, and remove users. In addition, there are functions that allow a student to join a course. 

@author Jon Inloes
@author James Pearson
@author Mark Gius
@author Matthew Tytel
@author John Hartquist
'''
from django.http import Http404 
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from courses.models import Course
from pages.models import Page
from courses.course import *
from django.db import IntegrityError, transaction
from django.template.defaultfilters import slugify
from home.views import master_rtr
from django.contrib.auth.decorators import login_required
from pages.views import show_page

@login_required
def create_course(request):
	'''
	Creates a new course if course name is long enough
	and the coursename is unique.  If not gives an error.
	Also sets a course to private if the checkbox was checked.

	@author John Hartquist
	@author Matthew Tytel
	'''
	data = {}
	
	if request.method == "POST":
		name = request.POST['coursename'].strip()
		
		private = False;
		if "private" in request.POST:
			private = True;

		# some basic validation
		if len(name) < 1:
			data['message'] = 'A Course name must be at least 1 characters.'
		else:
			try:
				sid = transaction.savepoint()
				c = CreateCourse(name, User.objects.get(username=request.user.username), private)
				transaction.savepoint_commit(sid)
				return HttpResponseRedirect(reverse('pages.views.edit_page', args=[c.slug, c.slug]))
			except IntegrityError:
				transaction.savepoint_rollback(sid)
				data['message'] = 'A Course with that name already exists.'

	return master_rtr(request, 'courses/create_course.html', data)

@login_required
def show_roster(request, course_slug):
	'''
	Displays the roster
	pre: user.isLoggedIn == true
	post: if user.manage then show(roster/index.html) else show(roster/invalid_permissions.html)

	@author Jon Inloes
	'''
	# It is better to get the enrollment by this method, because in this case
	# the database searches using Primary Keys, which are indexed, instead of 
	# username, which is not indexed. -mgius
	#enrollment = Enrollment.objects.get(user__username__exact=request.user.username, course__slug__exact=course_slug)

	failedList = []

	#if there are users that failed to be added from a previous command, then retrieve the list 
	if request.session.has_key('badusers'):
		failedList = request.session['badusers']
		del request.session['badusers']
	
	#retreive the current course
	try:
		course = Course.objects.get(slug=course_slug)	
	except Course.DoesNotExist:
		raise Http404
	
	#retrieve the logged in user
	enrollment = request.user.enrollments.get(course=course)
	
	#check the logged in user's enrollment permissions
	if enrollment.manage:
		enrollments = course.roster.all();

		return master_rtr(request, 'roster/index.html', \
		                  {'course': course, \
		                   'enrollments': enrollments, \
		                   'course_slug': course.slug, 'failedList': failedList})

	else:
		return master_rtr(request, 'roster/invalid_permissions.html', \
		                  {'course': course, \
		                   'course_slug': course.slug })

def show_course(request, course_slug):
	''' 
	Shows the main page of a course. 
	
	@author Mark Gius
	'''
	return show_page(request, course_slug, course_slug)

@login_required
def add_user(request, course_slug):
	'''
	Handles the commands given by the add user screen

	pre: none
	post: db'.contains(user) == true and db'.length == db.length + 1 if !db.contains(user)
	
	@author Jon Inloes
	'''
	#retrieve the course
	course = Course.objects.get(slug=course_slug)

	#retrieve the currently logged in user
	enrollment = request.user.enrollments.get(course=course)

	#check the logged in user's permissions
	if enrollment.manage:	
		#if the request method was a post determine the command that was given
		if request.method == 'POST':
		
			#if the command was an add try to add the user
			if request.POST['command'] == 'add':
				usr = request.POST['username']

				try:
					#if the user exists add it
					user = User.objects.get(username=usr)
					addUser(course, user)

				except User.DoesNotExist:
					#if the user does not exist print error message
					return master_rtr(request, 'adduser/failed.html', \
					                  {'course_slug':course_slug, \
					                   'course': course})
				
				#show the roster screen
				return HttpResponseRedirect(reverse('courses.views.show_roster', args=[course_slug]))

			elif request.POST['command'] == 'search':
				#if the command was a search, search for the user
				
				firstname = request.POST['firstname'].strip()
				lastname = request.POST['lastname'].strip()

				users = User.objects.filter(first_name = firstname, last_name = lastname)

				return master_rtr(request, 'adduser/search.html', \
				                  {'course_slug': course_slug, \
				                   'course':course, \
				                   'users':users, \
				                   'firstname': firstname, \
				                   'lastname': lastname})
		else:
			#display the adduser page
			return master_rtr(request,'adduser/index.html', {'course_slug': course_slug, 'course': course, 'url': request.path})
	else:
		return master_rtr(request, 'roster/invalid_permissions.html', \
				{'course': course, \
				 'course_slug': course_slug})

@login_required
def update_roster(request, course_slug):
	'''
		Updates the roster according to the checkboxes on the page
		pre:none
		post: for all enrollments in db changed(enrollment) in db' 
		      if not removing then db.length = db'.length

		@author Jon Inloes
	'''

	#retrieve the course
	course = Course.objects.get(slug=course_slug)

	#retrieve the currently logged in user
	enrollment = request.user.enrollments.get(course=course)

	#check the logged in user's permissions
	if enrollment.manage:
		editList =  request.POST.getlist('edit')
		manageList = request.POST.getlist('manage')
		statsList = request.POST.getlist('stats')
		removeList = request.POST.getlist('remove')
		enrollments = Enrollment.objects.select_related(depth=1).\
		                                 filter(course__slug__exact=course_slug)

		#for each enrollment
		for enrollment in enrollments:
			changed = False
			try:
				editList.index(enrollment.user.username)
				#if the user does not have edit permission, then set the permission to true
				if not enrollment.edit:
					enrollment.edit = True
					changed = True
			except ValueError:
				#if if the user does have edit permission, then set the permission to false
				if enrollment.edit:
					enrollment.edit = False
					changed = True
			try:
				manageList.index(enrollment.user.username)
				#if the user does not have manage permission, then set the permission to true
				if not enrollment.manage:
					enrollment.manage = True
					changed = True
			except ValueError:
				#if the user does have manage permission, then set the permission to false
				if enrollment.manage:
					enrollment.manage = False
					changed = True
			try:
				statsList.index(enrollment.user.username)
				#if the user does not have stats permission, then set the permission to true
				if not enrollment.stats:
					enrollment.stats = True
					changed = True
			except ValueError:
				#if the user does have stats permission, then set the permission to false
				if enrollment.stats:
					enrollment.stats = False
					changed = True

			#if the user has changed then update it
			if changed:
				enrollment.save()

			try:
				removeList.index(enrollment.user.username)
				#if the remove checkbox was checked attempt to remove the user
				removeUser(enrollment.course,enrollment.user)
			except ValueError:
				pass
		return HttpResponseRedirect(reverse('courses.views.show_roster', \
		                                    args=[course_slug]))
	else:
		return master_rtr(request, 'roster/invalid_permissions.html', \
		                  {'course': course, 'course_slug': course.slug})

def cancel_add(request, course_slug):
	'''
	Redirects to the roster screen when viewing the add user page
	pre: courses.views.show_roster.exists() == true
	post: roster/index.html.isRendered() == true
		
	@author Jon Inloes
	'''
	return HttpResponseRedirect(reverse('courses.views.show_roster', \
	                                    args=[course_slug]))

@login_required
def manage_pending_requests(request, course_slug):
	'''
	Accepts and denies users in the pending request list for a roster
	pre: user.isLoggedIn = True
	post: (for username in acceptList
	         course.enrollments.username.view = True
	      and
	      course.enrollments.length' = course.enrollments.length)
	      (for username in denyList
	         course.enrollments.remove(username)
	      and
	      course.enrollments.length' = course.enrollments.length - denyList.length)

	@author Jon Inloes
	'''
	
	#retrieve the course
	course = Course.objects.get(slug=course_slug)

	#retrieve the logged in user
	enrollment = request.user.enrollments.get(course=course)

	#check the logged in user's permissions
	if enrollment.manage:
		acceptList =  request.POST.getlist('accept')
		denyList = request.POST.getlist('deny')	
		course = Course.objects.select_related(depth=2).get(slug=course_slug)
		enrollments = course.roster.all()

		#for each enrollment in the accept list set the view permission to true
		for enrollment in enrollments:
			user = enrollment.user
			try:
				acceptList.index(enrollment.user.username)
				enrollment.view = True
				enrollment.save()
			except ValueError:
				pass
			try:
				denyList.index(enrollment.user.username)
				removeUser(course,user)
			except ValueError:
				pass
	
		return HttpResponseRedirect(reverse('courses.views.show_roster', \
		                                    args=[course_slug]))

	else:
		return master_rtr(request, 'roster/invalid_permissions.html', \
		                  {'course': course, 'course_slug': course.slug})

def join_course_form(request):
	'''
		Displays a list of unenrolled courses for a user to request to join.

		@author Mark Gius
	'''
	if request.user.is_authenticated():
		enrollmentIds = [e.course.id for e in request.user.enrollments.all()]
		courses = Course.objects.exclude(id__in=enrollmentIds)
	else:
		#anonymous users cannot see private courses
		if "anonCourses" in request.session:
			enrollmentIds = [c.id for c in request.session['anonCourses']]
			courses = Course.objects.exclude(id__in=enrollmentIds).exclude(private=True)
		else:
			courses = Course.objects.exclude(private=True)

	return master_rtr(request, 'courses/join_course_form.html', \
	                  {'join_courses' : courses})

#@login_required //login is not required to join a course
def join_course_request(request):
	'''
	Displays the classes a user can join

	@author Mark Gius
	'''
	courseid = request.POST['courseid']
	course = Course.objects.get(id=courseid)

	if course.private:
		view = False
		redirect = False
	else:
		view = True
		redirect = True


	if request.user.is_authenticated():
		user = User.objects.get(username=request.user.username)

		if addUser(course, user, view):
			message = "Congratulations, you have been added to %s." % course
			if course.private:
				message += "  This is a private course, and your enrollment"
				message += " is pending."  
		else:
			message = "You are already enrolled in %s" % course
			redirect = False
	
	else:
		#anonymous user is joining course
		if "anonCourses" in request.session:
			
			if course in request.session['anonCourses']:
				message = "You are already enrolled in %s" % course
				redirect = False
			else:
				courses = request.session['anonCourses']
				courses.append(course)
				request.session['anonCourses'] = courses
				message = "You have been temporarily added to %s. Register to make this enrollment permanent" % course
				print(request.session['anonCourses'])
		else:
			request.session['anonCourses'] = [course]
			message = "You have been temporarily added to %s" % str(course)
		
		user = "Anonymous user"
		
		
	return master_rtr(request, 'courses/join_course_status.html', \
	                  {'course':course, 'user':user, 'message':message, \
							 'redirect':redirect })

def show_chat(request, course_slug):
	''' 
	Shows the chat for the course

	@author Jon Inloes
	'''

	#retrieve the current course
	try:	
		course = Course.objects.get(slug=course_slug)
	except Course.DoesNotExist:
		raise Http404
		
	return master_rtr(request, 'chat/index.html', {'course_slug': course_slug, 'username': request.user.username, 'course': course})

@login_required
def add_from_file(request, course_slug):
	'''
	Adds usernames from a text file

	@author Jon Inloes
	'''
	course = Course.objects.get(slug=course_slug)
	enrollment = request.user.enrollments.get(course=course)
	failedList = []

	if enrollment.manage:
		#call addUsersFromFile if the user has manage permission
		failedList = addUsersFromFile(course, request.FILES) 
		request.session['badusers']=failedList
		return HttpResponseRedirect(reverse('courses.views.show_roster', \
	                                    args=[course_slug]))
	else:
			return master_rtr(request, 'roster/invalid_permissions.html', \
				               {'course': course, 'course_slug': course.slug})
