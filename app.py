import openai
import polib
import os
import json
import openai.error
import re
import time
import glob

# Attempt to import pyreadline3 (it provides a readline module on Windows)
try:
    import readline
except ImportError:
    print("Error: pyreadline3 not installed. Please install it using 'pip install pyreadline3'")
    readline = None

# Bind the TAB key to auto-completion if readline is available.
if readline:
    readline.parse_and_bind("tab: complete")

def complete_path(text, state):
    """
    Custom completer function that returns a list of file paths matching the given text.
    """
    matches = glob.glob(text + "*")
    try:
        return matches[state]
    except IndexError:
        return None

def input_with_path_completion(prompt_str):
    """
    Prompts the user for input with file path auto-completion enabled.
    Only active if pyreadline3 (readline) is available.
    """
    if readline:
        original_completer = readline.get_completer()
        readline.set_completer(complete_path)
    result = input(prompt_str)
    if readline:
        readline.set_completer(original_completer)
    return result

from dotenv import load_dotenv  # Used to load environment variables from a .env file

def clear_console():
    """
    Clears the console screen based on the operating system.
    On Windows, it calls 'cls'; on Unix-like systems, it calls 'clear'.
    """
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def format_elapsed_time(seconds):
    """
    Converts a duration in seconds into a formatted string displaying years, months, days, hours, minutes, and seconds.
    
    Parameters:
        seconds (float): The total number of seconds.
    
    Returns:
        str: A formatted string.
    """
    sec = int(seconds)
    # Define approximate conversion factors.
    seconds_per_year = 31536000  # 365 days
    seconds_per_month = 2592000  # 30 days
    seconds_per_day = 86400
    seconds_per_hour = 3600
    seconds_per_minute = 60

    years = sec // seconds_per_year
    sec %= seconds_per_year
    months = sec // seconds_per_month
    sec %= seconds_per_month
    days = sec // seconds_per_day
    sec %= seconds_per_day
    hours = sec // seconds_per_hour
    sec %= seconds_per_hour
    minutes = sec // seconds_per_minute
    sec %= seconds_per_minute

    parts = []
    if years:
        parts.append(f"{years} year{'s' if years != 1 else ''}")
    if months:
        parts.append(f"{months} month{'s' if months != 1 else ''}")
    if days:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    parts.append(f"{sec} second{'s' if sec != 1 else ''}")
    
    return ", ".join(parts)

def translate_string(text, target_language, context):
    """
    Translates the given text into the target language using the provided context.
    Measures the elapsed time for the API call but does not print it for each string.

    Parameters:
        text (str): The text to be translated.
        target_language (str): The language into which the text should be translated.
        context (str): The translation context to improve accuracy.

    Returns:
        str: The translated text. If an error occurs or the translation is invalid,
             the original text is returned.
    """
    prompt_text = (
        f"Translate the following text into {target_language} while considering the context '{context}', "
        "preserving the meaning and adapting when necessary without adding extra information:\n"
        f"Original text: {text}\n"
        "Translated text:"
    )
    start_time = time.time()
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt_text}],
            max_tokens=100,
            temperature=0.5,
        )
        translation = response.choices[0].message['content'].strip()
        # Do not print per-string translation time.
        if ("no need to be corrected" in translation.lower() or
            "reference to" in translation.lower() or
            re.match(r"^[^a-zA-Z]*$", translation)):
            print(f"Warning: Incorrect translation detected for '{text}'. Using the original text.")
            return text
        return translation
    except openai.error.RateLimitError:
        print("Error: OpenAI API rate limit reached. Please wait and try again later.")
        return text
    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return text

def load_progress(progress_path):
    """
    Loads the translation progress from a JSON file.

    Parameters:
        progress_path (str): The file path of the progress file.

    Returns:
        dict: The progress data loaded from the file, or an empty dictionary if the file does not exist.
    """
    if os.path.exists(progress_path):
        with open(progress_path, 'r') as file:
            return json.load(file)
    return {}

def save_progress(progress_path, current_index):
    """
    Saves the current translation progress (the index of the last processed entry) into a JSON file.

    Parameters:
        progress_path (str): The file path of the progress file.
        current_index (int): The index of the current translation progress.
    """
    with open(progress_path, 'w') as file:
        json.dump({"index": current_index}, file)

def main():
    """
    Main function that orchestrates the translation process.
    
    Workflow:
      1. Load environment variables from the .env file (expects only OPENAI_API_KEY).
      2. Prompt the user to input the target language, the translation context, and the file paths.
         File path inputs use auto-completion via pyreadline3.
      3. Clear the console for a clean display before starting the translation.
      4. Load the PO file (Portable Object file) using the 'polib' library.
      5. Determine the output file name for the translated file (using the '_translated' suffix).
      6. Load any existing progress from a progress file specific to the input PO file.
      7. Iterate over the PO file entries:
            - Skip entries that are comments or non-translatable.
            - For each translatable entry, if it has plural forms, translate each form separately.
            - Otherwise, translate the singular message.
      8. Save progress after each translated entry and update the PO file.
      9. Print the total translation time upon completion.
    """
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        print("Error: OPENAI_API_KEY not set in the environment.")
        return

    target_language = input("Enter the target language (e.g., 'English', 'Portuguese', 'Spanish'): ").strip()
    if not target_language:
        print("Error: target language must be specified.")
        return

    context = input("Enter the translation context: ").strip()
    if not context:
        print("Error: translation context must be specified.")
        return

    po_file_path = input_with_path_completion("Enter the path to the PO file: ").strip()
    if not os.path.exists(po_file_path):
        print(f"Error: The file '{po_file_path}' does not exist.")
        return

    progress_file_path = input_with_path_completion("Enter the path for the progress file (press Enter to use a file-specific progress file): ").strip()
    if not progress_file_path:
        base_name, _ = os.path.splitext(po_file_path)
        progress_file_path = f"{base_name}_progress.json"

    clear_console()

    po = polib.pofile(po_file_path)
    if po_file_path.endswith(".po"):
        translated_file_name = po_file_path.replace(".po", "_translated.po")
    else:
        translated_file_name = po_file_path + "_translated.po"

    progress = load_progress(progress_file_path)
    starting_index = progress.get("index", 0)
    overall_start_time = time.time()

    for i, entry in enumerate(po):
        if i < starting_index:
            continue
        if entry.msgid:
            if (entry.msgid.strip().startswith("#") or 
                re.match(r"^[^a-zA-Z]*$", entry.msgid) or 
                re.match(r"^%[a-zA-Z]*$", entry.msgid) or 
                not re.search(r"[a-zA-Z]", entry.msgid)):
                print(f"Skipping line {entry.linenum}: msgid: {entry.msgid} (non-translatable, comment, or placeholder).")
                continue
            print(f"Translating line {entry.linenum}: msgid: {entry.msgid}")
            if entry.msgid_plural:
                for idx in sorted(entry.msgstr_plural.keys()):
                    source_text = entry.msgid if idx == 0 else entry.msgid_plural
                    if source_text.strip().startswith("#"):
                        print(f"Skipping plural form [{idx}] for line {entry.linenum}: source text starts with '#'")
                        continue
                    print(f"Translating plural form [{idx}] for source: {source_text}")
                    new_translation = translate_string(source_text, target_language, context)
                    print(f"New translation for form [{idx}]: {new_translation}")
                    entry.msgstr_plural[idx] = new_translation
            else:
                new_translation = translate_string(entry.msgid, target_language, context)
                print(f"New translation: {new_translation}")
                entry.msgstr = new_translation
            save_progress(progress_file_path, i)
            po.save(translated_file_name)

    overall_elapsed = time.time() - overall_start_time
    formatted_time = format_elapsed_time(overall_elapsed)
    print(f"Translation and correction complete. File saved as '{translated_file_name}'.")
    print(f"Total translation time: {formatted_time}.")

if __name__ == "__main__":
    main()
