from setuptools import setup

setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='PhotoBooth',
    url='https://github.com/vk02169/PhotoBooth',
    author='Vinayak Kumar',
    author_email='vinayak.v.kumar@gmail.com',
    # Needed to actually package something
    packages=['camcore'],

    # Needed for dependencies
    install_requires=['',''],

    # *strongly* suggested for sharing
    version='1.0',
    # The license can be anything you like
    license='None',
    description='An example of a python package from pre-existing code',
    # We will also need a readme eventually (there will be a warning)
    # long_description=open('README.txt').read(),
)