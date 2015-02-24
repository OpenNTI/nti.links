#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import assert_that

import plasTeX.Base

from nti.assessment import grade_one_response, assess
from nti.assessment.interfaces import IResponseToSymbolicMathConverter

from nti.assessment._latexplastexconverter import factory
from nti.assessment._latexplastexdomcompare import _mathIsEqual as mathIsEqual
from nti.assessment._latexplastexconverter import _mathTexToDOMNodes as mathTexToDOMNodes

from nti.testing.matchers import validly_provides

from nti.assessment.tests import AssessmentTestCase

class TestAssessment(AssessmentTestCase):

	def test_latex_factory(self):
		from nti.assessment.response import QTextResponse
		rsp = QTextResponse('') # Empty
		assert_that( factory( None, rsp ), validly_provides( IResponseToSymbolicMathConverter ) )
		rsp = QTextResponse( '1' ) # Non-empty
		assert_that( factory( None, rsp ), validly_provides( IResponseToSymbolicMathConverter ) )

	def test_mathTexToDOM(self):
		mathStrings = ['$1$','$1+2$','$\\frac{1}{2}$']

		maths = mathTexToDOMNodes(mathStrings)

		self.assertEqual(len(mathStrings), len(maths),'Expected %d nodes but got %d' % (len(mathStrings), len(maths)))

		for math in maths:
			self.assertIsInstance(math, plasTeX.Base.Math.math, 'Expected all nodes to be math nodes but got %s'%math)

	def test_mathequalsistransitive(self):
		math1, math2, math3 = mathTexToDOMNodes(['$10 $','$10$',' $ 10$'])

		self.assertMathNodesEqual(math1, math2)
		self.assertMathNodesEqual(math2, math3)

		self.assertMathNodesEqual(math1, math3, '%s == %s and %s == %s but %s != %s!'\
						 %(math1.source, math2.source, math2.source, math3.source, math1.source, math3.source))

	def test_naturalnumbers(self):
		#Test things that should be equal are
		math1, math2, math3, math4 = mathTexToDOMNodes(['$7$','$ 7$',' $ 7$','$ 7 $'])

		self.assertMathNodesEqual(math1, math2)
		self.assertMathNodesEqual(math1, math3)
		self.assertMathNodesEqual(math1, math4)

		math1, math2 = mathTexToDOMNodes(['$7$','$7.0$'])

		self.assertMathNodesEqual(math1, math2)


		#Test things that should NOT be equal are not
		math1, math2, math3, math4 = mathTexToDOMNodes(['$7$','$7.01$','$9$', '$70$'])

		self.assertMathNodesNotEqual(math1, math2)
		self.assertMathNodesNotEqual(math1, math3)
		self.assertMathNodesNotEqual(math1, math4)

	def test_simplemacros_nokids(self):
		#Test things that should be equal are
		math1, math2, math3, math4 = mathTexToDOMNodes(['$\\frac{1}{2}$','$\\frac{1 }{ 2 }$',' $\\frac{ 1 }{2}$','$ \\frac {1} {2}$'])

		self.assertMathNodesEqual(math1, math2)
		self.assertMathNodesEqual(math1, math3)
		self.assertMathNodesEqual(math1, math4)

		math1, math2, math3, math4 = mathTexToDOMNodes(['$\\sqrt{2}$','$\\sqrt{ 2 }$','$\\sqrt[3]{2}$','$ \\sqrt[3]{2}$'])

		self.assertMathNodesEqual(math1, math2)
		self.assertMathNodesEqual(math3, math4)


		math1, math2, math3, math4 = mathTexToDOMNodes(['$\\frac{1}{2}$','$\\frac{2}{4}$','$1/2 $','$ \\frac{4}{8}$'])

		self.assertMathNodesNotEqual(math1, math2)
		self.assertMathNodesNotEqual(math1, math3)
		self.assertMathNodesNotEqual(math1, math4)

		math1, math2, math3, math4 = mathTexToDOMNodes(['$\\sqrt{2}$','$\\sqrt{ 4 }$','$\\sqrt[3]{2}$','$ \\sqrt[43]{2}$'])

		self.assertMathNodesNotEqual(math1, math2)
		self.assertMathNodesNotEqual(math3, math4)

	def test_exprinfractions(self):
		math1, math2 = mathTexToDOMNodes(['$\\frac{1+x}{2}$','$\\frac{1 + x}{2}$'])
		self.assertMathNodesEqual(math1,math2)

	def test_expr(self):
		math1, math2, math3, math4 = mathTexToDOMNodes(['$1 + x$','$1+x$','$x+1$','$x + 1$'])
		self.assertMathNodesEqual(math1,math2)
		self.assertMathNodesEqual(math3,math4)

		self.assertMathNodesEqual(math1,math3)
		self.assertMathNodesEqual(math2,math4)

	def test_symbols(self):
		math1, math2, math3, math4 = mathTexToDOMNodes(['$25\\pi$','$ 25 \\pi$','$25 \\pi $','$ 25\\pi $'])
		self.assertMathNodesEqual(math1, math2)
		self.assertMathNodesEqual(math1, math3)
		self.assertMathNodesEqual(math1, math4)

		math1, math2 = mathTexToDOMNodes(['$25\\pi$','$42\\pi$'])
		self.assertMathNodesNotEqual(math1, math2)

	def test_tuples(self):

		math1, math2, math3, math4 = mathTexToDOMNodes(['$(-1, 2)$','$(-1,2)$','$( -1, 2 )$','$(-1,2)$'])
		self.assertMathNodesEqual(math1, math2)
		self.assertMathNodesEqual(math1, math3)
		self.assertMathNodesEqual(math1, math4)

		math1, math2 = mathTexToDOMNodes(['$(1, 2)$','$(-1, -2)$'])
		self.assertMathNodesNotEqual(math1, math2)

	def test_time(self):
		#Test things that should be equal are
		math1, math2, math3, math4, math5 = mathTexToDOMNodes(['$3:30$', '$ 3:30$','$3:30 $','$ 3:30 $','$3 : 30$'])

		self.assertMathNodesEqual(math1, math2)
		self.assertMathNodesEqual(math1, math3)
		self.assertMathNodesEqual(math1, math4)
		self.assertMathNodesEqual(math1, math5)

		#Things that should not be equal
		math1, math2, math3, math4, math5 = mathTexToDOMNodes(['$3:30$', '$3:31$','$3:31 $','$ 5:30 $','$330$'])

		self.assertMathNodesNotEqual(math1, math2)
		self.assertMathNodesNotEqual(math1, math3)
		self.assertMathNodesNotEqual(math1, math4)
		self.assertMathNodesNotEqual(math1, math5)

	def test_simplemacros_kids(self):
		#Test things that should be equal are
		math1, math2, math3, math4 = mathTexToDOMNodes(['$3.2x10^32$','$3.2 x 10^32$','$1.4x10^\\frac{1}{2}$','$ 1.4 x  10^\\frac{ 1}{2}$'])

		self.assertMathNodesEqual(math1, math2)
		self.assertMathNodesEqual(math3, math4)

		#Things that should not be equal
		math1, math2, math3, math4 = mathTexToDOMNodes(['$3.2x10^32$','$3.2 x 10^33$','$1.14x10^32$','$ 1.4 x  10^32$'])

		self.assertMathNodesNotEqual(math1, math2)
		self.assertMathNodesNotEqual(math3, math4)

	def test_an_unparseable(self):
		_, math2 = mathTexToDOMNodes(('$4\\surd$3', "$4\\surd 3$"))
		self.assertMathNodesNotEqual( None, math2, message="None should not raise error" )

	def test_output_from_mathquill(self):
		# Some real-life output from mathquil

		answers = ( "$(0.5,0.5)$", )
		# as typed directly
		response = "\\left(0.5,0.5\\right)"
		assert_that( grade_one_response( response, answers ), "Parenthesis variations" )
		# as cut and paste
		response = "\\text{(0.5,0.5)}"
		assert_that( grade_one_response( response, answers ), "Text wrapping" )

		answers = (r"$\surd 97 \approx 9.8$",)
		# Bogus
		response = r"\surd\:97\:\approx\:9.8"
		assert_that( grade_one_response( response, answers ), "Broken spacing" )

		response = r"\surd\;97\;\approx\;9.8"
		assert_that( grade_one_response( response, answers ), "Correct explicit spacing spacing" )

	def assertMathNodesEqual(self, math1, math2, message=None):
		if not message:
			message = '%s != %s!' % (math1.source, math2.source)

		self.assertTrue(mathIsEqual(math1, math2), message)

	def assertMathNodesNotEqual(self, math1, math2, message=None):
		if not message:
			message = '%s != %s!' % (math1.source, math2.source)

		self.assertFalse(mathIsEqual(math1, math2), message)

	def test_assess(self):
		quiz = {1 : MockQuiz(['$5.00$','$5$']),
				2 : MockQuiz(['$12$']),
				3 : MockQuiz(['$15.37$']),
				4 : MockQuiz(['$1+x$']),
				5 : MockQuiz(['$\\frac{2}{3}$']),
				6 : MockQuiz(['$10$']),
				7 : MockQuiz(['$42$']),
				8 : MockQuiz(['$210$']),
				9 : MockQuiz(['$6$']),
				10 : MockQuiz(['$0$'])}

		responses = {1: '5', 2: '12', 3: '15.37', 4: '1 + x', 5:'\\frac{2}{3}', 6: '10', \
					 7 : '42', 8: '210', 9: '6', 10: '0'}

		expectedResults = {	1:True, 2:True, 3:True, 4:True, 5:True, 6:True, \
							7:True, 8:True, 9:True, 10:True}
		results = assess(quiz, responses)
		assert_that(results, is_(expectedResults))

		responses[3] = '15'
		responses[10] = '$1$'

		expectedResults[3] = False
		expectedResults[10] = False
		results = assess(quiz, responses)
		assert_that(results, is_(expectedResults))

		responses[4] = '<OMOBJ xmlns="http://www.openmath.org/OpenMath" '+ \
					   'version="2.0" cdbase="http://www.openmath.org/cd"> '+\
					   '<OMA><OMS cd="arith1" name="plus"/><OMI>1</OMI><OMV name="x"/></OMA></OMOBJ>'
		expectedResults[4] = True

		responses[5] = '<OMOBJ xmlns="http://www.openmath.org/OpenMath" '+\
					   'version="2.0" cdbase="http://www.openmath.org/cd"> '+\
					   '<OMA><OMS cd="arith1" name="divide"/><OMI>1</OMI> '+\
					   '<OMS cd="nums1" name="pi"/></OMA></OMOBJ>'

		expectedResults[5] = False
		results = assess(quiz, responses)
		assert_that(results, is_(expectedResults))

	def test_assess_two(self):
		quiz = {1 : MockQuiz(['$(0.4, 0.3)$']) }
		responses = {1: '(0.4, 0.3)'}

		results = assess(quiz, responses)
		assert_that(results, is_({1: True}))

class MockQuiz(object):
	def __init__(self, answers):
		if not answers:
			answers = ['No answer']
		self.answers = answers
