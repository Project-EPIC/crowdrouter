from distutils.core import setup
setup(
  name = 'crowdrouter',
  packages = ['crowdrouter', 'crowdrouter/task', 'crowdrouter/workflow'], # this must be the same as the name above
  version = '0.5',
  description = 'A framework for architecting tasks to the crowd.',
  author = 'Mario Barrenechea',
  author_email = 'mbarrenecheajr@gmail.com',
  url = 'https://github.com/Project-EPIC/crowdrouter', # use the URL to the github repo
  download_url = 'https://github.com/Project-EPIC/crowdrouter/archive/0.5.tar.gz',
  keywords = ['crowdsourcing', 'tasks', 'workflows'], # arbitrary keywords
  classifiers = [],
)
