''' 
URL to View Regular Expression mappings

@author Andrew J. Musselman
'''
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
	(r'.*', 'stats.views.display_course_stats'),
)
