import io
from urllib.request import Request as UrlRequest, urlopen

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload


ALLOWED_IMAGE_MIME_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024


def get_drive_service(credentials):
    """Builds a Google Drive API service client."""
    return build("drive", "v3", credentials=credentials)


def list_folders(credentials, parent_id="root"):
    """Lists subfolders from a given Drive folder id."""
    service = get_drive_service(credentials)
    query = (
        "mimeType = 'application/vnd.google-apps.folder' "
        "and trashed = false "
        f"and '{parent_id}' in parents"
    )
    response = service.files().list(
        q=query,
        fields="files(id,name)",
        orderBy="name",
        pageSize=200,
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()
    return response.get("files", [])


def upload_file_to_folder(credentials, folder_id, file_name, file_bytes, mime_type):
    """Uploads a binary file to a Drive folder and returns file metadata."""
    if not file_bytes:
        raise ValueError("File is empty.")
    if len(file_bytes) > MAX_IMAGE_SIZE_BYTES:
        raise ValueError("Image is too large. Maximum size is 10 MB.")
    if (mime_type or "").lower() not in ALLOWED_IMAGE_MIME_TYPES:
        raise ValueError("Unsupported image format. Use JPG, PNG, or WEBP.")

    service = get_drive_service(credentials)
    metadata = {"name": file_name, "parents": [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype=mime_type, resumable=False)

    return service.files().create(
        body=metadata,
        media_body=media,
        fields="id,name,webViewLink,webContentLink",
        supportsAllDrives=True,
    ).execute()


def set_file_public(credentials, file_id):
    """Makes a Drive file readable by anyone with the link."""
    service = get_drive_service(credentials)
    service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
        fields="id",
        supportsAllDrives=True,
    ).execute()


def build_public_file_url(file_id):
    """Builds a direct-view URL suitable for external consumers."""
    return f"https://drive.google.com/uc?export=view&id={file_id}"


def validate_public_url(url, timeout_s=8):
    """Checks if a URL is publicly accessible."""
    req = UrlRequest(url, method="GET")
    with urlopen(req, timeout=timeout_s) as resp:
        return 200 <= resp.status < 400
