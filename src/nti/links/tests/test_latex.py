#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import assert_that

from zope import component

from nti.assessment import interfaces
from nti.assessment import response, solution
from nti.assessment import grade_one_response
from nti.assessment._latexplastexdomcompare import _mathChildIsEqual as mce

from nti.assessment.tests.test_solution import grades_right, grades_wrong

from nti.testing.matchers import is_true, is_false
from nti.testing.matchers import verifiably_provides

from nti.assessment.tests import AssessmentTestCase

class TestLatex(AssessmentTestCase):

	def test_simple_grade(self):

		soln = solution.QLatexSymbolicMathSolution( r"$\frac{1}{2}$" )
		assert_that( soln, verifiably_provides( interfaces.IQLatexSymbolicMathSolution ) )

		rsp = response.QTextResponse( soln.value )

		grader = component.getMultiAdapter( (None, soln, rsp), interfaces.IQSymbolicMathGrader )
		assert_that( grader(  ), is_true() )
		assert_that( soln, grades_right( soln.value ) )


	def test_simple_grade_with_numeric_parens(self):
		# We don't get it right, but we don't blow up either
		soln = solution.QLatexSymbolicMathSolution( r"$6$" )

		rsp = response.QTextResponse(  r"$3(2)$" )

		grader = component.getMultiAdapter( (None, soln, rsp), interfaces.IQSymbolicMathGrader )
		assert_that( grader(  ), is_false() )


	def test_simple_grade_require_trailing_units(self):
		soln = solution.QLatexSymbolicMathSolution( r"$\frac{1}{2}$", ('day',) )

		rsp = response.QTextResponse( soln.value + " day" )

		grader = component.getMultiAdapter( (None, soln, rsp), interfaces.IQSymbolicMathGrader )
		assert_that( grader(  ), is_true() )
		assert_that( soln, grades_right( soln.value + " day" ) )

		rsp = response.QTextResponse( soln.value )

		grader = component.getMultiAdapter( (None, soln, rsp), interfaces.IQSymbolicMathGrader )
		assert_that( grader(  ), is_false() )
		assert_that( soln, grades_wrong( soln.value ) )

	def test_simple_grade_optional_trailing_units(self):
		soln = solution.QLatexSymbolicMathSolution( r"$\frac{1}{2}$", ('day','') )

		rsp = response.QTextResponse( soln.value + " day" )

		grader = component.getMultiAdapter( (None, soln, rsp), interfaces.IQSymbolicMathGrader )
		assert_that( grader(  ), is_true() )
		assert_that( soln, grades_right( soln.value + " day" ) )

		rsp = response.QTextResponse( soln.value )

		grader = component.getMultiAdapter( (None, soln, rsp), interfaces.IQSymbolicMathGrader )
		assert_that( grader(  ), is_true() )
		assert_that( soln, grades_right( soln.value ) )

	def test_simple_grade_forbids_trailing_units(self):
		soln = solution.QLatexSymbolicMathSolution( r"$\frac{1}{2}$", () )

		rsp = response.QTextResponse( soln.value + " day" )

		grader = component.getMultiAdapter( (None, soln, rsp), interfaces.IQSymbolicMathGrader )
		assert_that( grader(  ), is_false() )
		assert_that( soln, grades_wrong( soln.value + " day" ) )

		rsp = response.QTextResponse( soln.value )

		grader = component.getMultiAdapter( (None, soln, rsp), interfaces.IQSymbolicMathGrader )
		assert_that( grader(  ), is_true() )
		assert_that( soln, grades_right( soln.value ) )

	def test_simple_grade_accept_trailing_percent(self):
		for soln_text in "$75$", "75": # with/out surrounding $

			soln = solution.QLatexSymbolicMathSolution( soln_text )
			assert_that( soln, grades_right( soln_text ) )

			responses = ("75", r"$75 \%$", r"$75\%$", r"75 \%", r"75\%")

			# No units at all. Legacy behaviour.
			for r in responses:
				rsp = response.QTextResponse( r )
				# Directly grade
				assert_that( soln, grades_right( rsp ) )
				# The adapter layers also do the right thing
				assert_that( grade_one_response( r, [soln_text] ), is_true() )

			# With units specified with and without space
			# required
			soln.allowed_units = [u'\uff05'] # full-width percent
			for r in responses[1:]: # the first one can't work, it's missing unit
				rsp = response.QTextResponse( r )
				assert_that( soln, grades_right( rsp ) )

			# optional
			soln.allowed_units.append( '' )
			for r in responses:
				rsp = response.QTextResponse( r )
				assert_that( soln, grades_right( rsp ) )


	def test_grade_empty(self):
		rsp = response.QTextResponse( "" )
		soln = solution.QLatexSymbolicMathSolution( r"$\frac{1}{2}$" )

		grader = component.getMultiAdapter( (None, soln, rsp), interfaces.IQSymbolicMathGrader )
		assert_that( grader(  ), is_false() )

	def test_grade_sympy_parse_problem(self):
		rsp = response.QTextResponse( "'''" ) # Notice an unterminated string
		soln = solution.QLatexSymbolicMathSolution( r"1876" )

		grader = component.getMultiAdapter( (None, soln, rsp), interfaces.IQSymbolicMathGrader )
		assert_that( grader(  ), is_false() )

	def test_grade_plastex_parse_problem(self):
		soln = solution.QLatexSymbolicMathSolution(u'16')
		# Seen in real life. The browser's GUI editor makes this relatively
		# easy to construct. Hopefully it can redisplay it, too
		rsp = response.QTextResponse('\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{\\frac{1}{1}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}')

		grader = component.getMultiAdapter( (None, soln, rsp), interfaces.IQSymbolicMathGrader )
		assert_that( grader(), is_false() )

	def test_grade_sympy_memory_error(self):
		soln = solution.QLatexSymbolicMathSolution(u'16')
		# Seen in real life, causes a MemoryError sometimes. The browser's GUI editor makes this relatively
		# easy to construct. Hopefully it can redisplay it, too

		rsp = response.QTextResponse(u'\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(2.72\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)', u'', u'\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(\\left(2.72\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)\\right)')

		grader = component.getMultiAdapter( (None, soln, rsp), interfaces.IQSymbolicMathGrader )
		assert_that( grader(), is_false() )


	def test_math_child_is_equal_cases(self):

		class MathChild(object):
			OTHER_NODE = 0
			TEXT_NODE = 1
			ELEMENT_NODE = 2
			DOCUMENT_FRAGMENT_NODE = 3

			nodeType = 0
			childNodes = ()
			arguments = ()

			textContent = ''

		child1 = MathChild()
		child2 = MathChild()
		assert_that( mce( child1, child2 ), is_true() )

		# diff types
		child2.nodeType = 4
		assert_that( mce( child1, child2 ), is_false() )

		child2.nodeType = child1.nodeType = child1.ELEMENT_NODE
		# back to equal
		assert_that( mce( child1, child2 ), is_true() )

		# diff arguments
		child2.arguments = (1,)
		assert_that( mce( child1, child2 ), is_false() )

		child2.arguments = ()
		assert_that( mce( child1, child2 ), is_true() )

		# diff child nodes
		child2.childNodes = (MathChild(),)
		assert_that( mce( child1, child2 ), is_false() )
