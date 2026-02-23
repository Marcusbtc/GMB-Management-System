import pytest

from src.gmb_app.services.post_service import build_post_payload


def test_build_post_payload_with_required_fields():
    payload = build_post_payload(summary="Hello world", topic_type="STANDARD", language_code="en")
    assert payload["summary"] == "Hello world"
    assert payload["topicType"] == "STANDARD"
    assert payload["languageCode"] == "en"


def test_build_post_payload_rejects_invalid_image_url():
    with pytest.raises(ValueError):
        build_post_payload(summary="x", image_url="ftp://invalid")


def test_build_post_payload_rejects_invalid_cta_url():
    with pytest.raises(ValueError):
        build_post_payload(summary="x", cta_type="LEARN_MORE", cta_url="invalid")


def test_build_post_payload_with_media_and_cta():
    payload = build_post_payload(
        summary="x",
        topic_type="OFFER",
        cta_type="LEARN_MORE",
        cta_url="https://example.com",
        image_url="https://example.com/image.jpg",
    )
    assert payload["topicType"] == "OFFER"
    assert payload["callToAction"]["actionType"] == "LEARN_MORE"
    assert payload["media"][0]["sourceUrl"].startswith("https://")
