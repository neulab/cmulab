from setuptools import setup, find_packages
import unittest
import codecs
import re
import os


# def test_suite():
#   test_loader = unittest.TestLoader()
#   test_suite = test_loader.discover("cmulab/tests", pattern="test_*.py")
# 
#   return test_suite


def find_version():
  """Find version in cmulab/__init__.py"""
  here = os.path.abspath(os.path.dirname(__file__))
  with codecs.open(os.path.join(here, "cmulab", "__init__.py"), 'r') as fp:
    version_file = fp.read()
    version_match = re.search(
      r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
  raise RuntimeError("Unable to find version string.")


setup(
  name="cmulab",
  version=find_version(),
  description="CMU Lingistic Annotation Backend",
  long_description=codecs.open("README.md", encoding="utf-8").read(),
  long_description_content_type="text/markdown",
  url="https://github.com/neulab/cmulab",
  author="Antonios Anastasopoulos and Graham Neubig",
  license="BSD 3-Clause",
  test_suite="setup.test_suite",
  classifiers=[
  "Intended Audience :: Developers",
  "Topic :: Text Processing",
  "Topic :: Scientific/Engineering :: Artificial Intelligence",
  "License :: OSI Approved :: BSD License",
  "Programming Language :: Python :: 3",
  ],
  packages=find_packages(),
  install_requires=[
    "django",
    "djangorestframework",
    "coreapi",
    "pyyaml",
    "django-filter",
    "markdown",
    "httpie"
  ],
  include_package_data=True,
)
