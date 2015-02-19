from setuptools import setup


setup(name='SpecView',
      version='0.1',
      description='Interactive spectral analysis suite.',
      url='https://github.com/spacetelescope/specview',
      author='Harry Ferguson',
      author_email='ferguson@stsci.edu',
      license='AURA',
      packages=['specview'],
      zip_safe=False,
      install_requires=['numpy>=1.9.1',
                        'scipy>=0.15',
                        'astropy>=1.0'])