#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_not
from hamcrest import assert_that
does_not = is_not

from nose.tools import assert_raises

import pickle

from nti.testing.matchers import validly_provides
from nti.testing.matchers import verifiably_provides

import unittest

from nti.links.interfaces import ILink

from nti.links.links import Link


class TestLinks(unittest.TestCase):

    def test_model(self):
        href = "https://www.google.com"
        link = Link(href, rel='google', method='GET', elements=('mail',))
        assert_that(link, validly_provides(ILink))
        assert_that(link, verifiably_provides(ILink))
        
    def test_picle(self):
        href = "https://www.google.com"
        link = Link(href, rel='google', method='GET')
        with assert_raises(TypeError):
            pickle.dumps(link)
