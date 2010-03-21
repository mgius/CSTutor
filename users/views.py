'''
users/views.py - This is where all user-related pages are rendered, such as profile, login, logout, registerNewUser...
@author John Hartquist
@author Russell Mezzetta
'''
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from home.views import master_rtr
from user import registerNewUser, loginWrapper, updateEmail, changePassword, updateName, deleteUser
from courses.course import addUser

def show_profile(request):
	'''
	Displays the profile of the user that is currently logged in

	@pre user.is_authenticated() == True
	@post

	@author John Hartquist 
	'''
	#print 'in show_profile'

	#make sure user is logged in
	if request.user.is_authenticated():
		#check if method was post
		if (request.method=="POST"):
			if (request.POST["form"] == "Change E-mail"):
				status = updateEmail(request)
				if status == 0:
					return master_rtr(request, 'user/profile.html', {'user': request.user})
				else:
					return master_rtr(request, 'user/profile.html', 
		                                       {'user': request.user,
							'emailError': "Invalid E-mail Address"})

			if (request.POST["form"] == "Change Password"):
				status = changePassword(request)
				if status == 1:
					return master_rtr(request, 'user/profile.html', 
		                                       {'user': request.user,
											    'passError': "Incorrect current password"})					   
				elif status == 2:
					return master_rtr(request, 'user/profile.html', 
		                                       {'user': request.user,
											    'passError': "Passwords do not match"})	
			if (request.POST["form"] == "Delete Account"):
				return master_rtr(request, 'user/confirmDelete.html')
			
			if (request.POST["form"] == "Update Name"):
				status = updateName(request)
				if status == 0:
					return master_rtr(request, 'user/profile.html', {'user': request.user, 'nameMessage':"Update Successful" })
			if (request.POST["form"] == "Yes"):
				status = deleteUser(request)
				if status == 0:
					return HttpResponseRedirect(reverse('home.views.show_homepage'))		
			
			
		return master_rtr(request, 'user/profile.html', {'user':request.user})
	else:
		return master_rtr(request, 'user/notloggedin.html')
	
def show_logout(request):
	'''
	Logs out the current user

	@pre
	@post request.user.is_authenticated() == false

	@author John Hartquist
	@author Russell Mezzetta
	'''
	#russ--making logout not really log people out in certain cases
	username = None
	lastCourseSlug = None
	if request.user.is_authenticated() == True:
		if 'rememberme' in request.session:
		   username = request.user.username

	#logout flushes the contents of the session/cookie
	logout(request)
	if username != None:
		request.session['username'] = username
		request.session['rememberme'] = True

	return master_rtr(request, 'user/logout.html')

def show_login(request):
	'''
	This shows the login page and displays any errors.
	@pre request is a requestobject
	@post

	@author Russell Mezzetta
	'''
	#if the user is still logged in, redirect them to homepage, don't show login
	if request.user.is_authenticated():
		#if 'autologin' in request.session and request.session['autologin'] == True:
		#		return HttpResponseRedirect(reverse('home.views.show_homepage'))
		return HttpResponseRedirect(reverse('home.views.show_homepage'))

	if request.method == 'POST':
		#form was submitted
		username = request.POST['username']
		password = request.POST['password']
		#checkboxes don't put anything in post if they are unchecked so we have to do a little
		#extra work. This involves making a list of the possible checkboxes.
		checkboxList = request.POST.getlist('anonymous')
		checkboxList += request.POST.getlist('autologin')
		checkboxList += request.POST.getlist('rememberme')
		#set the cookie to expire when browser closes(may be changed below)
		request.session.set_expiry(0)

		if "anonymous" in checkboxList:
			#bypass login
			#if the session has data in it, set it to false, set cookie to expire when browser closes
			#if 'autologin' in request.session:
			#	request.session['autologin'] = False
			#if 'rememberme' in request.session:
			#	request.session['rememberme'] = False
			#clear the session
			request.session.flush()
			return HttpResponseRedirect(reverse('home.views.show_homepage'))

		#all autologin will do is make sure the cookie doesn't expire on browser close
		if "autologin" in checkboxList:
			#set cookie/session to expire in 2 weeks (1209600 is # of seconds in 2 weeks)
			request.session.set_expiry(1209600)
			request.session['autologin'] = True
		#else:
		#	request.session['autologin'] = False

		if "rememberme" in checkboxList:
			#save this in their session(auto fill username)
			request.session.set_expiry(1209600)
			request.session['rememberme'] = True
			request.session['username'] = username
		else:
			request.session['rememberme'] = False
			request.session['username'] = ""
		
		ret = loginWrapper(request, username, password)
		if ret == 0:
			#print "successful login"
			# grab the "next" var from the GET dict, and redirect there
			if 'next' in request.GET:
				return HttpResponseRedirect(request.GET['next'])
			else:
			   # send em to the index
				return HttpResponseRedirect(reverse('home.views.show_homepage'))
		elif ret == 1:
			# Return an 'invalid login' error message.
			#print "invalid login"
			return master_rtr(request, 'user/login.html', {'message': "Please try again, Invalid Username/Password"})
		else:#ret == 2:
			# Return a 'disabled account' error message
			#print "account marked as inactive"
			return master_rtr(request, 'user/login.html', {'message': "Account marked as inactive, contact System Admins"})
	else:
		#form has not yet been submitted (first time visiting login page)
		#check if username is in the session so we can prefill the username field
		if 'username' in request.session:
			return master_rtr(request, 'user/login.html', {'loginusername':request.session['username']})
		else:
			return master_rtr(request, 'user/login.html')

def show_register_new_user(request):
	'''
	This def shows the register new user page
	@pre request is a requestobject
	
	@author Russell Mezzetta
	'''
	if request.method == 'POST':
		#form was submitted
		username = request.POST['username']
		password = request.POST['password']
		vpassword = request.POST['verifypassword']
		email = request.POST['email']
		firstN = request.POST['firstname']
		lastN = request.POST['lastname']
		#send form data to registerNewUser function
		ret = registerNewUser(username, password, vpassword, firstN, lastN, email)
		if ret == 0:
			#successful registration
			#return render_to_response('user/login.html', {'message': "User Registration Successful"})
			#TODO create a response like "success!"
			# attempt to enroll the user in their temporary courses, if possible
			if "anonCourses" in request.session:
				user = User.objects.get(username=username)
				for c in request.session['anonCourses']:
					addUser(c, user, True)
			return HttpResponseRedirect(reverse('users.views.show_login'))
		elif ret == 1:
			errorMsg = "That username is already taken"
		elif ret == 2:
			errorMsg = "Passwords do not match"
		elif ret == 3:
			errorMsg = "The username field is empty"
		elif ret == 4:
			errorMsg = "The password field is empty"
		else: #ret == 5
			errorMsg = "Either first name or last name field is empty"
		return master_rtr(request, 'user/register-new-user.html', {'message': errorMsg})
	else:
		return master_rtr(request, 'user/register-new-user.html')

