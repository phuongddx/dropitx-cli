"""QR code generation for DropItX CLI."""

import io
from typing import Optional

try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False


def generate_qr_text(url: str) -> str:
    """Generate a text-based QR code for the URL.
    
    This is a simple ASCII representation that works without qrcode library.
    """
    # Simple ASCII QR code placeholder
    # In production, use qrcode library for proper QR codes
    lines = [
        "┌" + "─" * (len(url) + 4) + "┐",
        "│  " + url + "  │",
        "└" + "─" * (len(url) + 4) + "┘",
    ]
    return "\n".join(lines)


def generate_qr_ascii(url: str, box_size: int = 1) -> str:
    """Generate ASCII QR code using qrcode library if available.
    
    Falls back to simple text representation if qrcode is not installed.
    """
    if not HAS_QRCODE:
        return generate_qr_text(url)
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size,
        border=1,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    # Generate ASCII output
    f = io.StringIO()
    qr.print_ascii(out=f, invert=True)
    f.seek(0)
    return f.getvalue()


def generate_qr_image(url: str, output_path: str) -> bool:
    """Generate QR code image and save to file.
    
    Returns True if successful, False if qrcode library not available.
    """
    if not HAS_QRCODE:
        return False
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)
    return True
