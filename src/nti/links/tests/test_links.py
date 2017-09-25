#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_not
from hamcrest import assert_that
does_not = is_not

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
        with self.assertRaises(TypeError):
            pickle.dumps(link)