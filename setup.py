from setuptools import setup, find_packages

setup(
  name = 'crowdrouter',
  packages = find_packages(exclude=['example', 'dist', 'build']),
  version = '1.5.4',
  description = 'A framework for architecting tasks to the crowd.',
  long_description = "The crowdrouter is a framework for architecting workflows and tasks to the crowd. Organize Tasks into WorkFlows, and use the CrowdRouter manager to route HTTP requests to those WorkFlows. Use Pipelining to create ordered sequences of Task, user-authentication to check requests at the route, workflow, or task level, and crowd-statistics to gather up task counts for Task executions.",
  license = "MIT",
  author = 'Mario Barrenechea',
  author_email = 'mbarrenecheajr@gmail.com',
  install_requires = ["pickledb", "simplejson"],
  url = 'https://github.com/Project-EPIC/crowdrouter', # use the URL to the github repo
  download_url = 'https://github.com/Project-EPIC/crowdrouter/archive/1.5.4.tar.gz',
  keywords = ['crowdsourcing', 'tasks', 'workflows'], # arbitrary keywords
  classifiers = [],
)
