from setuptools import setup, find_packages

setup(
  name = 'crowdrouter',
  packages = find_packages(exclude=['example', 'dist', 'build']),
  version = '1.1',
  description = 'A framework for architecting tasks to the crowd.',
  license = "MIT",
  author = 'Mario Barrenechea',
  author_email = 'mbarrenecheajr@gmail.com',
  url = 'https://github.com/Project-EPIC/crowdrouter', # use the URL to the github repo
  download_url = 'https://github.com/Project-EPIC/crowdrouter/archive/1.1.tar.gz',
  keywords = ['crowdsourcing', 'tasks', 'workflows'], # arbitrary keywords
  classifiers = [],
)
