#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import equal_to
from hamcrest import not_none
from hamcrest import assert_that
from hamcrest import starts_with
from hamcrest import greater_than
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
        link = Link(href, rel='google', method='GET', elements=('mail.txt',),
                    params={'app':'42'}, target_mime_type='text/plain',
                    title=u'Google', ignore_properties_of_target=True)
        assert_that(link, validly_provides(ILink))
        assert_that(link, verifiably_provides(ILink))

        assert_that(repr(link),
                    starts_with("<Link rel='google'"))

        assert_that(hash(link), is_(not_none()))
        
        link2 = Link(href, rel='google', method='GET', elements=('mail',))
        assert_that(link, is_not(equal_to(link2)))
        
        link3 = Link("https://www.amazon.com", rel='amazon', method='GET')
        assert_that(sorted({link, link3}),
                    is_([link3, link]))
        
        assert_that(link, greater_than(link3))
        assert_that(hash(Link(object(), rel='foo')), is_(not_none()))
        
        assert_that(link, is_not(equal_to(none())))
        
        obj = object()
        for func in (Link.__gt__, Link.__lt__):
            assert_that(func(link, obj), is_(NotImplemented))
        
    def test_pickle(self):
        href = "https://www.google.com"
        link = Link(href, rel='google', method='GET')
        with self.assertRaises(TypeError):
            pickle.dumps(link)
        with self.assertRaises(TypeError):
            link.__reduce__()
