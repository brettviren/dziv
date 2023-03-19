import setuptools

setuptools.setup(
    name="dziv",
    version='0.0.0',
    author="Brett Viren",
    author_email="brett.viren@gmail.com",
    description="Deep zoom image views",
    url="https://brettviren.github.io/dziv",
    packages=setuptools.find_packages(),
    python_requires='>=3.5',
    install_requires=[
        "click",
        "pytest",
        "scipy",
        "pillow",
        "flask",
    ],
    entry_points = {
        'console_scripts': [
            'dziv = dziv.__main__:main',
        ],
    ),
)
