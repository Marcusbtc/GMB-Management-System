from src.gmb_app.integrations.drive_client import build_public_file_url


def test_build_public_file_url():
    result = build_public_file_url("abc123")
    assert result == "https://drive.google.com/uc?export=view&id=abc123"
