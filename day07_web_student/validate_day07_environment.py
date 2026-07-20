"""第7天课前环境检查：不启动服务器，不修改学生文件。"""

from importlib.util import find_spec
from pathlib import Path
import sys


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    checks = []

    for package in ("flask", "pandas"):
        checks.append((f"Python包：{package}", find_spec(package) is not None))

    for relative in (
        "app.py",
        "requirements.txt",
        "templates/base.html",
        "templates/login.html",
        "templates/dashboard.html",
        "templates/assistant.html",
        "static/css/style.css",
        "static/js/assistant.js",
        "data/overall_metrics.csv",
        "data/category_analysis.csv",
        "data/segment_analysis.csv",
        "static/images/01_category_bar.png",
        "static/images/03_ordered_line.png",
    ):
        checks.append((f"文件：{relative}", (root / relative).is_file()))

    print(f"检查目录：{root}")
    for label, ok in checks:
        print(f"[{'通过' if ok else '失败'}] {label}")

    failed = [label for label, ok in checks if not ok]
    if failed:
        print(f"\n环境检查未通过：{len(failed)}项失败。")
        return 1
    print("\n环境检查通过，可以运行：python app.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
