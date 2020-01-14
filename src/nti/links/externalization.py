#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import collections
from six import string_types
from six.moves import urllib_parse

from zope import component
from zope import interface

from zope.location.interfaces import LocationError

from zope.traversing.interfaces import TraversalError

from nti.base.interfaces import ICreated

# See comment in render_link for an explanation of the handling of
# IShouldHaveTraversablePath and the monkeying around that is happening here.
try:
    from nti.coremetadata.interfaces import IShouldHaveTraversablePath
except ImportError:
    IShouldHaveTraversablePath = interface.Interface
else:
    from nti.coremetadata.interfaces import IDataserver

from nti.externalization.interfaces import StandardExternalFields
from nti.externalization.interfaces import ILocatedExternalMapping
from nti.externalization.interfaces import IExternalObjectDecorator
from nti.externalization.interfaces import IInternalObjectExternalizer

from nti.externalization.singleton import Singleton

from nti.links.interfaces import ILink
from nti.links.interfaces import ILinkExternalHrefOnly

from nti.mimetype.mimetype import nti_mimetype_from_object

from nti.ntiids.ntiids import TYPE_OID
from nti.ntiids.ntiids import is_ntiid_of_type
from nti.ntiids.ntiids import is_valid_ntiid_string

from nti.traversal.traversal import normal_resource_path
from nti.traversal.traversal import is_valid_resource_path

logger = __import__('logging').getLogger(__name__)


def _root_for_ntiid_link(link, nearest_site=None):
    # Place the NTIID reference under the most specific place possible: the owner,
    # if in belongs to someone, otherwise the global Site
    root = None
    target = link.target
    if ICreated.providedBy(target) and target.creator:
        try:
            root = normal_resource_path(target.creator)
        except TypeError:  # pragma: no cover
            pass
    if root is None and ICreated.providedBy(link) and link.creator:
        try:
            root = normal_resource_path(link.creator)
        except TypeError:
            pass

    if root is None:
        root = normal_resource_path(nearest_site)

    return root


def render_link(link, nearest_site=None):
    """
    :param link: The link to render. Optionally, the link may be
            :class:`loc_interfaces.ILocation` if we need to find a site. The target
            of the link can be a string, in which case it should be a complete path or an
            NTIID, or it can be an object with a complete lineage. If the target is an NTIID
            string, we will try to find the creating user of the link (or its target) to
            provide a more localized representation; the link or its target has to implement
            :class:`nti_interfaces.ICreated` for this to work or we will use the nearest
            site (probably the root).
    :param nearest_site: Currently unused.
    :type link: :class:`nti_interfaces.ILink`
    """
    # pylint: disable=unused-variable
    __traceback_info__ = link, nearest_site

    target = link.target
    assert target is not None
    rel = link.rel
    content_type = link.target_mime_type
    content_type_derived_from_target = False
    if not content_type:
        content_type = nti_mimetype_from_object(target)
        content_type_derived_from_target = True

    href = None
    ntiid = getattr(target, 'ntiid', None) \
         or getattr(target, 'NTIID', None)
    if ntiid:
        ntiid_derived_from_target = True
    elif isinstance(target, string_types) and is_valid_ntiid_string(target):
        ntiid = target
        ntiid_derived_from_target = False  # it *is* the target

    if ntiid and not IShouldHaveTraversablePath.providedBy(target):
        # Although (enclosures and entities and other things with IShouldHaveTraversablePath)
        # have an NTIID, we want to avoid using it
        # if possible because it has a much nicer pretty url.
        href = ntiid
        # We're using ntiid as a backdoor for arbitrary strings.
        # But if it really is an NTIID, then direct it specially if
        # we can.
        # Hardcoded paths.
        # Somewhere in the site there should be an object that represents each of these,
        # and we should be able to find it, get a traversal path for it, and use it here.
        # That object should implement the lookup behaviour found currently in
        # ntiids.
        #
        # 1/2020 This is a legacy code path, in general objects should be traversable and
        # be referenced by their normal resource path. In some systems many objects had no
        # traversable paths and instead we generated ntiid based links for those objects.
        # This legacy behaviour is activated by the installation of the `legacy` extras, specifically
        # the inclusion of IShouldHaveTraversablePath from nti.coremetadata.
        # https://github.com/NextThought/nti.links/issues/2
        if is_valid_ntiid_string(ntiid):
            # In the past, if the link was not ICreated, the root would become
            # the nearest site. But not all site objects support the Objects and
            # NTIIDs traversal. So the simplest thing to do is to use the root
            # site
            # This may not be quite correct for NTIIDs in the future?
            # It should always be correct for OIDs though.
            try:
                ds_root = component.getUtility(IDataserver).root
            except (LookupError, NameError):
                msg = "No dataserver found, you must have provided a site. Only in test cases"
                logger.warn(msg)
                ds_root = nearest_site
            root = _root_for_ntiid_link(link, ds_root)

            if is_ntiid_of_type(ntiid, TYPE_OID):
                href = root + '/Objects/' + urllib_parse.quote(ntiid)
            else:
                href = root + '/NTIIDs/' + urllib_parse.quote(ntiid)

    elif is_valid_resource_path(target):
        href = target
    else:
        # This will raise a LocationError or TypeError if something is broken
        # in the chain. That shouldn't happen and needs to be dealt with
        # at dev time.
        # next fun puts target in __traceback_info__
        __traceback_info__ = rel, link.elements
        href = normal_resource_path(target)

    assert href

    # Join any additional path segments that were requested
    if link.elements:
        href = href + ('/' if not href.endswith('/') else '')
        href += '/'.join(link.elements)
    if link.params:
        href = href + '?%s' % urllib_parse.urlencode(link.params)

    result = component.getMultiAdapter((), ILocatedExternalMapping)
    result.update({StandardExternalFields.CLASS: 'Link',
                   StandardExternalFields.HREF: href,
                   'rel': rel})
    if content_type:
        # If a method was provided, do not try to infer from the target object,
        # must be explicit
        if link.method and link.target_mime_type:
            result['type'] = content_type
        elif not link.method:
            if      not link.ignore_properties_of_target \
                and not content_type_derived_from_target:
                result['type'] = content_type

    if is_valid_ntiid_string(ntiid):
        if not link.ignore_properties_of_target or not ntiid_derived_from_target:
            result['ntiid'] = ntiid

    if link.method:
        result['method'] = link.method

    if link.title:
        result['title'] = link.title

    if      not is_valid_resource_path(href) \
        and not is_valid_ntiid_string(href):  # pragma: no cover
        # This shouldn't be possible anymore.
        __traceback_info__ = href, link, target, nearest_site
        raise TraversalError(href)

    if ILinkExternalHrefOnly_providedBy(link):
        # The marker that identifies the link should be replaced by just the href
        # Because of the decorator, it's easiest to just do this here
        result = result['href']

    return result


@component.adapter(ILink)
@interface.implementer(IInternalObjectExternalizer)
class LinkExternal(object):
    """
    See :func:`render_link`
    """

    def __init__(self, context):
        self.context = context

    def toExternalObject(self, **unused_kwargs):
        return render_link(self.context)


_MutableMapping = collections.MutableMapping
_MutableSequence = collections.MutableSequence

ILink_providedBy = ILink.providedBy
ILinkExternalHrefOnly_providedBy = ILinkExternalHrefOnly.providedBy

LINKS = StandardExternalFields.LINKS


@component.adapter(object)
@interface.implementer(IExternalObjectDecorator)
class LinkExternalObjectDecorator(Singleton):
    """
    An object decorator which (comes after the mapping decorators)
    to clean up any links that are added by decorators that didn't get rendered.
    """

    def decorateExternalObject(self, unused_context, obj):
        if isinstance(obj, _MutableSequence):
            for i, x in enumerate(obj):
                if ILink_providedBy(x):
                    obj[i] = render_link(x)
        elif isinstance(obj, _MutableMapping) and obj.get(LINKS, ()):
            links = []
            for link in obj[LINKS]:
                # pylint: disable=unused-variable
                __traceback_info__ = link
                try:
                    if ILink_providedBy(link):
                        rendered = render_link(link)
                    else:
                        rendered = link
                    links.append(rendered)
                except (TypeError, LocationError):
                    logger.error("Error rendering link %s", link)
            obj[LINKS] = links
