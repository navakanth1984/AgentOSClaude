import crp_runtime


def test_version_present() -> None:
    assert crp_runtime.__version__ == "0.1.0"
