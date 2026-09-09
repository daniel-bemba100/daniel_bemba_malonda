from setuptools import setup, find_packages

setup(
    name="upc-notepad",
    version="2.0.0",
    author="Daniel Bemba Malonda",
    description="A professional text editor built with PyQt6.",
    packages=find_packages(),
    install_requires=[
        "PyQt6>=6.6.0",
        "gTTS>=2.5.0",
        "pyttsx3>=2.90",
        "edge-tts>=7.0.0",
    ],
    entry_points={
        "console_scripts": [
            "upc-notepad=src.app:main",
        ],
    },
    include_package_data=True,
    python_requires=">=3.8",
)
