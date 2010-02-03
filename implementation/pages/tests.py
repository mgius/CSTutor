'''
Unit Tests for Classes in the Page module
@author Mark Gius
'''

from django.test import TestCase
from django.test.client import Client
from courses.models import Course
from pages.models import Page
from pages.page import *

class PageTests(TestCase):
	''' Unit tests and other tests on the Page class and it's related functions
	'''
	fixtures = ['PageTests']
	courseName = 'PageTestsCourse'

	def validateTree(self):
		'''
		Verifies that the left/right indexes of the test Course are valid

		The indexes are valid if for every page in a course, all left/rights are
		unique, the lowest left is 1, and the highest right is the number
		of pages multiplied by two.

		@Post: True if all left/right indexes are unique, and the index range is
		 		 1 -> (# of pages) * 2 inclusive, otherwise False
		
		case no.    inputs           expected output    remark
		1           Valid Course     True
		2           Invalid Course   False  
		'''
		pages = Page.objects.filter(course__name=self.courseName)
		usedNumbers = set([page.left for page in pages]) |\
						  set([page.right for page in pages])

		self.assertEquals(len(pages) * 2, len(usedNumbers))
		self.assertEquals(min(usedNumbers), 1)
		self.assertEquals(max(usedNumbers), len(pages) * 2)

		return True
			
	def test_insertPage(self):
		'''
		Tests adding a new page to the tree as a sibling of an existing
		page
		'''
		olderSibling = Page.objects.get(slug='PageTestsPage1')
		youngerSibling = getNextPage(olderSibling)
		newPage = Page(slug="testAddPageAsSibling", name="testAddPageAsSibling")
		insertPage(newPage, olderSibling)
		self.validateTree()

      # have to reload these
		olderSibling = Page.objects.get(id=olderSibling.id)
		youngerSibling = Page.objects.get(id=youngerSibling.id)

		self.assertEquals(getPrevPage(newPage), olderSibling)
		self.assertEquals(getNextPage(olderSibling), newPage)
		self.assertEquals(getNextPage(newPage), youngerSibling)
		self.assertEquals(getPrevPage(youngerSibling), newPage)

	def test_insertChildPage(self):
		'''
		Tests adding a new page to the tree as a child of an existing page
		'''
		parent = Page.objects.get(slug='PageTestsPage1')
		youngerUncle = getNextPage(parent)

		newPage = Page(slug="testAddPageAsChild", name="testAddPageAsChild")
		insertChildPage(newPage, parent)
		self.validateTree()

		# reload these because their contents have changed
		parent = Page.objects.get(id=parent.id)
		youngerUncle = Page.objects.get(id=youngerUncle.id)

		self.assertEquals(getPrevPage(newPage), parent)
		self.assertEquals(getNextPage(parent), newPage)
		self.assertEquals(getNextPage(newPage), youngerUncle)
		self.assertEquals(getPrevPage(youngerUncle), newPage)

	def test_removePage(self):
		'''
		Tests removing a page from the tree
		'''
		self.assertTrue(True)

	def test_movePage(self):
		'''
		Tests moving a page from one part of the tree to another
		'''
		self.assertTrue(True)

	def test_removePage_multiple(self):
		'''
		Tests removing several pages from the tree
		'''
		self.assertTrue(True)
