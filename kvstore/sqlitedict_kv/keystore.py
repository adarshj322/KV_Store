import threading
import time
from sqlitedict import SqliteDict
import os
import json
from sqlitedict_kv import config
import sys




#for create operation 
#use syntax "create(key_name,value,timeout_value)" timeout is optional you can continue by passing two arguments without timeout
def good(val, vtype="key"): # method to check whether the key/value satisfies the constraints respectively.

    if vtype == "key":
        if not isinstance(val, str):
            raise ValueError(f"Key [{val}] must be of type str.")
        return len(val) <= config.MAX_KEY_LEN
    elif vtype == "value":
        if isinstance(val, dict):
            return sys.getsizeof(val) <= config.MAX_VALUE_SIZE
        raise ValueError(f"Value [{val}] must be of type dict.")


class KeyStore:

    def __init__(self, dictionary,file_name, *args, **kwargs):
        self.__dict = dictionary
        self.__file = file_name
        self.__lock = threading.Lock()

    def create(self,key,value,timeout=0)->int:
        with self.__lock:
            if key in self.__dict:
                raise KeyError("error: this key already exists") #raising a KeyError
            else:
                if os.stat(self.__file).st_size < config.MAX_LOCAL_STORAGE_SIZE:
                    if good(key, vtype = "key") and good(value, vtype = "value"):
                        if timeout == 0:
                            value["timeout"] = 0
                        else:
                            value["timeout"] = (time.time()*1000 + timeout)
                        self.__dict[key] = json.dumps(value)
                        return 1
                            
                    else:
                        raise ValueError(
                            f"Either provided key(allowed_size:{config.MAX_KEY_LEN} characters) or value(allowed_size:{config.MAX_VALUE_SIZE} bytes) doesn't meet the size config.")

                else:
                    raise MemoryError("error: Memory limit exceeded!! ")# raising a Memory Error


                
    def read(self,key) -> dict:
        
        with self.__lock:
            if key not in self.__dict:
                raise KeyError("error: given key does not exist in database. Please enter a valid key") #raising a key error
            else:
                mydict = json.loads(self.__dict[key])
                if mydict['timeout']!=0:
                    if (time.time()*1000)<mydict['timeout']: #comparing the present time with expiry time
                        return mydict
                    else:
                        raise ValueError("error: time-to-live of",key,"has expired") #raising a value error
                else:
                    
                    return mydict

    def delete(self,key)-> int:
        
        with self.__lock:
            if key not in self.__dict:
                raise KeyError("error: given key does not exist in database. Please enter a valid key") #raising a key error
            else:
                mydict = json.loads(self.__dict[key])
                if mydict["timeout"]!= 0:
                    if (time.time()*1000)<mydict['timeout']: #comparing the current time with expiry time
                        del self.__dict[key]
                        return 2
                    else:
                        raise ValueError("error: time-to-live of",key,"has expired") #raising a value error
                else:
                    del self.__dict[key]
                    return 2

    def delete_all(self)->None:
        
        with self.__lock:
            self.__dict = dict()

