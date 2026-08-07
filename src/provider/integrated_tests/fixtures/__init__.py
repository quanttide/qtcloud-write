"""加载测试文本和风格定义（本地副本）。"""

from pathlib import Path
import yaml

HERE = Path(__file__).parent


def load_text(name: str) -> str:
    return (HERE / name).read_text("utf-8")


def load_style(name: str) -> dict:
    return yaml.safe_load((HERE / name).read_text("utf-8"))


CAMPUS_STYLE = load_style("campus_style.yaml")
CAMPUS_FINAL = load_text("campus_final.txt")

URBAN_STYLE = load_style("urban_style.yaml")
URBAN_FINAL = load_text("urban_final.txt")
