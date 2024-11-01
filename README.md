# Laravel Translation Key Updater

This quickly hacked up Python script scans a specified PHP or Blade file to replace hardcoded translation strings within `__()` calls with keys. It then updates a specified translation file (in Laravel's `/lang` format) to include the detected strings as key-value pairs. The script is interactive, allowing you to customize keys or accept defaults based on the translation text.

## Features

- Finds hardcoded strings within `__()` calls.
- Prompts for each detected string, suggesting a default key derived from the first four words. You can customize the key or press Enter to accept the default.
- Adds new key-value pairs to the specified translation file without removing existing entries.
- Preserves HTML tags, attributes, and placeholders like `:name` or `:level`.

## Requirements

- **Python 3**
- **Laravel Project with a Translations Directory**: Laravel’s `lang` directory (e.g., `lang`).

## Usage

```bash
python move-translation-strings-to-keys.py <input_file> <translation_file>
```

Example:
```bash
python move-translation-strings-to-keys.py resources/views/profile/index/partials/hero/core.blade.php lang/en/profile.php
```
