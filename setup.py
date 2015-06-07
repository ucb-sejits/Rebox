__author__ = 'nzhang-dev'
from distutils.core import setup

setup(
    name='Rebox',
    version='0.1.0',
    url='github.com/pyprogrammer/Rebox',
    license='B',
    author='Nathan Zhang',
    author_email='nzhang32@eecs.berkeley.edu',
    description='Dynamic stencil reindexing in Python',

    packages=[
        'Rebox.specializers.rm',
        'Rebox.specializers.z',
        'Rebox.specializers.generic',
        'Rebox.stencils',
        'Rebox',
    ],

    install_requires=[
        'ctree'
    ]
)
