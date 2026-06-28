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
├── tests/
│   └── test_dropitx.py     (136 LOC - 13 tests, network-free)
├── .github/workflows/
│   └── ci.yml              (37 LOC - Python 3.9+3.12 matrix, pytest, CLI smoke)
├── pyproject.toml          (49 LOC - deps, scripts)
├── README.md               (214 LOC - usage docs)
├── LICENSE                 (21 LOC - MIT, Copyright 2026 DropItX)
└── .gitignore              (excludes __pycache__, *.egg-info, .venv, .pytest_cache)
```

**Total Python LOC:** ~795 (including tests)  
**Entry Point:** `dropitx = "dropitx.cli:cli"` (console script)  
**Repository:** https://github.com/phuongddx/dropitx-cli (public, MIT)

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

### `tests/test_dropitx.py` (136 LOC) - Test Suite
- **13 network-free tests** covering:
  - Package version and module imports
  - CLI surface (`--help`, `--version`, subcommands via `CliRunner`)
  - `UploadResult` field mapping (including `deleteToken`→`delete_token` camelCase + defaults)
  - Config/env resolution precedence (env > file > default)
  - QR text/ascii/image generation with `skipif(not HAS_QRCODE)`
- **Isolation:** Uses `monkeypatch` to redirect config to tmp paths (never reads real `~/.dropitx`)
- **Runner:** pytest with network-free execution

### `.github/workflows/ci.yml` (37 LOC) - CI Pipeline
- **Matrix:** Python 3.9 + 3.12
- **Steps:** Install `.[dev,qr]` → `pytest -q` → CLI smoke (`--version`, `--help`)
- **Triggers:** Push to `main`, pull requests
- **Status:** Green on both Python versions

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

### Test Coverage
```
pytest runs tests/test_dropitx.py
├── Version/import checks → dropitx.__version__, module attributes
├── CLI surface → CliRunner invokes --help, --version, subcommands
├── UploadResult mapping → Server deleteToken → client delete_token
├── Config resolution → monkeypatch isolates env/file/default precedence
└── QR generation → skipif guards when qrcode[pil] missing
```

### CI Pipeline
```
GitHub Actions (.github/workflows/ci.yml)
├── Push to main or PR
├── Matrix: Python 3.9, 3.12
├── Steps:
│   ├── checkout@v4
│   ├── setup-python@v5
│   ├── pip install -e '.[dev,qr]'
│   ├── pytest -q (13 tests)
│   └── CLI smoke (--version, --help)
└── Result: Green check on all versions
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
| test_dropitx.py | 136 | Test suite (13 tests, network-free) |
| config.py | 74 | Config file and env resolution |
| qr.py | 71 | QR code generation (optional) |
| ci.yml | 37 | CI pipeline (Python 3.9+3.12 matrix) |
| __init__.py | 3 | Version export |

**Note:** `cli.py` is the only file exceeding 200 LOC. If more commands are added, consider splitting into command modules (e.g., `upload_cmd.py`, `config_cmd.py`).

---

**Last Updated:** 2026-06-28  
**Total Python LOC:** ~795 (including tests)  
**Repository:** https://github.com/phuongddx/dropitx-cli (public, MIT)
