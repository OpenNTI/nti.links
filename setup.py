import codecs
from setuptools import setup, find_packages

VERSION = '0.0.0'

entry_points = {
	"z3c.autoinclude.plugin": [
		'target = nti.contentrendering',
	],
}

TESTS_REQUIRE = [
	'nose',
	'nose-timer',
	'nose-pudb',
	'nose-progressive',
	'nose2[coverage_plugin]',
	'pyhamcrest',
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
	keywords = 'pyramid preference',
	classifiers = [
		'Intended Audience :: Developers',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.7'
		'Programming Language :: Python :: Implementation :: CPython'
	],
	packages=find_packages('src'),
	package_dir={'': 'src'},
	namespace_packages=['nti',],
	tests_require=TESTS_REQUIRE,
	install_requires=[
		'setuptools',
		'six',
		'zope.component',
		'zope.interface',
		'zope.location',
		'zope.traversing',
		'zope.mimetype',
		'zope.schema',
		'nti.externalization',
		'nti.nose_traceback_info',
	],
	extras_require={
		'test': TESTS_REQUIRE,
	},
	dependency_links=[
		'git+https://github.com/NextThought/nti.schema.git#egg=nti.schema',
		'git+https://github.com/NextThought/nti.nose_traceback_info.git#egg=nti.nose_traceback_info'
	],
	entry_points=entry_points
)
