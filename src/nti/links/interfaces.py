#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=inherit-non-class

from zope import interface

from zope.mimetype.interfaces import mimeTypeConstraint

from zope.schema import Iterable

from nti.schema.field import ValidTextLine
from nti.schema.field import DecodingValidTextLine
from nti.schema.field import Int


class ILink(interface.Interface):
    """
    A relationship between the containing entity and
    some other entity.
    """

    rel = DecodingValidTextLine(title=u"The type of relationship",
                                required=True)

    target = interface.Attribute(
        """
        The target of the relationship.

        May be an actual object of some type or may be a string. If a string,
        will be interpreted as an absolute or relative URI.
        """)

    elements = Iterable(title=u"Additional path segments to put after the `target`",
                        description=u"Each element must be a string and will be a new URL segment. "
                        u"This is useful for things like view names or namespace traversals.")

    target_mime_type = DecodingValidTextLine(
        title=u'Target Mime Type',
        description=u"The mime type explicitly specified for the target object, if any",
        constraint=mimeTypeConstraint,
        required=False)

    method = DecodingValidTextLine(
        title=u'HTTP Method',
        description=u"The HTTP method most suited for this link relation",
        required=False)

    title = ValidTextLine(title=u"Human readable title",
                          required=False)


class IFramedLink(ILink):
    """
    A link that is intended to be launched into an iframed destination
    """

    height = Int(title=u'The height of the iframe.',
                 required=True)

    width = Int(title=u'The width of the iframe.',
                required=True)


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
    links = Iterable(title=u'Iterator over the ILinks this object contains.')
