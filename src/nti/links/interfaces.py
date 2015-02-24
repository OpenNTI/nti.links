#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from zope.mimetype.interfaces import mimeTypeConstraint

from zope.schema import Iterable

from nti.schema.field import ValidTextLine
from nti.schema.field import ValidChoice as Choice
from nti.schema.field import DecodingValidTextLine

class ILink(interface.Interface):
    """
    A relationship between the containing entity and
    some other entity.
    """

    rel = Choice(
        title=u'The type of relationship',
        values=('related', 'alternate', 'self', 'enclosure', 'edit', 'like',
                'unlike', 'content'))

    target = interface.Attribute(
        """
        The target of the relationship.

        May be an actual object of some type or may be a string. If a string,
        will be interpreted as an absolute or relative URI.
        """)

    elements = Iterable(
        title="Additional path segments to put after the `target`",
        description="""Each element must be a string and will be a new URL segment.

        This is useful for things like view names or namespace traversals.""")

    target_mime_type = DecodingValidTextLine(
        title='Target Mime Type',
        description="The mime type explicitly specified for the target object, if any",
        constraint=mimeTypeConstraint,
        required=False)

    method = DecodingValidTextLine(
        title='HTTP Method',
        description="The HTTP method most suited for this link relation",
        required=False)

    title = ValidTextLine(
        title="Human readable title",
        required=False)

class ILinkExternalHrefOnly(ILink):
    """
    A marker interface intended to be used when a link
    object should be externalized as its 'href' value only and
    not the wrapping object.
    """

class ILinked(interface.Interface):
    """
    Something that possess links to other objects.
    """
    links = Iterable(
        title=u'Iterator over the ILinks this object contains.')
