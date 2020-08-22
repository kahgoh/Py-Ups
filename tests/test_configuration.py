from pyups import configuration
from pyups.configuration import Configuration
from unittest.mock import patch
from unittest import mock


def __set_up_no_encryption(s3_bucket: str, repository_path) -> Configuration:
    """
    This is used by the tests to set up a configuration for a repository **without** encryption.
    This is done by mocking the user inputs and running `configuration.get_configuration`.

    Parameters
    ----------
    s3_bucket
        The name of the S3 bucket that the repository will be configured with. The back up
        copies would normally be uploaded to this bucket.

    repository_path
        The path to the repository of files to be backed up. This repository must not yet
        have been initialised (i.e. it has not been previously configured).

    Returns
    -------
    The `Configuration` that was created for the repository.
    """
    with mock.patch('builtins.input') as mock_input:
        mock_input.side_effect = [s3_bucket, "n"]
        return configuration.get_configuration(repository_path=repository_path)


def test_configuration_no_encryption(tmp_path) -> None:
    """
    This tests seting up a configuration for a repository, without encryption.
    """
    created_configuration = __set_up_no_encryption(s3_bucket="abc",
                                                   repository_path=tmp_path)

    assert created_configuration == Configuration(s3_bucket="abc",
                                                  encryption_password=None)


def test_read_configuration_no_encryption(tmp_path) -> None:
    """
    This tests reading back a configuration for a repository (withoouut extra encryptio) after
    it has been set up.
    """
    created_configuration = __set_up_no_encryption(s3_bucket="def",
                                                   repository_path=tmp_path)
    read_configuration = configuration.get_configuration(
        repository_path=tmp_path)

    assert created_configuration == read_configuration


def __set_up_with_encryption(s3_bucket: str, password: str,
                             repository_path) -> None:
    """
    This is used by the tests to set up a configuration for a repository **with** encryption.
    This is done by mocking the user inputs and running `configuration.get_configuration`.

    Parameters
    ----------
    s3_bucket
        The name of the S3 bucket that the repository will be configured with. The back
        up copies would normally be uploaded to this bucket.

    password
        The encryption password that will be configured for the repository.

    repository_path
        The path to the repository of files to be backed up. This repository
        **must not** yet have been initialised (i.e. it has not been previously
        configured).

    Returns
    -------
    The `Configuration` that was created for the repository.
    """
    with mock.patch('builtins.input') as mock_input:
        mock_input.side_effect = [s3_bucket, "y"]

        with mock.patch('getpass.getpass') as mock_getpass:
            mock_getpass.return_value = password
            return configuration.get_configuration(
                repository_path=repository_path)


def __read_configuration_with_encryption(password: str,
                                         repository_path) -> None:
    """
    This is used by the tests to read back the configuration for a repository
    configured with encryption. It is expected that the user will be prompted for
    the encryption password when reading the configuration (the method will mock
    the user input).

    Parameters
    ----------
    password
        The encryption password for the repository. This **must** match the
        password that was set during configuraton.

    repository_path
        The path to the repository of files to be backed up. This repository
        **must** have been already been configured.

    Return
    ------
    The `Configuration` that was read back from the repository.
    """
    with mock.patch('getpass.getpass') as mock_getpass:
        mock_getpass.return_value = password
        return configuration.get_configuration(repository_path=repository_path)


def test_configuration_with_encryption(tmp_path) -> None:
    """
    Tests creating the initial configuration for a repository, with encryption.
    """
    created_configuration = __set_up_with_encryption(s3_bucket="bucket",
                                                     password="abc",
                                                     repository_path=tmp_path)

    assert created_configuration.s3_bucket == "bucket"
    assert created_configuration.encryption_password != None


def test_read_configuration_with_encryption(tmp_path) -> None:
    """
    Tests reading back the configuration for an existing repository, with encryption.
    """
    created_configuration = __set_up_with_encryption(s3_bucket="bucket2",
                                                     password="test",
                                                     repository_path=tmp_path)
    read_configuration = __read_configuration_with_encryption(
        repository_path=tmp_path, password="test")

    assert created_configuration == read_configuration
    assert read_configuration == read_configuration
