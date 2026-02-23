from src.gmb_app.core.i18n import translate


def test_translate_english_default_key():
    assert translate("en", "create_post") == "Create Post"


def test_translate_fallback_lang():
    assert translate("unknown", "create_post") == "Create Post"


def test_translate_fallback_key():
    assert translate("en", "non_existing_key") == "non_existing_key"
