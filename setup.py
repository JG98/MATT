import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bio-matt-preview",
    version="0.2.3",
    author="Jeff Raffael Gower",
    author_email="jeffgower98@gmail.com",
    description="A Framework for Modifying And Testing Topologies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JG98/MATT",
    packages=setuptools.find_packages(),
    package_data={'': ['*']},
    include_package_data=True,
    install_requires=["flask"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
    entry_points={
        'console_scripts': ["matt = matt.app:main"]
    }
)
