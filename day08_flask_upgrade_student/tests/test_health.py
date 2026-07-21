import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app as flask_app


def test_health_endpoint():
    """测试 /health 返回 200 状态码和正确响应"""
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["ok"] is True
        assert data["service"] == "day08-flask-upgrade"
        print("✓ test_health_endpoint 测试通过")


if __name__ == "__main__":
    test_health_endpoint()
    print("\n所有测试通过！")