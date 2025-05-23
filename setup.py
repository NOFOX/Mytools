from setuptools import setup, find_packages

setup(
    name="mytools",
    version="0.1.0",
    description="A collection of useful tools with Gradio interfaces",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/mytools",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "gradio>=4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "mytools=tools.run_tool:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
)