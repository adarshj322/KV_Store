# [kV_Store]

##### File based Key-Value store implemented using mmap and sqlitedict

   A file based key-value data store that supports basic CRD (Create, Read, Delete) operations. This data store can be used as local storage for one single process on one laptop. The data store can be exposed as a library to the clients that can instantiate a class and work with the data store.

**Functionalities:**
  1. It can be initialized using an optional file path. If one is not provided, it will reliably create itself using `uuid`.
  2. Key string capped at 32 characters and Value must be a JSON object capped at 16KB.
  3. If Create is invoked for an existing key, appropriate error message is returned.
  4. A Read operation on the key can be performed by providing the key and receiving the value in the JSON Object
  5. A Delete operation can be performed by providing the key
  6. Every key supports setting a Time-To-Live property when it is created. This property is optional. If provided, it will be evaluated as an integer defining the number of seconds. Once the Time-To-Live for a key has expired, the key will no longer be available for Read or Delete operations.
  7. Only one process can access the datastore (local file) at a time.
  8. Thread safe. (inbuilt in sqlitedict implementation).
  9. If any exception arises appropriate error messages are returned.
  10. A client can access the data store using multiple threads.

**Special Functionalities of sqlitedict implementation:**
  1. Can handle upto 100GB of data effortlessly.
  2. Faster performance and less memory occupied comapared to mmap implementation.
  3. leveraging sqlite functionalities to store data (Stores key : value in '.sqlite' database file
  4. Far less complex implementation comparing to mmap

**Usage:**

###### Creating an instance (mmap implementation)
```
import mmap_kv
inst = mmap_kv.instance_obj()
```

###### Creating an data
```
key = 'Student'
value = {"Name": "Jacob"}  # must be a JSON
time_to_live = 5*1000  # in milliseconds
inst.create(key, value, time_to_live)
```

###### Retrieving data
```
key = 'Student'
inst.get(key)   # returns {"Name": "Jacob"} if retrieved within 5 seconds else ValueError
```

###### Deleting data
```
key = 'Student'
inst.delete(key)  # key-value is removed from the datastore
```

###### Delete all data
```
inst.delete_all()
```

###### Creating an instance (sqlitedict implementation)

```
import sqlitedict_kv
obj = sqlitedict_kv.create_inst('my_db') #file name is optional
```
###### Creating an data
```
key = 'Student'
value = {"Name": "Jacob"}  # must be a JSON
time_to_live = 5*1000  # in milliseconds
obj.create(key, value, time_to_live)
```
###### Retrieving data
```
key = 'Student'
obj.read(key)   # returns {"Name": "Jacob"} if retrieved within 5 seconds else ValueError
```
###### Deleting data
```
key = 'Student'
obj.delete(key)  # key-value is removed from the datastore
```
###### Delete all data
```
obj.delete_all()
```

