from unittest.mock import patch

from src.gmb_app.services.post_service import build_post_payload, publish_post


def test_publish_post_success_calls_integration():
    payload = build_post_payload(summary="hello", image_url="https://example.com/a.jpg")

    with patch("src.gmb_app.services.post_service.create_local_post") as mocked_create:
        mocked_create.return_value = {"name": "posts/123"}
        result = publish_post("creds", "accounts/1/locations/2", "accounts/1", payload)

    assert result["name"] == "posts/123"
    mocked_create.assert_called_once()


def test_publish_post_error_bubbles_up():
    payload = build_post_payload(summary="hello")

    with patch("src.gmb_app.services.post_service.create_local_post") as mocked_create:
        mocked_create.side_effect = RuntimeError("api down")
        try:
            publish_post("creds", "accounts/1/locations/2", "accounts/1", payload)
            assert False, "expected RuntimeError"
        except RuntimeError as exc:
            assert "api down" in str(exc)
