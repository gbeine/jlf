from setuptools import setup
from setuptools.command.build_ext import build_ext as _build_ext


class build_ext(_build_ext):
    # Taken from http://stackoverflow.com/a/21621689/1064619
    def finalize_options(self):
        _build_ext.finalize_options(self)
        # Prevent numpy from thinking it is still in its setup process:
        __builtins__.__NUMPY_SETUP__ = False
        import numpy
        self.include_dirs.append(numpy.get_include())

setup(
    name="Just lean forward",
    version="0.2.0",
    description="Get Lean Stats like throughput and cycle time out of Jira/FogBugz with ease",
    author="Chris Young",
    license="LICENSE.md",
    author_email="chris@chrisyoung.org,mail@gerritbeine.com",
    platforms=["Any"],
    packages=['jlf_stats'],
    include_package_data=True,
    scripts=['bin/jlf'],
    setup_requires=['numpy'],
    install_requires=[
        'BeautifulSoup4',
        'nose',
        'mock',
        'argparse',
        'ipython',
        'jira',
        'openpyxl',
        'pandas',
        'python-dateutil',
        'pytz',
        'xlrd',
        'xlwt',
        'XlsxWriter'
    ]
)
