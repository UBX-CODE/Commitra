import pytest
from tools.git_tools import is_file_sensitive, _map_status_code

def test_is_file_sensitive():
    assert is_file_sensitive(".env") is True
    assert is_file_sensitive("config/.env.prod") is True
    assert is_file_sensitive("key.pem") is True
    assert is_file_sensitive("id_rsa") is True
    assert is_file_sensitive("app/credentials.json") is True
    assert is_file_sensitive("README.md") is False
    assert is_file_sensitive("src/main.py") is False

def test_map_status_code():
    assert _map_status_code("M") == "modified"
    assert _map_status_code("A") == "added"
    assert _map_status_code("D") == "deleted"
    assert _map_status_code("?") == "unknown"
