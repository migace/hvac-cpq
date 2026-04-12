from fastapi.testclient import TestClient


def test_validation_error_has_consistent_shape(client: TestClient) -> None:
    response = client.post("/product-families", json={"code": "x"})

    assert response.status_code == 422
    body = response.json()

    assert "error" in body
    assert body["error"]["type"] == "RequestValidationError"
    assert body["error"]["code"] == "request_validation_error"
    assert "request_id" in body["error"]
    assert "details" in body["error"]


def test_not_found_error_has_request_id(client: TestClient) -> None:
    response = client.get("/product-quotes/999999")

    assert response.status_code == 404
    body = response.json()

    assert body["error"]["type"] == "ProductQuoteNotFoundError"
    assert body["error"]["code"] == "product_quote_not_found"
    assert body["error"]["request_id"] is not None


def test_custom_request_id_is_returned(client: TestClient) -> None:
    request_id = "test-request-id-123"

    response = client.get("/health", headers={"X-Request-ID": request_id})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == request_id