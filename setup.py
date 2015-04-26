from distutils.core import setup
from Cython.Build import cythonize

setup(name='Skyscreen',
      version='0.1',
      description='Skyscreen library',
      author='Richard Weiss',
      author_email='richardweiss@richardweiss.org',
      url='https://www.python.org/sigs/distutils-sig/',
      packages=[
            'skyscreen_tools',
            'skyscreen_core',
            'screens'],
      ext_modules=cythonize("skyscreen_tools/flatspace_tools.pyx")
)
