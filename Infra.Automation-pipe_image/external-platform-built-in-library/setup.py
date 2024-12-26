import setuptools


setuptools.setup(
    name="external-platform-library-builtIn",
    version="0.0.1",
    author="ta_team",
    description="BuiltIn External Library source package",
    long_description_content_type="text/markdown",
    url="https://git.qubership.org/PROD.Platform.HA/Infra.Automation/external-platform-built-in-library",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
