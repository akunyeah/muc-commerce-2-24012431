"""第7天下午成果检查：检查核心结构、TODO、README、截图和拓展证据。"""

from pathlib import Path
import re
import sys


REQUIRED_FILES = [
    "app.py",
    "README.md",
    "requirements.txt",
    "templates/base.html",
    "templates/login.html",
    "templates/dashboard.html",
    "templates/assistant.html",
    "services/data_service.py",
    "services/qa_service.py",
    "static/css/style.css",
    "static/js/assistant.js",
]

SCREENSHOTS = [
    "screenshots/01_login.png",
    "screenshots/02_dashboard.png",
    "screenshots/03_interaction.png",
    "screenshots/04_assistant.png",
]

EXTENSION_EVIDENCE = [
    "screenshots/05_extension.png",
    "test_result.txt",
]


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    errors = []
    warnings = []

    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"缺少文件：{relative}")

    for relative in SCREENSHOTS:
        if not (root / relative).is_file():
            warnings.append(f"缺少验收截图：{relative}")

    text_files = [root / path for path in REQUIRED_FILES if path.endswith((".py", ".html"))]
    unfinished = []
    for path in text_files:
        if path.is_file():
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if re.search(r"TODO\s*(2-1|2-2|2-3|3-1|4-1)", line):
                    unfinished.append(f"{path.relative_to(root)}:{number}")
    if unfinished:
        warnings.append("仍有TODO：" + "、".join(unfinished[:12]))

    app_text = (root / "app.py").read_text(encoding="utf-8") if (root / "app.py").is_file() else ""
    for pattern, message in [
        (r"methods\s*=\s*\[.*POST", "登录路由未发现POST方法"),
        (r"session", "未发现Session登录状态"),
        (r"/api/ask", "未发现问答接口"),
    ]:
        if not re.search(pattern, app_text, re.I | re.S):
            errors.append(message)

    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").is_file() else ""
    if "姓名：TODO" in readme or "学号：TODO" in readme:
        warnings.append("README中的姓名或学号尚未填写")
    for label in ["选择的拓展任务", "拓展访问或运行方法", "拓展证据文件"]:
        if re.search(rf"{label}：\s*TODO", readme):
            warnings.append(f"README中的“{label}”尚未填写")

    tests_dir = root / "tests"
    has_tests = tests_dir.is_dir() and any(tests_dir.rglob("test_*.py"))
    has_extension_evidence = any((root / path).is_file() for path in EXTENSION_EVIDENCE) or has_tests
    if not has_extension_evidence:
        warnings.append("未发现拓展证据：请提供screenshots/05_extension.png、test_result.txt或tests/test_*.py")

    secret_patterns = [r"sk-[A-Za-z0-9_-]{20,}", r"AIza[A-Za-z0-9_-]{20,}"]
    for path in text_files:
        if path.is_file():
            content = path.read_text(encoding="utf-8")
            if any(re.search(pattern, content) for pattern in secret_patterns):
                errors.append(f"疑似真实API密钥：{path.relative_to(root)}")

    print(f"检查目录：{root}\n")
    for message in errors:
        print(f"[失败] {message}")
    for message in warnings:
        print(f"[提醒] {message}")
    if not errors:
        print("[通过] 必需结构与关键路由检查通过")

    print(f"\n结论：{len(errors)}项失败，{len(warnings)}项提醒。")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
