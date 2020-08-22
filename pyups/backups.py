import boto3
import logging
from pathlib import Path
from pyups import encryption
from pyups.configuration import Configuration
from pyups.state.repository import StateRepository
from botocore.exceptions import ClientError

"""
When files from the repository are deleted, their backup copies in the S3
bucket are also deleted. S3 allows each delete request to contain multiple
items to delete. This value is the maximum number of items that each delete
request should contain.
"""
__DELETE_GROUP_SIZE = 500

def backup(repository_path: Path, configuration: Configuration) -> None:
    """
    Parameters
    ----------
    path
        The file system path to the directory that will be backed up. This path 
        is expected to be an existing directory.

    configuration
        This provides a representation of the configuration for the backup (e.g.
        which Amazon S3 Bucket to upload backups to).
    """
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(configuration.s3_bucket)
    states = StateRepository(root_path=repository_path)

    if configuration.encryption_password:
        file_provider = lambda file: encryption.encrypted_file(source=file, password=configuration.encryption_password)
    else:
        file_provider = lambda file: (file, lambda: None)

    any_changes = False
    to_delete = []
    for c in states.changes():
        any_changes = True
        if (c.item_path.exists()):
            if (not c.previous_state) or c.previous_state.hash != c.new_state.hash:
                logging.info(f'Uploading item {c.item.as_posix()}.')
                (to_upload, cleanup) = file_provider(c.item_path)
                try:
                    bucket.upload_file(to_upload.as_posix(), f"content/{c.item.as_posix()}")
                finally:
                    cleanup()
            else:
                logging.info(f'Content of item {c.item.as_posix()} has not changed, skipping upload.')
            c.commit()
        else:
            if c.new_state == None and c.previous_state != None:
                logging.info(f'Item {c.item.as_posix()} is no longer in filesystem. It will be deleted.')
                to_delete.append(c)

    delete_groups = [ to_delete[i:min(i + __DELETE_GROUP_SIZE, len(to_delete))]
        for i in range(0, len(to_delete), __DELETE_GROUP_SIZE) ]

    for sublist in delete_groups:
        keys = [ { 'Key': f"content/{c.item.as_posix()}" } for c in sublist ]
        response = bucket.delete_objects(Delete={ 'Objects': keys , 'Quiet': True})

        failed = []
        if 'Errors' in response:
            # List of objects or items that failed to be deleted. Documentation says
            # the list should contain only the things that encountered an error while
            # deleting.
            failed = [ o['Key'] for o in response['Errors'] ]

        for c in to_delete:
            if any(m for m in failed if m == c.item.as_posix()):
                # This means we could not delete the item.
                logging.warn(f'Could not delete {c.item.as_posix()}')
            else:
                c.commit()

    if any_changes == False:
        if __has_content(states):
            print("No changes was detected.")
        else:
            print(f"Directory '{repository_path}' contains no files to back up.")

def __has_content(states: StateRepository) -> bool:
    try:
        next(states.content_paths())
        return True
    except StopIteration:
        return False