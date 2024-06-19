from setuptools import setup, find_packages
import yaml

version_config = yaml.safe_load(open('almo_cli/version.yaml'))
almo_cli_version = version_config['almo-cli']
almo_version = version_config['almo']

print(
    f"ALMO CLI version: {almo_cli_version}\n"
    f"ALMO version: {almo_version}"


)

setup(
    name='almo-cli',
    version=almo_cli_version,
    packages=find_packages(),
    install_requires=[
        'PyYAML',
        'argparse',
        'almo',
        'livereload'
    ],
    entry_points={
        'console_scripts': [
            'almo-cli=almo_cli.almo_cli:main [cli]',
        ],
    },
)