from argparse import ArgumentParser
import logging
from pathlib import Path
import pyups.backups as backups
from pyups.configuration import get_configuration

logging.config.fileConfig('logging.ini')

parser = ArgumentParser(prog="pyups", description="Back up a directory into an Amazon S3 bucket")
parser.add_argument("directory", help="The path of the directory to backup.")
arguments = parser.parse_args()

path = Path(arguments.directory)
if path.exists() and path.is_dir():
    logging.info(f"Backing up directory {arguments.directory}")
    backups.backup(path, get_configuration(path))
else:
    print(f'Could {path} either does not exist or is not a directory.')
