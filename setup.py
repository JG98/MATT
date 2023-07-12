import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("matt/version.txt", "r") as vf:
    version = vf.read()

setuptools.setup(
    name="phylo-matt",
    version=version,
    author="Jeff Raffael Gower",
    author_email="jeffgower98@gmail.com",
    description="A Framework For Modifying And Testing Topologies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BIONF/MATT",
    packages=setuptools.find_packages(),
    package_data={'': ['*']},
    include_package_data=True,
    install_requires=["flask>=2.0.0"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': ["matt = matt.app:main"]
    }
)
