from configparser import ConfigParser
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
    Reads the configuration for a directory being backed up.
    """
    data_path = repository_path.joinpath(DATA_PATH)
    config_file = data_path.joinpath("config")
    
    # Configuration for the repository being backed up
    config_parser = ConfigParser()
    config_parser.read(config_file)
    
    return Configuration(
        s3_bucket=config_parser.get(section="s3", option="bucket"),
    )
