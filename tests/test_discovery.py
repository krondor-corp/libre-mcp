import os

import pytest

from src.office import discovery
from src.office.soffice import unique_pipe_name


def test_worker_script_exists():
    path = discovery.worker_script()
    assert path.endswith("uno_worker.py")
    assert os.path.exists(path)


def test_find_soffice_bad_override():
    with pytest.raises(discovery.DiscoveryError):
        discovery.find_soffice("/no/such/soffice")


def test_find_python_bad_override():
    with pytest.raises(discovery.DiscoveryError):
        discovery.find_bundled_python("/no/such/python")


def test_pipe_names_are_unique():
    names = {unique_pipe_name() for _ in range(100)}
    assert len(names) == 100
