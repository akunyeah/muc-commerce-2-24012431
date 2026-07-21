import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app as flask_app


def test_metrics_unauthorized():
    """测试未登录访问 /api/metrics 被拦截并重定向到登录页"""
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        response = client.get("/api/metrics")
        assert response.status_code == 302
        assert "/login" in response.location
        print("✓ test_metrics_unauthorized 测试通过")


def test_metrics_authorized():
    """测试登录后 /api/metrics 返回 ok 和 metrics"""
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        with client.session_transaction() as sess:
            sess["username"] = "student"
        
        response = client.get("/api/metrics")
        assert response.status_code == 200
        data = response.get_json()
        assert data["ok"] is True
        assert "metrics" in data
        assert isinstance(data["metrics"], list)
        assert len(data["metrics"]) == 4
        for metric in data["metrics"]:
            assert "label" in metric
            assert "value" in metric
            assert "note" in metric
        print("✓ test_metrics_authorized 测试通过")


if __name__ == "__main__":
    test_metrics_unauthorized()
    test_metrics_authorized()
    print("\n所有测试通过！")