from pathlib import Path
import yaml

def test_config_has_diseases():
    cfg = yaml.safe_load(Path("src/config/diseases.yaml").read_text())
    assert "diseases" in cfg and len(cfg["diseases"]) >= 3
