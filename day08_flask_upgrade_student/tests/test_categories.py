import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app as flask_app


def test_categories_filter_fashion():
    """测试 /api/categories?category=Fashion 返回筛选结果"""
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        with client.session_transaction() as sess:
            sess["username"] = "student"
        
        response_all = client.get("/api/categories")
        assert response_all.status_code == 200
        data_all = response_all.get_json()
        all_count = len(data_all["rows"])
        
        response_fashion = client.get("/api/categories?category=Fashion")
        assert response_fashion.status_code == 200
        data_fashion = response_fashion.get_json()
        fashion_count = len(data_fashion["rows"])
        
        assert data_fashion["category"] == "Fashion"
        assert fashion_count <= all_count
        assert fashion_count > 0
        
        for row in data_fashion["rows"]:
            assert row["偏好品类"] == "Fashion"
        print("✓ test_categories_filter_fashion 测试通过")


def test_categories_all():
    """测试 /api/categories 返回所有品类数据"""
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        with client.session_transaction() as sess:
            sess["username"] = "student"
        
        response = client.get("/api/categories")
        assert response.status_code == 200
        data = response.get_json()
        assert data["ok"] is True
        assert data["category"] == "全部"
        assert isinstance(data["rows"], list)
        assert len(data["rows"]) > 0
        print("✓ test_categories_all 测试通过")


if __name__ == "__main__":
    test_categories_filter_fashion()
    test_categories_all()
    print("\n所有测试通过！")