import models


def test_validate_promocode_rejects_unknown_code(monkeypatch):
    monkeypatch.setattr(
        models,
        "get_promocode",
        lambda code: None
    )

    promo, error = models.validate_promocode("UNKNOWN", 100)

    assert promo is None
    assert error == "Промокод не знайдено."


def test_validate_promocode_rejects_inactive_code(monkeypatch):
    promo_data = {
        "code": "SALE10",
        "active": 0,
        "expires_at": None,
        "min_order": 0,
    }

    monkeypatch.setattr(
        models,
        "get_promocode",
        lambda code: promo_data
    )

    result, error = models.validate_promocode("SALE10", 100)

    assert result is None
    assert error == "Цей промокод неактивний."


def test_validate_promocode_rejects_expired_code(monkeypatch):
    promo_data = {
        "code": "OLD",
        "active": 1,
        "expires_at": "2020-01-01",
        "min_order": 0,
    }

    monkeypatch.setattr(
        models,
        "get_promocode",
        lambda code: promo_data
    )
    monkeypatch.setattr(
        models,
        "now",
        lambda: "2026-11-26 12:00:00"
    )

    result, error = models.validate_promocode("OLD", 100)

    assert result is None
    assert error == "Термін дії промокоду завершено."


def test_validate_promocode_checks_minimum_order(monkeypatch):
    promo_data = {
        "code": "MIN100",
        "active": 1,
        "expires_at": None,
        "min_order": 100,
    }

    monkeypatch.setattr(
        models,
        "get_promocode",
        lambda code: promo_data
    )

    result, error = models.validate_promocode("MIN100", 50)

    assert result is None
    assert "Мінімальна сума замовлення" in error


def test_validate_promocode_accepts_valid_code(monkeypatch):
    promo_data = {
        "code": "SALE10",
        "active": 1,
        "expires_at": None,
        "min_order": 100,
    }

    monkeypatch.setattr(
        models,
        "get_promocode",
        lambda code: promo_data
    )

    result, error = models.validate_promocode("SALE10", 150)

    assert result == promo_data
    assert error is None
