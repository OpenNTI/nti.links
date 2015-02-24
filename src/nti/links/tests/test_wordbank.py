#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import equal_to
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import has_entries
from hamcrest import has_property

from nti.assessment.wordbank import WordBank
from nti.assessment.wordbank import WordEntry
from nti.assessment import interfaces as asm_interfaces

from nti.externalization.tests import externalizes

from nti.testing.matchers import verifiably_provides

from nti.assessment.tests import AssessmentTestCase

class TestWordBank(AssessmentTestCase):

	def test_entry(self):
		we = WordEntry(wid='1', word='bankai')
		assert_that(we, verifiably_provides(asm_interfaces.IWordEntry))
		assert_that(we, has_property('lang', is_('en')))
		assert_that(we, externalizes(has_entries('Class', 'WordEntry',
												 'word', 'bankai',
												 'wid', '1',
												 'lang', 'en')))

		lst = ['1', 'bankai']
		awe = asm_interfaces.IWordEntry(lst)
		assert_that(we, is_(equal_to(awe)))

		lst = ['2', 'shikai', 'ja']
		awe = asm_interfaces.IWordEntry(lst)
		assert_that(awe, has_property('wid', is_('2')))
		assert_that(awe, has_property('word', is_('shikai')))
		assert_that(awe, has_property('lang', is_('ja')))

	def test_bank(self):
		entries = [WordEntry(wid='1', word='bankai'),
				   WordEntry(wid='2', word='shikai')]
		bank = WordBank(entries=entries, unique=True)
		assert_that(bank, verifiably_provides(asm_interfaces.IWordBank))
		assert_that(bank, has_length(2))
		assert_that('1' in bank, is_(True))
		assert_that('2x' in bank, is_(False))
		assert_that(bank.contains_id('2'), is_(True))
		assert_that(bank.contains_word('shikai'), is_(True))
		assert_that(bank.contains_word('BANKAI'), is_(True))
		assert_that(bank.contains_word('foo'), is_(False))

		assert_that(bank.words, has_length(2))
		assert_that(sorted(bank.words), is_(['bankai', 'shikai']))

		w1 = bank.get('1')
		assert_that(w1, has_property('wid', is_('1')))
		w2 = bank.get('2')
		assert_that(w2, has_property('wid', is_('2')))
		assert_that(w1, is_not(equal_to(w2)))

		assert_that(bank, externalizes(has_entries('Class', 'WordBank',
												   'unique', True,
												   'entries', has_length(2))))

		assert_that(bank.sorted(), has_length(2))

		new_entries = [WordEntry(wid='2', word='shikai'), WordEntry(wid='1', word='bankai')]
		ab = WordBank(entries=new_entries, unique=True)
		assert_that(bank, is_(equal_to(ab)))

	def test_bank_add(self):
		entries = [WordEntry(wid='1', word='bankai')]
		bank1 = WordBank(entries=entries, unique=True)

		entries = [WordEntry(wid='2', word='shikai')]
		bank2 = WordBank(entries=entries, unique=False)

		bank = bank1 + bank2
		assert_that(bank, has_length(2))
		assert_that('1' in bank, is_(True))
		assert_that('2' in bank, is_(True))
		assert_that(has_property('unique', is_(False)))

		bank = bank1 + None
		assert_that(bank, has_length(1))
		assert_that('1' in bank, is_(True))
		assert_that('2' in bank, is_(False))
		
	def test_biology_words(self):
		entries = [WordEntry(wid='1', word=u"Phospholipase A\u2082"),
				   WordEntry(wid='2', word='Cyclooxygenase'),
				   WordEntry(wid='3', word='Lipoxygenase')]
		bank = WordBank(entries=entries, unique=True)
		assert_that(bank.get('1'), is_not(none()))
			
		assert_that(bank.idOf('xx'), is_(none()))
		assert_that(bank.idOf('Lipoxygenase'), is_not(none()))
		assert_that(bank.idOf(u'Phospholipase'), is_(none()))
		assert_that(bank.idOf(u'Phospholipase A\u2082'), is_not(none()))
	
		assert_that(bank, externalizes(has_entries('Class', 'WordBank',
												   'unique', True,
												   'entries', has_length(3))))

