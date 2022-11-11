from setuptools import setup

setup(name='pyshamir',
      version='0.1',
      description="Python port of HashiCorp Vault's Shamir key Split and Combine methods.",
      long_description=open('README.md').read(),
      url='https://github.com/konidev20/pyshamir',
      author='Srigovind Nayak',
      author_email='sgovind.dev@outlook.com',
      license='LICENSE',
      packages=['pyshamir'],
      zip_safe=False)