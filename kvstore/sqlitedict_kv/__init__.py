from sqlitedict import SqliteDict

from . import config
from .keystore import KeyStore

def creat_file_name()-> str:
    """
    Creates a unique file name for datastore by appending epoch timestamp to the file name
    :return:
    """
    import uuid
    uniq_append_string = uuid.uuid4().hex
    return "LOCAL_STORAGE_{}".format(uniq_append_string)

def create_inst(file_name = None)->KeyStore:
    if file_name is None:
        file_name = creat_file_name()
    full_file_name = f"{config.LOCAL_STORAGE_PREPEND_PATH}/{file_name}.sqlite"
    mydict = SqliteDict(full_file_name, autocommit = True)
    return KeyStore(mydict, full_file_name)

__all__ = ['create_inst']
