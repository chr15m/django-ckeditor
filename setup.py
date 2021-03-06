from setuptools import setup, find_packages

setup(
    name='django-ckeditor',
    version='0.0.5',
    description='Django admin CKEditor integration.',
    long_description = open('README.rst', 'r').read(),
    author='Shaun Sephton',
    author_email='shaunsephton@gmail.com',
    url='http://github.com/shaunsephton/django-ckeditor',
    packages = find_packages(),
    dependency_links = [
        'http://dist.plone.org/thirdparty/',
    ],
    install_requires = [
        'PIL',
    ],
    include_package_data=True,
    classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    zip_safe=False,
)
