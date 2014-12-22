# Install setuptools automagically from the interwebz
from ez_setup import use_setuptools
use_setuptools()

from glob import glob
import sys
from os.path import join, expanduser

from setuptools import setup, find_packages
import setuptools
from setuptools.command.bdist_egg import bdist_egg as _bdist_egg
from setuptools.command.develop import develop as _develop
from setuptools.command.install import install as _install

from version import __version__

class InstallSystemPackagesCommand(setuptools.Command):
    '''
    Custom setup.py install keyword to initiate system-package installation
    '''
    user_options = []
    description = 'Installs all system packages via the package manager(Requires super-user)'

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from miseqpipeline.dependency import (
            install_system_packages,
            get_distribution_package_list,
            UserNotRootError
        )
        try:
            system_packages = get_distribution_package_list('system_packages.lst')
            install_system_packages(system_packages)
        except UserNotRootError as e:
            print "You need to be root to install system packages"

class InstallPythonCommand(setuptools.Command):
    '''
    Wrapper around installing python into HOME prefix
    '''
    description = 'Allows the user to easily install python into a prefix'
    user_options = [
        ('prefix=', None, 'Where to install python to. Default is $HOME'),
        ('version=', None, 'What version to install. Default is 2.7.8')
    ]

    def initialize_options(self):
        self.prefix = expanduser('~/')
        self.version = '2.7.8'

    def finalize_options(self):
        pass

    def run(self):
        from miseqpipeline.dependency import install_python
        install_python( self.prefix, self.version )

class PipelineInstallCommand(_install):
    '''
    Custom install command which should install everything needed
    '''
    #user_options = []
    description = 'Installs the pipeline'

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # Because setuptools is so terrible at handling this
        self.pip_install( 'requirements.txt' )
        # Install dependencies outside of python
        # May require that setup_requires has been processed
        # so has to come after _bdist_egg.run
        print "Installing ext deps"
        self._install_external_dependencies()

    def pip_install( self, reqfile ):
        ''' Just run pip install pkg '''
        from subprocess import check_call, PIPE
        check_call( ['pip', 'install', '-r', reqfile] )

    def _install_external_dependencies(self):
        # URLs for dependencies
        bwa_url = 'https://github.com/lh3/bwa'
        samtools_url = 'https://github.com/samtools/samtools'
        trimmomatic_url = 'http://www.usadellab.org/cms/uploads/supplementary/Trimmomatic/Trimmomatic-0.32.zip'

        # Install samtools and bwa
        from miseqpipeline.dependency import (
                install_samtools,
                install_bwa,
                install_trimmomatic
        )

        # Prefix path for installation
        prefix = sys.prefix
        bindir = join(prefix,'bin')
        libdir = join(prefix,'lib')

        # Install all dependencies outside fo pypi
        install_bwa(bwa_url, '0.7.6a', prefix)
        install_samtools(samtools_url, 'ccf1da91b29b75764402e20f46ec21fc293fe5f5', prefix)
        install_trimmomatic(trimmomatic_url, libdir)

class bdist_egg(_bdist_egg):
    def run(self):
        self.run_command('install_pipeline')
        _bdist_egg.run(self)

class develop(_develop):
    def run(self):
        install_pipeline = self.distribution.get_command_obj('install_pipeline')
        install_pipeline.develop = True
        self.run_command('install_pipeline')
        _develop.run(self)

# Run setuptools setup
setup(
    name = "miseqpipeline",
    version = __version__,
    packages = find_packages(),
    scripts = glob('bin/*'),
    entry_points = {
        'console_scripts': [
            'sample_coverage = miseqpipeline.coverage:main',
            'make_example_config = miseqpipeline.config:main',
        ]
    },
    setup_requires = [
        'nose',
        'tempdir'
    ],
    tests_require = [
        'nose',
        'mock',
    ],
    package_data = {
        'miseqpipeline': ['config.yaml'],
    },
    author = 'Tyghe Vallard',
    author_email = 'vallardt@gmail.com',
    description = 'Pipeline that combines sff and fastq files from multiple platforms',
    license = '',
    keywords = 'miseq iontorrent roche 454 fastq vcf',
    url = 'https://github.com/VDBWRAIR/miseqpipeline',
    cmdclass = {
        'install_system_packages': InstallSystemPackagesCommand,
        'install_pipeline': PipelineInstallCommand,
        'install_python': InstallPythonCommand,
        'bdist_egg': bdist_egg,
        'develop': develop,
    },
)
