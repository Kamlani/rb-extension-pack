from setuptools import setup, find_packages

PACKAGE="RB-XMLExport"
VERSION="0.1"

setup(
    name=PACKAGE,
    version=VERSION,
    description="""XML Export of Review Files""",
    author="Kahlil Amlani",
    packages=["rbxmlexport"],
    entry_points={
        'reviewboard.extensions':
        '%s = rbxmlexport.extension:RBXMLExport' % PACKAGE,
    },
    package_data={
        'rbxmlexport': [
            'htdocs/css/*.css',
            'htdocs/js/*.js',
            'templates/rbxmlexport/*.html',
            'templates/rbxmlexport/*.txt',
        ],
    }
)
