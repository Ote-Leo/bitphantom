import setuptools

with open("README.rst", "r", encoding="utf8") as fh:
	long_description = fh.read()

from pyrent import __version__, __description__

setuptools.setup(
	name="pyrent",
	author="Ote Leo",
	author_email="ote.leo73@gmail.com",
	version=__version__,
	description=__description__,
	long_description=long_description,
	long_description_content_type="text/x-rst",
	packages=["pyrent"],
	python_requires=">=3.10",
	include_package_data=True,
	install_requires=[],
	extras_require={},
)
