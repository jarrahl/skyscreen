from setuptools import setup
from Cython.Build import cythonize
import numpy

setup(name='Skyscreen',
      version='0.1',
      description='Skyscreen library',
      author='Richard Weiss',
      author_email='richardweiss@richardweiss.org',
      url='https://www.python.org/sigs/distutils-sig/',
      packages=[
            'skyscreen_tools',
            'skyscreen_core',
            'pyrendering',
            'patterns'
      ],
      setup_requires=[
            'cython',
            'numpy',
            'pyserial'
      ],
      install_requires=[
            'numpy',
            'scipy',
            'sphinx',
            'sphinx-autobuild',
            'theano',
            #'Cython==0.21.2',
            'nose',
            'noise',
            'pyzmq',
            'plumbum',
            'scales',
            'pyyaml',
            'msgpack-python',
            'pyserial'
      ],
      include_dirs=[
            numpy.get_include()
      ],
      ext_modules=cythonize([
            "pyrendering/fast_tools.pyx",
            "skyscreen_tools/flatspace_tools.pyx"
      ])
      )
