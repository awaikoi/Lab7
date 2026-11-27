def create_test_product(client):
    response = client.post(
        "/api/v1/products",
        json={
            "name": "Тестовий товар",
            "price": 50
        }
    )

    assert response.status_code == 201

    return response.get_json()["id"]


def create_test_order(client, product_id):
    return client.post(
        "/api/v1/orders",
        json={
            "email": "buyer@example.com",
            "address": "м. Луцьк, вул. Шевченка, 1",
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 2
                }
            ]
        }
    )


def test_create_order_returns_201(client):
    product_id = create_test_product(client)

    response = create_test_order(client, product_id)

    assert response.status_code == 201
    assert response.get_json()["total_price"] == 100


def test_create_order_with_invalid_email_returns_400(client):
    product_id = create_test_product(client)

    response = client.post(
        "/api/v1/orders",
        json={
            "email": "not-an-email",
            "address": "м. Луцьк",
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 1
                }
            ]
        }
    )

    assert response.status_code == 400


def test_create_order_with_missing_product_returns_400(client):
    response = client.post(
        "/api/v1/orders",
        json={
            "email": "buyer@example.com",
            "address": "м. Луцьк",
            "items": [
                {
                    "product_id": 999999,
                    "quantity": 1
                }
            ]
        }
    )

    assert response.status_code == 400


def test_get_missing_order_returns_404(client):
    response = client.get("/api/v1/orders/999999")

    assert response.status_code == 404


def test_update_order_status_returns_200(client):
    product_id = create_test_product(client)

    created = create_test_order(client, product_id)
    assert created.status_code == 201

    order_id = created.get_json()["id"]

    response = client.patch(
        f"/api/v1/orders/{order_id}/status",
        json={
            "status": "Відправлено"
        }
    )

    assert response.status_code == 200
    assert response.get_json()["status"] == "Відправлено"
