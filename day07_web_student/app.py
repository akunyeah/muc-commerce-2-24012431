
from functools import wraps
from pathlib import Path

from flask import Flask, flash, jsonify, make_response, redirect, render_template, request, session, url_for


from services.data_service import load_dashboard_data, export_category_csv
from services.qa_service import answer_question


BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)
app.config["SECRET_KEY"] = "day07-classroom-demo-key"
app.config["TEMPLATES_AUTO_RELOAD"] = True
def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "username" not in session:
            flash("请先登录后再访问数据看板。", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


@app.route("/")
def index():
    return redirect(url_for("dashboard") if "username" in session else url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if username == "student" and password == "day07":
            session["username"] = username
            flash("登录成功，欢迎进入电商用户分析系统。", "success")
            return redirect(url_for("dashboard"))
        flash("账号或密码错误。演示账号：student / day07", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("你已安全退出。", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    category = request.args.get("category", "全部")
    dashboard_data = load_dashboard_data(BASE_DIR, category)
    return render_template(
        "dashboard.html",
        username=session["username"],
        selected_category=category,
        **dashboard_data,
    )


@app.route("/assistant")
@login_required
def assistant():
    return render_template("assistant.html", username=session["username"])


@app.route("/api/ask", methods=["POST"])
@login_required
def ask():
    payload = request.get_json(silent=True) or {}
    question = str(payload.get("question", "")).strip()
    if not question:
        return jsonify({"ok": False, "answer": "请输入一个与项目数据有关的问题。"}), 400
    return jsonify({"ok": True, "answer": answer_question(BASE_DIR, question)})

@app.route("/download")
@login_required
def download():
    from urllib.parse import quote

    category = request.args.get("category", "全部")
    csv_bytes = export_category_csv(BASE_DIR, category)

    # ASCII 文件名（兼容旧浏览器，不让 latin-1 编码报错）
    safe_filename = f"{quote(category, safe='')}_category_data.csv"
    # 完整中文文件名，通过 RFC 5987 编码下发
    display_filename = f"{category}_品类分析数据.csv"
    encoded = quote(display_filename)

    resp = make_response(csv_bytes)
    resp.headers["Content-Type"] = "text/csv; charset=utf-8-sig"
    # 关键：filename 只用 ASCII；真正的中文名通过 filename*=UTF-8'' 下发
    resp.headers["Content-Disposition"] = (
        f"attachment; filename=\"{safe_filename}\"; filename*=UTF-8''{encoded}"
    )
    return resp


@app.errorhandler(404)
def page_not_found(_error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True, port=5000)
