from setuptools import setup, find_packages

# Define your package metadata here
setup(
    name='dcc-wrapper-genai',
    version='0.0.1',
    description='A toy tool for wrapping genAI tools to make them function more like iterable digital content creation tools.',
    author='Bhautik Joshi',
    author_email='bjoshi@gmail.com',
    #url='https://github.com/yourusername/my_project',  # Optional: Repository URL
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        # List your project dependencies here
        # For example:
        # 'numpy>=1.20.0',
        # 'pandas>=1.3.0'
    ],
    entry_points={
        'console_scripts': [
            'dcc-wrapper-genai=main:main',  # Example entry point to run src/main.py
