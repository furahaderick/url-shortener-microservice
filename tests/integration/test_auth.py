async def test_register_user(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "StrongPassword123!"},
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "test@example.com"
    assert "password" not in data


async def test_register_invalid_email(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "invalid-email", "password": "StrongPassword123!"},
    )

    assert response.status_code == 422


async def test_register_duplicate_email(client):
    payload = {"email": "test@example.com", "password": "StrongPassword123!"}

    first = await client.post("/api/v1/auth/register", json=payload)
    second = await client.post("/api/v1/auth/register", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409
