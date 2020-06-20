from configparser import ConfigParser
import logging
from pathlib import Path

DATA_PATH = ".pyups"

class Configuration:
    """
    Provides a representation for the configuration of a directory that may be
    backed up.
    """
    def __init__(self, s3_bucket: str):
        self.__s3_bucket = s3_bucket

    @property
    def s3_bucket(self):
        """
        This is the name of the Amazon S3 bucket where the directory will be
        uploaded to for backup.
        """
        return self.__s3_bucket

def get_configuration(repository_path: Path) -> Configuration:
    """
    Obtains the configuration for a repository (or directory) that is being
    backed up. It will first look for an existing configuration file
    (`.pyups/config`) in the repository. If one exists, the configuration is read
    from the file. Otherwise, the user will be prompted for a basic
    configuration and stored for the next time the back up is run.

    Parameters
    ----------
    repository_path
        The path on the filesystem to the repository (or directory) that is
        being backed up.

    Returns
    -------
    The configuration for the repository.
    """
    data_path = repository_path.joinpath(DATA_PATH)
    config_file = data_path.joinpath("config")

    if config_file.exists():
        configuration = __read_configuration(config_file)
    else:
        logging.debug(f"Configuration file {config_file.as_posix()} does not exist")
        configuration = __setup_configuration(repository_path, config_file)

    return configuration

def __read_configuration(config_file: Path) -> Configuration:
    # Configuration for the repository being backed up
    config_parser = ConfigParser()
    config_parser.read(config_file)

    return Configuration(
        s3_bucket=config_parser.get(section="s3", option="bucket"),
    )

def __setup_configuration(repository_path: Path, config_file: Path) -> Configuration:
    print(f"Backup for {repository_path.as_posix()} has not yet been configured.")
    print("Which S3 Bucket should backups be uploaded to?")
    bucket_name = input("Name of S3 Bucket: ")

    config_parser = ConfigParser()
    config_parser["s3"] = {
        "bucket": bucket_name
    }

    config_file.parent.mkdir(parents=True, exist_ok=True)
    with config_file.open(mode="w") as file:
        config_parser.write(file)

    return Configuration(
        s3_bucket=bucket_name
    )