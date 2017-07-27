from setuptools import setup, find_packages
import sys, os

version = '0.2.1'

setup(
	name='ckanext-nsw',
	version=version,
	description="",
	long_description="""\
	""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	author='',
	author_email='',
	url='',
	license='',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	namespace_packages=['ckanext', 'ckanext.nsw'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
	],
	entry_points=\
	"""
        [ckan.plugins]
	# Add plugins here, eg
	nsw=ckanext.nsw.plugin:NSWPlugin
        [paste.paster_command]
        nsw=ckanext.nsw.command:NSWCommand
	""",
)
