"""Setup script for the package."""

from setuptools import setup, find_packages
import os

# Read the contents of README.md
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

# Read the version from the package
about = {}
with open(os.path.join("src", "llm_chat", "__version__.py"), encoding="utf-8") as f:
    exec(f.read(), about)

# Define package dependencies based on project type
install_requires = []
# Streamlit project dependencies
install_requires.extend([
    "streamlit>=1.30.0",
    "pandas>=2.0.0",
    "numpy>=1.24.0",
])

setup(
    name="llm_chat",
    version=about["__version__"],
    description="A chat with LLM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Jesus Rosario",
    author_email="jar285@njit.edu",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 310",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
