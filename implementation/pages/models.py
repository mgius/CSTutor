'''
Models file for page related classes

Contains the Overall "Page" class, plus the Classes that are primarily
contained within a Page, such as Quiz and Lesson. In addition it contains
classes for path, question, codeQuestion, multipleChoiceQuestion, and answer.

Author(s): Russell Mezzetta, Mark Gius, James Pearson

'''
from django.db import models
from courses.models import Course

from django.core.exceptions import ObjectDoesNotExist

# Create your models here.

class Page(models.Model):
	'''
	A single unit of a course

	A page contains links to other pages based on the Course flow.
	'''
	course = models.ForeignKey(Course, related_name='pages')
	slug = models.SlugField(unique=True)
	name = models.TextField()
	left = models.IntegerField(db_index=True)
	right = models.IntegerField(db_index=True)

	def __unicode__(self):
		return self.name

	@models.permalink
	def get_absolute_url(self):
		return ('page.views.show_page', [self.course.slug, self.slug])
