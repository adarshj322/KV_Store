import pytest
import time
#from mmap_kv import instance_obj,config

from sqlitedict_kv import create_inst,config




@pytest.fixture(scope='session')
def instance():
    inst = create_inst('test_pop')
    return inst


def test_ds_create(instance):
    for i in range(101):
        instance.create(str(i), {"Name" : "coder"})
