import pytest

from routes.api.errors import ApiError
from routes.api.validation import validate_fields


RULES = {
    "name": {"type": str, "required": True, "max_len": 20},
    "price": {
        "type": (int, float),
        "required": True,
        "min": 0,
        "max": 100,
    },
}


def test_validate_fields_returns_clean_data():
    data = {"name": "  Чай  ", "price": 50}

    result = validate_fields(data, RULES)

    assert result == {"name": "Чай", "price": 50}


def test_validate_fields_rejects_missing_required_field():
    with pytest.raises(ApiError) as error:
        validate_fields({"name": "Чай"}, RULES)

    assert error.value.status == 400
    assert "price" in error.value.details


def test_validate_fields_rejects_empty_string():
    with pytest.raises(ApiError) as error:
        validate_fields({"name": "   ", "price": 50}, RULES)

    assert error.value.status == 400
    assert "name" in error.value.details


def test_validate_fields_rejects_bool_as_number():
    with pytest.raises(ApiError) as error:
        validate_fields({"name": "Чай", "price": True}, RULES)

    assert error.value.status == 400
    assert "price" in error.value.details


@pytest.mark.parametrize("price", [-1, 101])
def test_validate_fields_rejects_out_of_range_price(price):
    with pytest.raises(ApiError) as error:
        validate_fields({"name": "Чай", "price": price}, RULES)

    assert error.value.status == 400
    assert "price" in error.value.details


def test_validate_fields_allows_partial_data():
    result = validate_fields(
        {"price": 25},
        RULES,
        partial=True
    )

    assert result == {"price": 25}
