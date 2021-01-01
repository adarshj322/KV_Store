import json
import mmap
import sys
import threading
import time
from collections import OrderedDict

from mmap_kv import config


def good(val, vtype="key"): # method to check whether the key/value satisfies the constraints respectively.

    if vtype == "key":
        if not isinstance(val, str):
            raise ValueError(f"Key [{val}] must be of type str.")
        return len(val) <= config.MAX_KEY_LEN
    elif vtype == "value":
        if isinstance(val, dict):
            return sys.getsizeof(val) <= config.MAX_VALUE_SIZE
        raise ValueError(f"Value [{val}] must be of type dict.")


class ValueObject: #A simple ValueObject class which can be used to access value based on its ttl if provided.

    def __init__(self, val, created, ttl, *args, **kwargs):
        self.value = val
        self.ttl = ttl
        self.created_at = created

    def is_expired(self):
        if self.ttl is None:
            return False
        curr_ts = int(time.time() * 1000)
        return (curr_ts - self.created) > self.ttl * 1000


class DataStore:
    def __init__(self, file_descriptor, *args, **kwargs):
        self.__fd = file_descriptor
        self.__mmap = self.mmaped_fd_done()
        self.__data = OrderedDict()
        self.__lock = threading.Lock()
        self._read_data()

    def mmaped_fd_done(self) -> mmap.mmap:
            #creates an mmap object for the provided file_descriptor. Always resizes the mmap size to config.MAX_LOCAL_STORAGE_SIZE
        
        try:
            mmaped_fd = mmap.mmap(self.__fd, 0, access=mmap.ACCESS_WRITE)
            mmaped_fd.resize(config.MAX_LOCAL_STORAGE_SIZE)
            return mmaped_fd
        except mmap.error:
            raise

    def _read_data(self) -> None:
        """
            Reads the data from mmap and parse it as json and store in data
        :return:
        """
        raw_data = self.__mmap[:].decode('ascii').rstrip('\0')
        self.__data = json.loads(raw_data)

    def create(self, key, value, ttl=None) -> None:
        """
            Creates a new entry for the given key with the value in data if and only if,
                1. The key is not already present. (raises ValueError with message 'Key already present')
                2. Both key and value satisfies the size constraints.
                3. If ttl is provided, it must be an integer in milli-seconds
        """
        with self.__lock:
            if key in self.__data:
                raise ValueError(f"Key '{key}' already present.")
            if good(key, vtype="key") and good(value, vtype="value"):
                if ttl is not None:
                    try:
                        ttl = int(ttl)
                    except:
                        raise ValueError(f"Time-to-live {ttl} must be an integer value.")
                val_array = [value, int(time.time() * 1000), ttl]
                self.__data[key] = val_array
                self.flush()
            else:
                raise ValueError(
                    f"Either provided key(allowed_size:{config.MAX_KEY_LEN} characters) or value(allowed_size:{config.MAX_VALUE_SIZE} bytes) doesn't meet the size config.")

    def delete(self, key) -> None:
        """
            Deletes the key-value pair from data.
            If key is not present it will ignore.
        """
        with self.__lock:
            if key not in self.__data:
                return  # Ignore if key is non-existent
            del self.__data[key]
            self.flush()

    def get(self, key) -> dict:
        """
            Get the value in data for the given key.
            If key is not present, raises ValueError with message 'Key not in datastore'
            Calculates the expiry attribute if ttl is provided at the time of key creation and if expired,
                deletes the key from data.
        """
        with self.__lock:
            if key not in self.__data:
                raise ValueError(f"Key [{key}] not in datastore.")
            value = ValueObject(*self.__data.get(key))  # type: ValueObject
            if value.is_expired():
                self.__data.pop(key)
                self.flush()
                raise ValueError(f"Key [{key}] Time-to-live expired.")
            return value.value

    def delete_all(self):
        """
            Additional method to flush the database and start new.
        """
        with self.__lock:
            self.__data = dict()
            self.flush()

    def flush(self) -> None:
        """
            Writes the data to mmap by converting it to bytes and filling the unused space with null byte char.
        """
        self.__mmap.seek(0)
        data_string = bytes(json.dumps(self.__data).encode('ascii'))
        self.__mmap.write(data_string)
        empty_space_bytes = self.__mmap.size() - self.__mmap.tell()
        self.__mmap[self.__mmap.tell():] = b'\0' * empty_space_bytes

