"""Upload logic for DropItX CLI."""

import sys
from pathlib import Path
from typing import Optional

import httpx

from .config import get_api_key, get_api_url


class UploadResult:
    """Result of an upload operation."""
    
    def __init__(self, data: dict):
        self.slug: str = data.get("slug", "")
        self.url: str = data.get("url", "")
        self.filename: str = data.get("filename", "")
        self.delete_token: str = data.get("deleteToken", "")
        self.size: int = data.get("size", 0)
        self.expires_at: str = data.get("expires_at", "")
        self.burn_after_reading: bool = data.get("burn_after_reading", False)
        self.password_protected: bool = data.get("password_protected", False)
    
    def __str__(self) -> str:
        return self.url


def upload_file(
    file_path: str,
    password: Optional[str] = None,
    expires: Optional[str] = None,
    burn: bool = False,
    slug: Optional[str] = None,
) -> UploadResult:
    """Upload a file to DropItX.
    
    Args:
        file_path: Path to the file to upload
        password: Optional password for protection
        expires: Optional expiration time (e.g., "1h", "7d", "1w")
        burn: Whether to burn after reading
        slug: Optional custom slug
    
    Returns:
        UploadResult with the share URL and metadata
    
    Raises:
        FileNotFoundError: If the file doesn't exist
        httpx.HTTPStatusError: If the upload fails
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    api_url = get_api_url()
    api_key = get_api_key()
    
    # Build headers
    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key
    
    # Build form data
    data = {}
    if password:
        data["password"] = password
    if expires:
        data["expires"] = expires
    if burn:
        data["burn"] = "true"
    if slug:
        data["slug"] = slug
    
    # Upload file
    with open(path, "rb") as f:
        files = {"file": (path.name, f)}
        response = httpx.post(
            f"{api_url}/api/cli/upload",
            headers=headers,
            data=data,
            files=files,
            timeout=300,  # 5 minutes for large files
        )
    
    response.raise_for_status()
    return UploadResult(response.json())


def upload_text(
    content: str,
    filename: Optional[str] = None,
    password: Optional[str] = None,
    expires: Optional[str] = None,
    burn: bool = False,
    slug: Optional[str] = None,
) -> UploadResult:
    """Upload text content to DropItX.
    
    Args:
        content: Text content to upload
        filename: Optional filename for the content
        password: Optional password for protection
        expires: Optional expiration time
        burn: Whether to burn after reading
        slug: Optional custom slug
    
    Returns:
        UploadResult with the share URL and metadata
    """
    api_url = get_api_url()
    api_key = get_api_key()
    
    # Build headers
    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key
    
    # Build form data
    data = {"content": content}
    if filename:
        data["filename"] = filename
    if password:
        data["password"] = password
    if expires:
        data["expires"] = expires
    if burn:
        data["burn"] = "true"
    if slug:
        data["slug"] = slug
    
    response = httpx.post(
        f"{api_url}/api/cli/upload/text",
        headers=headers,
        data=data,
        timeout=60,
    )
    
    response.raise_for_status()
    return UploadResult(response.json())


def upload_stdin(
    password: Optional[str] = None,
    expires: Optional[str] = None,
    burn: bool = False,
    slug: Optional[str] = None,
) -> UploadResult:
    """Upload content from stdin.
    
    Args:
        password: Optional password for protection
        expires: Optional expiration time
        burn: Whether to burn after reading
        slug: Optional custom slug
    
    Returns:
        UploadResult with the share URL and metadata
    """
    # Read from stdin
    content = sys.stdin.read()
    if not content:
        raise ValueError("No content from stdin")
    
    return upload_text(
        content=content,
        filename="stdin.txt",
        password=password,
        expires=expires,
        burn=burn,
        slug=slug,
    )
