# DropItX CLI - Codebase Summary

## Package Structure

```
dropitx-cli/
├── dropitx/
│   ├── __init__.py         (3 LOC - __version__ = "1.0.0")
│   ├── cli.py              (339 LOC - Click CLI, all commands)
│   ├── uploader.py         (172 LOC - httpx upload logic)
│   ├── config.py           (74 LOC - config/env resolution)
│   └── qr.py               (71 LOC - optional QR generation)
├── pyproject.toml          (49 LOC - deps, scripts)
├── README.md               (211 LOC - usage docs)
└── tests/                  (empty - no tests yet)
```

**Total Python LOC:** ~659  
**Entry Point:** `dropitx = "dropitx.cli:cli"` (console script)

## File Responsibilities

### `dropitx/__init__.py` (3 LOC)
- Exports `__version__ = "1.0.0"`
- Duplicated in pyproject.toml (must keep in sync)

### `dropitx/cli.py` (339 LOC) - Main CLI
- **Click app:** `@click.group(invoke_without_command=True)` named `cli`
- **Commands:** `upload`, `text`, `config`, `qr`
- **Global options:** `--password`, `--expires`, `--burn`, `--slug`, `--qr`, `--qr-file`
- **Pipe magic:** Bare `dropitx` with piped stdin → `upload_stdin()`
- **Output layer:** `print_upload_result()` renders green Panel + Table
- **Error handling:** Generic Exception catch, red error text, `sys.exit(1)`

### `dropitx/uploader.py` (172 LOC) - Upload Logic
- **`upload_file()`** - multipart POST for files, 300s timeout
- **`upload_text()`** - form POST for text content, 60s timeout
- **`upload_stdin()`** - reads sys.stdin, delegates to `upload_text()`
- **`UploadResult`** - dataclass for API response fields
- **API contract:** Optional `X-API-Key` header, form fields (password, expires, burn, slug)

### `dropitx/config.py` (74 LOC) - Configuration
- **`get_api_key()`** - precedence: env var → config file → None
- **`get_api_url()`** - precedence: env var → config file → DEFAULT_API_URL
- **`set_api_key()`** - saves to `~/.dropitx/config.json`
- **`load_config()`/`save_config()`** - JSON file I/O
- **Masking:** `config show` displays `api_key[:8] + "..." + api_key[-4:]`

### `dropitx/qr.py` (71 LOC) - QR Generation
- **`HAS_QRCODE`** - module-level bool from try/except import
- **`generate_qr_ascii()`** - fallback to text box if qrcode missing
- **`generate_qr_image()`** - returns False on missing dep, doesn't raise
- **Params:** ASCII uses ERROR_CORRECT_L, image uses ERROR_CORRECT_M

## How They Connect

### Command Flow
```
cli() (Click group)
├── No subcommand + stdin pipe → upload_stdin() → print_upload_result()
├── upload command:
│   ├── No files + stdin → upload_stdin()
│   └── Files provided → loop upload_file() → print_upload_result()
├── text command → upload_text() → print_upload_result()
├── config command → config.py functions
└── qr command → qr.py functions
```

### Config Resolution
```
get_api_key()
├── os.getenv("DROPITX_API_KEY")
├── load_config()["api_key"]
└── None (uploads still work)
```

### Upload Pipeline
```
upload_file(path, password, expires, burn, slug)
├── Read file bytes
├── httpx.post(api_url + "/api/cli/upload", ...)
│   ├── files={"file": ...}
│   ├── data={password, expires, burn, slug}
│   └── headers={"X-API-Key": key if exists}
└── return UploadResult(dataclass)
```

## Key Patterns

### Password Idiom (Repeated in Every Upload Command)
```python
@click.option("--password", "-p", is_flag=False, flag_value="")
def upload(password, ...):
    if password == "":  # bare -p flag
        password = click.prompt(..., hide_input=True, confirmation_prompt=True)
```

### Optional Dependency Pattern
```python
try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False

def generate_qr_image(url, output):
    if not HAS_QRCODE:
        return False  # caller surfaces pip install message
```

### API Response Mapping
```python
# Server returns: deleteToken (camelCase)
# Client stores: result.delete_token (snake_case)
# Other fields already snake_case: slug, url, filename, size, expires_at
```

### Single Shared Console
```python
from rich.console import Console
console = Console()  # global, reused everywhere
```

## Data Flow

### File Upload Path
```
User input → Click CLI → upload_file()
├── Read file from disk
├── Build multipart form
├── httpx POST (300s timeout)
└── UploadResult → print_upload_result()
    └── Rich Panel + Table → stdout
```

### Text Upload Path
```
User input → Click CLI → upload_text()
├── Accept content string + optional filename
├── Build form (content, filename)
├── httpx POST (60s timeout)
└── UploadResult → print_upload_result()
```

### Stdin Upload Path
```
Pipe → bare dropitx → upload_stdin()
├── sys.stdin.read()
├── Delegate to upload_text(filename="stdin.txt")
└── UploadResult → print_upload_result()
```

## LOC Distribution

| File | LOC | Purpose |
|------|-----|---------|
| cli.py | 339 | CLI commands, options, output rendering |
| uploader.py | 172 | HTTP upload logic, API client |
| config.py | 74 | Config file and env resolution |
| qr.py | 71 | QR code generation (optional) |
| __init__.py | 3 | Version export |

**Note:** `cli.py` is the only file exceeding 200 LOC. If more commands are added, consider splitting into command modules (e.g., `upload_cmd.py`, `config_cmd.py`).

---

**Last Updated:** 2026-06-28  
**Total Python LOC:** ~659
