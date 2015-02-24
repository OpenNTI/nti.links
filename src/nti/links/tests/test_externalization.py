#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import all_of
from hamcrest import has_key
from hamcrest import not_none
from hamcrest import has_entry
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import has_property
does_not = is_not

import os
import json

from nti.assessment.randomized.interfaces import IQuestionBank
from nti.assessment.randomized.interfaces import IQuestionIndexRange
from nti.assessment.question import QFillInTheBlankWithWordBankQuestion

from nti.externalization import internalization

from nti.externalization.tests import externalizes

from nti.assessment.tests import AssessmentTestCase

from nti.testing.matchers import verifiably_provides

GIF_DATAURL = b'data:image/gif;base64,R0lGODlhCwALAIAAAAAA3pn/ZiH5BAEAAAEALAAAAAALAAsAAAIUhA+hkcuO4lmNVindo7qyrIXiGBYAOw=='

class TestExternalization(AssessmentTestCase):

	def test_file_upload(self):
		ext_obj = {
			'MimeType': 'application/vnd.nextthought.assessment.uploadedfile',
			'value': GIF_DATAURL,
			'filename': r'c:\dir\file.gif',
			'name':'ichigo'
		}

		assert_that(internalization.find_factory_for(ext_obj),
					 is_(not_none()))

		internal = internalization.find_factory_for(ext_obj)()
		internalization.update_from_external_object(internal,
													 ext_obj,
													 require_updater=True)

		# value changed to URI
		assert_that(ext_obj, does_not(has_key('value')))
		assert_that(ext_obj, has_key('url'))

		# We produced an image file, not a plain file
		assert_that(internal.getImageSize(), is_((11, 11)))
		# with the right content time and filename
		assert_that(internal, has_property('mimeType', 'image/gif'))
		assert_that(internal, has_property('filename', 'file.gif'))
		assert_that(internal, has_property('name', 'ichigo'))

		assert_that(internal, externalizes(all_of(	has_key('FileMimeType'),
													has_key('filename'),
													has_key('name'),
													has_entry('url', none()),
													has_key('CreatedTime'),
													has_key('Last Modified'))))
		# But we have no URL because we're not in a connection anywhere

	def test_file_upload2(self):
		# Temporary workaround for iPad bug.
		ext_obj = {
			'MimeType': 'application/vnd.nextthought.assessment.quploadedfile',
			'value': GIF_DATAURL,
			'filename': r'c:\dir\file.gif',
			'name':'ichigo'
		}

		assert_that(internalization.find_factory_for(ext_obj),
					 is_(not_none()))

		internal = internalization.find_factory_for(ext_obj)()
		internalization.update_from_external_object(internal,
													 ext_obj,
													 require_updater=True)

		# value changed to URI
		assert_that(ext_obj, does_not(has_key('value')))
		assert_that(ext_obj, has_key('url'))

		# We produced an image file, not a plain file
		assert_that(internal.getImageSize(), is_((11, 11)))
		# with the right content time and filename
		assert_that(internal, has_property('mimeType', 'image/gif'))
		assert_that(internal, has_property('filename', 'file.gif'))
		assert_that(internal, has_property('name', 'ichigo'))

		assert_that(internal, externalizes(all_of(	has_key('FileMimeType'),
													has_key('filename'),
													has_key('name'),
													has_entry('url', none()),
													has_key('CreatedTime'),
													has_key('Last Modified'))))
		# But we have no URL because we're not in a connection anywhere

	def test_modeled_response_uploaded(self):
		ext_obj = {
			'MimeType': 'application/vnd.nextthought.assessment.modeledcontentresponse',
			'value': ['a part'],
		}

		assert_that(internalization.find_factory_for(ext_obj),
					 is_(not_none()))

		internal = internalization.find_factory_for(ext_obj)()
		internalization.update_from_external_object(internal,
													 ext_obj,
													 require_updater=True)

		assert_that(internal, has_property('value', is_(('a part',))))


	def test_wordbankentry(self):
		ext_obj = {
			u'Class': 'WordEntry',
			u'MimeType': u'application/vnd.nextthought.naqwordentry',
			u'lang': u'en',
			u'wid': u'14',
			u'word': u'at',
		}

		assert_that(internalization.find_factory_for(ext_obj),
					is_(not_none()))

		internal = internalization.find_factory_for(ext_obj)()
		internalization.update_from_external_object(internal,
													 ext_obj,
													 require_updater=True)

		assert_that(internal, has_property('word', is_('at')))
		assert_that(internal, has_property('wid', is_('14')))
		assert_that(internal, has_property('lang', is_('en')))
		assert_that(internal, has_property('content', is_('at')))

	def test_wordbank(self):
		ext_obj = {
			u'Class': 'WordBank',
			u'MimeType': u'application/vnd.nextthought.naqwordbank',
			u'entries':[ {u'Class': 'WordEntry',
						  u'MimeType': u'application/vnd.nextthought.naqwordentry',
						  u'lang': u'en',
						  u'wid': u'14',
						  u'word': u'at'}
						],
			u'unique':False
			}

		assert_that(internalization.find_factory_for(ext_obj),
					is_(not_none()))

		internal = internalization.find_factory_for(ext_obj)()
		internalization.update_from_external_object(internal,
													 ext_obj,
													 require_updater=True)

		assert_that(internal, has_length(1))
		assert_that(internal, has_property('unique', is_(False)))

		word = internal.get('14')
		assert_that(word, has_property('content', 'at'))

	def test_question(self):
		internal = QFillInTheBlankWithWordBankQuestion()
		assert_that(internal, externalizes(all_of(has_entry('Class', 'Question')))),

	def test_regex(self):
		ext_obj = {u'MimeType': u'application/vnd.nextthought.naqregex',
				   u'pattern': u"(^yes\\s*[,|\\s]\\s*I will(\\.)?$)|(^no\\s*[,|\\s]\\s*I (won't|will not)(\\.)?$)",
				   u'Class': 'RegEx',
				   u'solution': u'yes, I will'}
		assert_that(internalization.find_factory_for(ext_obj),
					is_(not_none()))

		internal = internalization.find_factory_for(ext_obj)()
		internalization.update_from_external_object(internal,
													 ext_obj,
													 require_updater=True)

		assert_that(internal, has_property('solution', is_(u'yes, I will')))
		assert_that(internal, has_property('pattern', is_(u"(^yes\\s*[,|\\s]\\s*I will(\\.)?$)|(^no\\s*[,|\\s]\\s*I (won't|will not)(\\.)?$)")))

	def test_regex_part(self):
		ext_obj = {u'MimeType': 'application/vnd.nextthought.assessment.fillintheblankshortanswerpart',
					'explanation': u'',
					'content': u'Will you visit America next year?',
					'solutions': [
									{u'MimeType': 'application/vnd.nextthought.assessment.fillintheblankshortanswersolution',
									 'value': {u'001': {u'MimeType': u'application/vnd.nextthought.naqregex',
														 'pattern': u"(^yes\\s*[,|\\s]\\s*I will(\\.)?$)|(^no\\s*[,|\\s]\\s*I (won't|will not)(\\.)?$)",
														 u'Class': 'RegEx',
														 'solution': u'yes, I will'}},
									 u'Class': 'FillInTheBlankShortAnswerSolution',
									 'weight': 1.0}
								 ],
				   u'Class': 'FillInTheBlankShortAnswerPart',
				    'hints': []}

		assert_that(internalization.find_factory_for(ext_obj),
					is_(not_none()))

		internal = internalization.find_factory_for(ext_obj)()
		internalization.update_from_external_object(internal, ext_obj,
													require_updater=True)
		hash(internal)

		assert_that(internal, has_property('solutions', has_length(1)))
		sol = internal.solutions[0]
		assert_that(sol, has_property('value', has_entry('001', has_property('solution', 'yes, I will'))))

	def test_question_bank(self):
		path = os.path.join(os.path.dirname(__file__), "questionbank.json")
		with open(path, "r") as fp:
			ext_obj = json.load(fp)

		factory = internalization.find_factory_for(ext_obj)
		assert_that(factory, is_(not_none()))

		internal = factory()
		internalization.update_from_external_object(internal, ext_obj, require_updater=True)

		ntiid = u"tag:nextthought.com,2011-10:OU-NAQ-BIOL2124_F_2014_Human_Physiology.naq.set.qset:intro_quiz1"
		internal.ntiid = ntiid

		assert_that(internal, verifiably_provides(IQuestionBank) )

		assert_that(internal, has_property('draw', is_(5)))
		assert_that(internal, has_property('questions', has_length(20)))

		internal.draw = 2
		internal.ranges = [IQuestionIndexRange([0,5]), IQuestionIndexRange([6, 10])]

		assert_that(internal, externalizes(all_of(	has_entry('draw', is_(2)),
													has_entry('NTIID', is_(ntiid)),
													has_entry('Class', is_('QuestionSet')),
													has_entry('MimeType', is_('application/vnd.nextthought.naquestionbank')),
													has_entry('ranges', has_length(2)))))
