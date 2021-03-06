import pytest
import time
#from mmap_kv import instance_obj,config

from sqlitedict_kv import create_inst,config


def flush_datastore(instance):
    instance.delete_all()


@pytest.fixture(scope='session')
def instance():
    inst = create_inst('ds_test_file')
    flush_datastore(inst)
    return inst


def test_ds_create(instance):
    instance.create("key", {})


def test_ds_create_multiple_key(instance):
    with pytest.raises(KeyError):
        instance.create("multiple_key1", {})
        instance.create("multiple_key1", {})


def test_ds_create_key_exception(instance):
    with pytest.raises(ValueError):
        instance.create(1, {})


def test_ds_create_key_greater_than_allowed_value(instance):
    key_exceeding_config = "a" * (config.MAX_KEY_LEN + 1)
    with pytest.raises(ValueError):
        instance.create(key_exceeding_config, {})

def test_ds_create_value_exception(instance):
    with pytest.raises(KeyError):
        instance.create("key", 1)


def test_ds_get(instance):
    msg = {"message": "success"}
    instance.create("get_test", msg)
    assert instance.read("get_test") == msg


def test_ds_delete(instance):
    instance.create("test_delete", {})
    instance.delete("test_delete")
    with pytest.raises(KeyError):
        instance.read("test_delete")

def test_ds_ttl(instance):
    sample = {"key": "Value"}
    instance.create("test_ttl", sample, 3)
    assert instance.read("test_ttl") == sample
    time.sleep(5)
    with pytest.raises(ValueError):
        instance.read("test_ttl")

