from src.utils.io import RAW, PROCESSED

def test_paths_exist():
    assert RAW.exists()
    assert PROCESSED.exists()
