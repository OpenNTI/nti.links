#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import is_not
from hamcrest import assert_that
from hamcrest import has_entries
does_not = is_not

import fudge

from zope import interface

from nti.base.interfaces import ICreated

from nti.externalization.externalization import to_external_object

from nti.links.links import Link

from nti.links.externalization import render_link
from nti.links.externalization import _root_for_ntiid_link

from nti.links.externalization import LinkExternalObjectDecorator

from nti.links.interfaces import ILinkExternalHrefOnly

from nti.links.tests import LinksTestCase


class TestExternalization(LinksTestCase):
    
    def test_link_external(self):
        href = "https://www.google.com"
        link = Link(href, rel='google', method='GET', elements=('mail',),
                    params=({'app':'42'}))
        result = to_external_object(link, name='second-pass')
        assert_that(result, 
                    has_entries('Class', 'Link',
                                'method', 'GET', 
                                'rel', 'google',
                                'href', 'https://www.google.com/mail?app=42'))

    @fudge.patch('nti.links.externalization.normal_resource_path')
    def test_root_for_ntiid_link(self, mock_rp):
        mock_rp.is_callable().with_args().returns('/dataserver2')
        link = Link("https://www.google.com")
        result = _root_for_ntiid_link(link)
        assert_that(result, is_('/dataserver2'))
        
        @interface.implementer(ICreated)
        class Bleach(object):
            creator = 'tite.kubo'
        bleach = Bleach()
        result = _root_for_ntiid_link(Link(bleach))
        assert_that(result, is_('/dataserver2'))

        link = Link("https://www.google.com")
        link.creator = 'alphabet'
        interface.alsoProvides(link, ICreated)
        result = _root_for_ntiid_link(link)
        assert_that(result, is_('/dataserver2'))
                     
    @fudge.patch('nti.links.externalization._root_for_ntiid_link')
    def test_render_link_one(self, mock_root):
        mock_root.is_callable().with_args().returns('/dataserver2')
        class Bleach(object):
            mimeType = 'application/vnd.nextthought.bleach'
            ntiid = 'tag:nextthought.com,2011-10:BLEACH-NTIVideo-Ichigo.vs.Aizen'
        
        target = Bleach()
        link = Link(target, rel='bleach', method='GET',
                    title='Ichigo.vs.Aizen')
        result = render_link(link)
        assert_that(result, 
                    has_entries('Class', 'Link',
                                'method', 'GET', 
                                'rel', 'bleach', 
                                'title', 'Ichigo.vs.Aizen',
                                'ntiid', 'tag:nextthought.com,2011-10:BLEACH-NTIVideo-Ichigo.vs.Aizen',
                                'href', '/dataserver2/NTIIDs/tag%3Anextthought.com%2C2011-10%3ABLEACH-NTIVideo-Ichigo.vs.Aizen'))

        interface.alsoProvides(link, ILinkExternalHrefOnly)
        result = render_link(link)
        assert_that(result, 
                    is_('/dataserver2/NTIIDs/tag%3Anextthought.com%2C2011-10%3ABLEACH-NTIVideo-Ichigo.vs.Aizen'))

    @fudge.patch('nti.links.externalization.normal_resource_path')
    def test_render_link_two(self, mock_rp):
        mock_rp.is_callable().with_args().returns('https://bleach.org/ichigo.gif')
        class Bleach(object):
            pass
        
        target = Bleach()
        link = Link(target, rel='ichigo', target_mime_type='image/gif')
        result = render_link(link)
        assert_that(result, 
                    has_entries('Class', 'Link',
                                'rel', 'ichigo', 
                                'href', 'https://bleach.org/ichigo.gif'))

    @fudge.patch('nti.links.externalization.normal_resource_path')
    def test_render_link_three(self, mock_rp):
        mock_rp.is_callable().with_args().returns('https://bleach.org')
        link = Link('tag:nextthought.com,2011-10:BLEACH-OID-Ichigo.vs.Aizen', 
                    rel='bleach', method='GET',
                    title='Ichigo.vs.Aizen')
        interface.alsoProvides(link, ILinkExternalHrefOnly)
        result = render_link(link)
        assert_that(result, 
                    is_('https://bleach.org/Objects/tag%3Anextthought.com%2C2011-10%3ABLEACH-OID-Ichigo.vs.Aizen'))
        
    def test_decorator(self):
        link = Link("https://www.google.com", rel='google', method='GET',
                    elements=('mail',),
                    ignore_properties_of_target=True)
        decorator = LinkExternalObjectDecorator()
        decorator.decorateExternalObject(None, [link])
        decorator.decorateExternalObject(None, {'Links':[link, 'https://www.amazon.com']})
