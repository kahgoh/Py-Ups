from configparser import ConfigParser
import getpass
from passlib.context import CryptContext
import logging
import secrets
from pathlib import Path

DATA_PATH = ".pyups"

__CRYPT_CONTEXT = CryptContext(
    schemes=["bcrypt", "pbkdf2_sha256", "sha512_crypt"])


class Configuration:
    """
    Provides a representation for the configuration of a directory that may be
    backed up.
    """
    def __init__(self, s3_bucket: str, encryption_password: str = None):
        self.__s3_bucket = s3_bucket
        self.__encryption_password = encryption_password

    @property
    def s3_bucket(self):
        """
        This is the name of the Amazon S3 bucket where the directory will be
        uploaded to for backup.
        """
        return self.__s3_bucket

    @property
    def encryption_password(self):
        """
        If configured, this is the password for encryption. This is `None` if
        encryption is not being used or no password has been set.
        """
        return self.__encryption_password

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return (self.s3_bucket == other.s3_bucket
                    and self.encryption_password == other.encryption_password)
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.s3_bucket, self.encryption_password))

    def __repr__(self) -> str:
        return f"Configuration(s3_bucket={self.s3_bucket})"


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
        logging.debug(
            f"Configuration file {config_file.as_posix()} does not exist")
        configuration = __setup_configuration(repository_path, config_file)

    return configuration


def __read_configuration(config_file: Path) -> Configuration:
    # Configuration for the repository being backed up
    config_parser = ConfigParser()
    config_parser.read(config_file)
    encryption_password = __read_encryption(config_parser)

    return Configuration(s3_bucket=config_parser.get(section="s3",
                                                     option="bucket"),
                         encryption_password=encryption_password)


def __read_encryption(config: ConfigParser):
    if "encryption" in config:
        if "password" in config["encryption"]:
            return __prompt_enter_password(config["encryption"]["password"])
    return None


def __prompt_enter_password(password_hash: str):
    password_input = getpass.getpass("Please enter password: ")
    while not __CRYPT_CONTEXT.verify(password_input, password_hash):
        print("Password is incorrect")
        password_input = getpass.getpass("Please enter password: ")
    return password_input


def __setup_configuration(repository_path: Path,
                          config_file: Path) -> Configuration:
    print(
        f"Backup for {repository_path.as_posix()} has not yet been configured."
    )
    print("Which S3 Bucket should backups be uploaded to?")
    bucket_name = input("Name of S3 Bucket: ")

    password = __prompt_choose_use_encrypt(config_file.parent)

    config_parser = ConfigParser()
    config_parser["s3"] = {"bucket": bucket_name}

    if password:
        password_hash = __CRYPT_CONTEXT.hash(password)
        config_parser["encryption"] = {"password": password_hash}

    config_file.parent.mkdir(parents=True, exist_ok=True)
    with config_file.open(mode="w") as file:
        config_parser.write(file)

    return Configuration(s3_bucket=bucket_name, encryption_password=password)


def __prompt_choose_password():
    while True:
        pass1 = getpass.getpass(f"Choose password: ")
        while len(pass1) == 0:
            print(f"Please choose a password")
            pass1 = getpass.getpass(f"Choose password: ")
        pass2 = getpass.getpass(f"Re-enter password: ")
        if pass1 == pass2:
            return pass1
        else:
            print("Passwords does not match!")


def __prompt_choose_use_encrypt(data_path: Path):
    choice = ""
    while choice not in ["y", "n"]:
        choice = input(
            "Use file encryption for backups? (y/n): ").strip().lower()
        if choice == "y":
            password = __prompt_choose_password()
            return password
        elif choice == "n":
            return None
        else:
            print("Invalid input! Please enter only either \"y\" or \"n\"")
