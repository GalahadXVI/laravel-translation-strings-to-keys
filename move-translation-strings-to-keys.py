import sys
import os
import re

def generate_key(text):
    # Remove HTML tags and special characters, limit to four words
    text_without_tags = re.sub(r'<[^>]+>', '', text)
    words = re.findall(r'\w+', text_without_tags.lower())
    key = '_'.join(words[:4])
    return key

def load_existing_translations(translations_path):
    existing_translations = {}
    if os.path.exists(translations_path):
        with open(translations_path, 'r', encoding='utf-8') as file:
            content = file.read()
            matches = re.findall(r'"(.*?)"\s*=>\s*"(.*?)",?', content, re.DOTALL)
            existing_translations = dict(matches)
    return existing_translations

def update_translation_file(translations_path, new_entries):
    existing_translations = load_existing_translations(translations_path)
    # Merge dictionaries, existing translations take precedence
    merged_translations = {**new_entries, **existing_translations}
    # Write to the translation file
    with open(translations_path, 'w', encoding='utf-8') as file:
        file.write("<?php\n\nreturn [\n")
        for key, value in merged_translations.items():
            # Escape double quotes and backslashes
            escaped_value = value.replace('\\', '\\\\').replace('"', '\\"')
            file.write(f'    "{key}" => "{escaped_value}",\n')
        file.write("];\n")

def process_file(file_path, translations_path, translation_file_name, existing_translations, used_keys):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Pattern to match __() calls with string literals, possibly with additional arguments
    pattern = r'__\(\s*([\'"])(.+?)\1\s*(,.*?)?\)'
    matches = list(re.finditer(pattern, content, re.DOTALL))

    if not matches:
        return None, None

    new_entries = {}
    file_updated = False

    for match in matches:
        full_match = match.group(0)
        quote_type = match.group(1)
        original_text = match.group(2)
        additional_args = match.group(3) if match.group(3) else ''

        # Check if the original_text is already a key (contains a period between words with no spaces)
        if re.search(r'\w\.\w', original_text):
            # This is an existing key, skip processing
            continue

        print(f"\nFound translation string in {os.path.basename(file_path)}: \"{original_text}\"")
        default_key_base = generate_key(original_text)
        default_key = default_key_base
        index = 1
        # Ensure the default key is unique (without prefix)
        while default_key in used_keys or default_key in new_entries:
            default_key = f"{default_key_base}_{index}"
            index += 1

        # Prompt the user for a key, showing the default
        user_input = input(f"Enter a key (default: {default_key}): ").strip()
        key = user_input if user_input else default_key
        # Ensure the user-provided key is unique
        while key in used_keys or key in new_entries:
            print(f"The key '{key}' is already in use. Please enter a unique key.")
            key = input(f"Enter a unique key for \"{original_text}\": ").strip()
            if not key:
                key = default_key
        used_keys.add(key)
        new_entries[key] = original_text

        # Show status messages
        print(f"Updating '{original_text}' to '{translation_file_name}.{key}' in {os.path.basename(file_path)}")
        print(f"Adding '{translation_file_name}.{key}' key to {os.path.basename(translations_path)}")

        # Build the new __() call
        new_call = f'__("{translation_file_name}.{key}"{additional_args})'

        # Replace the original __() call in the content
        content = content.replace(full_match, new_call)
        file_updated = True

    # Write the updated content back to the file if changes were made
    if file_updated:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

    return new_entries, file_updated

def replace_translations(input_path, translations_path):
    # Extract the translation file name without extension to use as key prefix
    translation_file_name = os.path.splitext(os.path.basename(translations_path))[0]
    existing_translations = load_existing_translations(translations_path)
    used_keys = set(existing_translations.keys())
    all_new_entries = {}

    if os.path.isfile(input_path):
        new_entries, _ = process_file(input_path, translations_path, translation_file_name, existing_translations, used_keys)
        if new_entries:
            all_new_entries.update(new_entries)
    elif os.path.isdir(input_path):
        for root, _, files in os.walk(input_path):
            for file in files:
                if file.endswith(('.php', '.blade.php')):
                    file_path = os.path.join(root, file)
                    new_entries, _ = process_file(file_path, translations_path, translation_file_name, existing_translations, used_keys)
                    if new_entries:
                        all_new_entries.update(new_entries)
    else:
        print(f"The path {input_path} is neither a file nor a directory.")
        return

    if all_new_entries:
        # Update the translation file once with all new entries
        update_translation_file(translations_path, all_new_entries)
        print(f"\nTranslation keys have been updated in '{translations_path}'.")
    else:
        print("No new translation strings found.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python run-translation.py input_path translation_file")
        sys.exit(1)

    input_path = sys.argv[1]
    translation_file = sys.argv[2]

    replace_translations(input_path, translation_file)
