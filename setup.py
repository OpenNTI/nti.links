import codecs
from setuptools import setup, find_packages

VERSION = '0.0.0'

entry_points = {
}

TESTS_REQUIRE = [
	'nose',
	'nose-timer',
	'nose-pudb',
	'nose-progressive',
	'nose2[coverage_plugin]',
	'pyhamcrest',
	'nti.nose_traceback_info',
	'nti.testing'
]

setup(
	name = 'nti.links',
	version = VERSION,
	author = 'Jason Madden',
	author_email = 'jason@nextthought.com',
	description = "Support for links",
	long_description = codecs.open('README.rst', encoding='utf-8').read(),
	license = 'Proprietary',
	keywords = 'Links',
	classifiers = [
		'Intended Audience :: Developers',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: Implementation :: CPython',
		'Programming Language :: Python :: Implementation :: PyPy'
	],
	packages=find_packages('src'),
	package_dir={'': 'src'},
	namespace_packages=['nti'],
	tests_require=TESTS_REQUIRE,
	install_requires=[
		'setuptools',
		'six',
		'zope.component',
		'zope.interface',
		'zope.location',
		'zope.mimetype',
		'zope.security',
		'zope.traversing',
		'zope.schema',
		'nti.base',
		'nti.coremetadata',
		'nti.externalization',
		'nti.mimetype',
		'nti.ntiids',
		'nti.schema',
		'nti.traversal'
	],
	extras_require={
		'test': TESTS_REQUIRE,
	},
	entry_points=entry_points
)

