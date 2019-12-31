'''
Entry points enables you to call the program from
command prompt simply as summarize2, from any directory.

If installing as a developer using "pip install -e ."
don't delete exhibit.egg-info folder.
'''


from setuptools import setup, find_packages

setup(name='summarize2',
      version='0.1',
      description='Command line tool for comparing datasets',
      author='German Priks',
      python_requires=">3.6",
      install_requires=[
        "pandas",
        "numpy",
        "scipy",
        "PyYAML",
        "matplotlib",
        "jinja2",
        "bokeh==1.4.0"
      ],
      packages=find_packages(),
      entry_points={
        'console_scripts': [
            'summarize2 = summarize2.command.bootstrap:main'
        ]}
     )
