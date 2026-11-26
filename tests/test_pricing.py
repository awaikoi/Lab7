import pytest
import models


@pytest.mark.parametrize(
    ("product", "expected"),
    [
        ({"price": 100, "discount_percent": 0}, 100.00),
        ({"price": 100, "discount_percent": 15}, 85.00),
        ({"price": 19.99, "discount_percent": 10}, 17.99),
        ({"price": 100, "discount_percent": 100}, 0.00),
        ({"price": 100, "discount_percent": 125}, 0.00),
        ({"price": 100, "discount_percent": -10}, 100.00),
    ],
)
def test_effective_product_price(product, expected):
    result = models.effective_product_price(product)

    assert result == expected


@pytest.mark.parametrize(
    ("promo", "subtotal", "expected"),
    [
        ({"discount_percent": 10, "discount_amount": 0}, 200, 20.00),
        ({"discount_percent": 0, "discount_amount": 30}, 100, 30.00),
        ({"discount_percent": 25, "discount_amount": 20}, 100, 25.00),
        ({"discount_percent": 10, "discount_amount": 40}, 200, 40.00),
        ({"discount_percent": 0, "discount_amount": 150}, 100, 100.00),
        ({"discount_percent": 0, "discount_amount": 0}, 0, 0.00),
    ],
)
def test_calculate_promocode_discount(promo, subtotal, expected):
    result = models.calculate_promocode_discount(promo, subtotal)

    assert result == expected