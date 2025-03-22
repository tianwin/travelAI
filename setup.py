from setuptools import setup, find_packages

with open("readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="travelai",
    version="0.1.0",
    author="TripAdvisor AI Team",
    author_email="ai@tripadvisor.com",
    description="AI-Powered Travel Planner",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tripadvisor/travelai",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Travel",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "travelai=app.main:main",
        ],
    },
    package_data={
        "app": ["config.yaml"],
    },
    include_package_data=True,
) 