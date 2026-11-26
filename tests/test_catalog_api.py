def test_get_products_returns_200(client):
    response = client.get("/api/v1/products")

    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_create_product_returns_201(client):
    response = client.post(
        "/api/v1/products",
        json={
            "name": "Чай",
            "price": 50
        }
    )

    assert response.status_code == 201
    assert response.get_json()["name"] == "Чай"


def test_create_product_with_invalid_price_returns_400(client):
    response = client.post(
        "/api/v1/products",
        json={
            "name": "Чай",
            "price": -5
        }
    )

    assert response.status_code == 400


def test_get_missing_product_returns_404(client):
    response = client.get("/api/v1/products/999999")

    assert response.status_code == 404


def test_create_category_returns_201(client):
    response = client.post(
        "/api/v1/categories",
        json={
            "name": "Електроніка"
        }
    )

    assert response.status_code == 201
    assert response.get_json()["name"] == "Електроніка"


def test_get_missing_category_returns_404(client):
    response = client.get("/api/v1/categories/999999")

    assert response.status_code == 404
