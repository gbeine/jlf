from setuptools import setup

setup(
    name = "JIRA lean forward",
    version = "0.1.1dev",
    description = "Get Lean Stats like throughput and cycle time out of jira with ease",
    author = "Chris Young",
    licence = "BSD",
    author_email = "chris@chrisyoung.org",
    platforms = ["Any"],
    packages = ['jira_stats'],
    include_package_data = True,
    install_requires=[
        'numpy',
        'pandas',
        'requests',
        'jira-python',
	'mockito',
        'xlwt',
        'argparse'
    ]
)
