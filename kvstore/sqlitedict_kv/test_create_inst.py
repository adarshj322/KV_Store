import pytest

from sqlitedict_kv import create_inst, creat_file_name, KeyStore



def test_create_inst():
    assert isinstance(create_inst('test_file'), KeyStore)


def test_get_uniq_file_name():
    file_name = creat_file_name()
    file_name1 = creat_file_name()
    assert file_name != file_name1
