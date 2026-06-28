# DropItX CLI - Project Roadmap

## Current State (v1.0.0 - 2026-06-28)

**Working Features:**
- File, text, and stdin uploads to DropItX API
- Password protection, expiration, burn-after-reading, custom slug
- Rich terminal output with Panel/Table formatting
- ASCII QR code generation
- Optional image QR with `dropitx[qr]` extra
- Config management (API key, URL) with env override

**Known Gaps:**
- No automated tests (pytest mentioned but no test files)
- No CI/CD pipeline
- No release automation
- Python version mismatch (declares 3.8+, requires 3.9+)
- No progress indication for large file uploads
- No client-side validation for slug length/expires format
- No chunked/resumable upload support
- No retry logic on network failures

## Proposed Roadmap

### Phase 1: Foundation & Reliability (Proposed)

**Priority: HIGH**

**1.1 Fix Python Version Declaration**
- Change `requires-python = ">=3.9"` in pyproject.toml
- Update classifiers to remove Python 3.8
- **Why:** Code uses PEP 585 generics (`list[UploadResult]`, `tuple[str, ...]`) which require 3.9+
- **Effort:** 5 minutes (one-line change)

**1.2 Add Test Suite**
- Create `tests/` directory with pytest structure
- Unit tests for:
  - `config.py`: env precedence, file loading, masking
  - `uploader.py`: API client, form building, response mapping
  - `qr.py`: fallback behavior, HAS_QRCODE handling
- Integration tests:
  - CLI invocation patterns (upload, text, pipe)
  - Error handling paths
- **Effort:** 2-3 days
- **Acceptance:** >80% coverage, tests pass on CI

**1.3 Add CI Pipeline**
- GitHub Actions workflow: test on Python 3.9, 3.10, 3.11, 3.12
- Run pytest with coverage
- Lint with ruff or black
- **Effort:** 1 day
- **Acceptance:** PR checks pass, all tests green

**1.4 Add Release Automation**
- GitHub Actions workflow for PyPI publishing
- Trigger on tag push (e.g., `v1.1.0`)
- Build dist, check with twine, upload to PyPI
- **Effort:** 1 day
- **Acceptance:** `git tag v1.1.0 && git push --tags` publishes to PyPI

### Phase 2: Enhanced UX (Proposed)

**Priority: MEDIUM**

**2.1 Upload Progress Indication**
- Add progress bar for large file uploads (300s timeout)
- Use `rich.progress` or similar
- Show during httpx POST multipart upload
- **Effort:** 1 day
- **Why:** Users have no feedback during long uploads

**2.2 Client-Side Validation**
- Validate slug length (3-32 chars) before sending
- Validate expires format (regex: `^\d+[hdwm]$`)
- Surface clear errors before upload attempt
- **Effort:** 0.5 day
- **Why:** Fail fast, reduce API roundtrips

**2.3 Retry Logic**
- Add retry on network errors (timeout, connection refused)
- Exponential backoff, max 3 retries
- Configurable via `--retry` flag or env var
- **Effort:** 1 day
- **Why:** Improve reliability on unstable networks

### Phase 3: Advanced Features (Proposed)

**Priority: LOW**

**3.1 Chunked/Resumable Uploads**
- Support large files (>100MB) with chunked upload
- Server-side support required (API enhancement)
- Resume interrupted uploads via upload ID
- **Effort:** 3-5 days (requires API changes)
- **Why:** Enable sharing large datasets, logs, VM images

**3.2 Batch Operations**
- `dropitx upload --batch manifest.json` for bulk uploads
- Parallel uploads with concurrency limit
- Aggregate result summary
- **Effort:** 2 days
- **Why:** Power users sharing many files at once

**3.3 Download Command**
- `dropitx download <url|slug>` to retrieve files
- Auth via API key if password-protected
- **Effort:** 1-2 days (requires API endpoint)
- **Why:** Complete the share lifecycle

**3.4 History/Cache**
- Local cache of recent uploads (sqlite or JSON)
- `dropitx history` to show past uploads
- `dropitx delete <slug>` to remove files
- **Effort:** 2 days
- **Why:** Users lose share URLs constantly

### Phase 4: Polish (Proposed)

**Priority: LOW**

**4.1 Modularity**
- Split `cli.py` (339 LOC) into command modules:
  - `dropitx/commands/upload.py`
  - `dropitx/commands/config.py`
  - `dropitx/commands/qr.py`
- **Effort:** 1 day
- **Why:** Easier to add commands, reduces file length

**4.2 Shell Completions**
- Generate shell completion scripts (bash, zsh, fish)
- Use `click-completion` or manual
- **Effort:** 0.5 day
- **Why:** Better DX, autocomplete flags/files

**4.3 Man Pages**
- Generate man page from Click docstrings
- Include in package, install to `man/man1/`
- **Effort:** 0.5 day
- **Why:** Standard CLI tool convention

**4.4 Config Validation**
- Validate config file on load (URL format, key prefix)
- Clear errors on malformed config
- **Effort:** 0.5 day
- **Why:** Users may corrupt JSON manually

## Dependencies & Blockers

### External Dependencies
- **Chunked upload:** Requires DropItX API support
- **Download command:** Requires API endpoint
- **History/cache:** Local-only, no API changes needed

### Internal Dependencies
- **Release automation (1.4)** should come after **CI (1.3)**
- **Progress indication (2.1)** benefits from **retry logic (2.2)**
- **Modularity (4.1)** should precede **new commands (3.x)**

## Non-Goals (Explicitly Out of Scope)

- GUI or web interface (CLI-only project)
- Account management/registration (use web dashboard)
- Multi-account/profile switching (not requested)
- Custom API endpoints beyond base URL (use env override)
- Plugin system (keep it simple)

## Success Metrics

**Phase 1 (Foundation):**
- All tests pass on 3.9, 3.10, 3.11, 3.12
- PR checks automated
- Release process fully automated
- Zero manual steps for publishing

**Phase 2 (Enhanced UX):**
- Users see progress during uploads
- Validation errors surface before API calls
- Intermittent network failures handled gracefully

**Phase 3+ (Advanced):**
- Large file sharing enabled (>100MB)
- Power users can batch upload
- Complete share lifecycle (upload + download + delete)

## Risks & Considerations

**API Compatibility:**
- Chunked upload/resume requires server-side changes
- Download command requires new endpoint
- Coordinate with DropItX API team before implementing

**Backward Compatibility:**
- New validation (slug length, expires format) must not break existing workflows
- Feature flags (retry, progress) should be opt-in initially

**Dependency Bloat:**
- Avoid adding heavy deps for marginal gains
- Prefer stdlib or already-installed packages (httpx, rich, click)

---

**Last Updated:** 2026-06-28  
**Roadmap Status:** Proposed, not committed
