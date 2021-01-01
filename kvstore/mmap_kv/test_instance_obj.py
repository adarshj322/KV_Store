import pytest

from mmap_kv import instance_obj, get_file_name, DataStore



def test_instance_obj():
    assert isinstance(instance_obj('test_file'), DataStore)


def test_instance_obj_on_same_file():
    with pytest.raises(BlockingIOError):
        instance_obj('test_file')


def test_get_uniq_file_name():
    file_name = get_file_name()
    file_name1 = get_file_name()
    assert file_name != file_name1
