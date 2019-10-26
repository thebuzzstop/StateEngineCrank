import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='StateEngineCrank',
    version='0.1',
    packages=setuptools.find_packages(),
    package_dir={'': ''},
    url='https://github.com/thebuzzstop/StateEngineCrank',
    license='GNU General Public License v3',
    author='Mark Sawyer',
    author_email='mbs@mysawyer.net',
    description='Basic StateEngineCrank utility with a suite of demonstrations',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: GPL :: v3",
        "Operating System :: OS Independent",
    ],
)
