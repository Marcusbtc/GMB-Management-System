import hashlib
import json

from data_fetcher import build_local_post_payload
from src.gmb_app.integrations.gbp_client import create_local_post


def build_post_payload(summary, topic_type="STANDARD", language_code="pt-BR", cta_type=None, cta_url=None, image_url=None):
    return build_local_post_payload(
        summary=summary,
        topic_type=topic_type,
        language_code=language_code,
        cta_type=cta_type,
        cta_url=cta_url,
        image_url=image_url,
    )


def payload_hash(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def publish_post(credentials, location_id, account_id, payload):
    return create_local_post(credentials, location_id, account_id, payload=payload)
