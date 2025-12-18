from setuptools import setup, find_packages

with open("timer-app-requirements.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="multi-timer-app",
    version="1.0.0",
    author="Your Name",
    description="A system tray application for Ubuntu that manages multiple named timers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "PyGObject>=3.40.0",
        "notify2>=0.3.1",
        "playsound>=1.3.0",
        "dbus-python>=1.2.18",
    ],
    package_data={
        "timer_app": [
            "../resources/icons/*.png",
            "../resources/sounds/*.ogg",
        ],
    },
    entry_points={
        "console_scripts": [
            "multi-timer=timer_app.main:main",
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: POSIX :: Linux",
    ],
)
