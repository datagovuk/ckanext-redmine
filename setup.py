from setuptools import setup, find_packages
import sys, os

version = '1.0'

setup(
	name='ckanext-redmine',
	version=version,
	description="CKAN integration with Redmine for recording quality issues.",
	long_description="""\
	""",
	classifiers=[],
	keywords='',
	author='Ross Jones',
	author_email='ross@servercode.co.uk',
	url='https://github.com/datagovuk/ckanext-redmine',
	license='',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	namespace_packages=['ckanext', 'ckanext.redmine'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		"requests>=1.1.0"
	],
	entry_points=\
	"""
        [ckan.plugins]
		redmine=ckanext.redmine.plugin:RedminePlugin
	""",
)
