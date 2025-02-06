import openai
import polib
import os
import json
import openai.error
import re
import time

# Try to import the readline module to enable TAB auto-completion in console inputs.
# This enhances the user experience on platforms that support it.
try:
    import readline
except ImportError:
    try:
        import pyreadline as readline  # Fallback for Windows if readline is not available.
    except ImportError:
        print("Warning: readline not available. Tab completion may not work.")

# Bind the TAB key to the auto-completion function (if supported by the environment).
readline.parse_and_bind('tab: complete')

from dotenv import load_dotenv  # Used to load environment variables from a .env file

def clear_console():
    """
    Clears the console screen based on the operating system.
    On Windows, it calls 'cls' and on Unix-like systems (macOS, Linux), it calls 'clear'.
    """
    if os.name == 'nt':  # If the OS is Windows
        os.system('cls')
    else:  # For macOS and Linux
        os.system('clear')

def translate_string(text, target_language, context):
    """
    Translates the given text into the target language using the provided context.
    Measures and prints the elapsed time for the API call.

    Parameters:
        text (str): The text to be translated.
        target_language (str): The language into which the text should be translated.
        context (str): The context for the translation to improve accuracy.

    Returns:
        str: The translated text. If an error occurs or the translation is invalid,
             the original text is returned.
    """
    # Construct the prompt for the OpenAI API including the target language and context.
    prompt = (
        f"Translate the following text into {target_language} while considering the context '{context}', "
        "preserving the meaning and adapting when necessary without adding extra information:\n"
        f"Original text: {text}\n"
        "Translated text:"
    )
    start_time = time.time()  # Record the start time for this translation call
    try:
        # Call the OpenAI ChatCompletion API with the constructed prompt.
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Specify the model to use
            messages=[{"role": "user", "content": prompt}],  # The API expects a list of message objects
            max_tokens=100,  # Limit the number of tokens in the output
            temperature=0.5,  # Control the randomness of the output
        )
        # Extract and clean the translation from the API response.
        translation = response.choices[0].message['content'].strip()
        elapsed_time = time.time() - start_time  # Calculate the elapsed time for this translation
        print(f"Translation took {elapsed_time:.2f} seconds.")
        
        # Check if the translation appears invalid (e.g., contains no letters or indicates no correction needed)
        if ("no need to be corrected" in translation.lower() or 
            "reference to" in translation.lower() or 
            re.match(r"^[^a-zA-Z]*$", translation)):
            print(f"Warning: Incorrect translation detected for '{text}'. Using the original text.")
            return text  # Return the original text if the translation is not acceptable
        return translation  # Return the valid translation
    except openai.error.RateLimitError:
        # Handle API rate limit errors by notifying the user and returning the original text.
        print("Error: OpenAI API rate limit reached. Please wait and try again later.")
        return text
    except openai.error.OpenAIError as e:
        # Handle any other API errors, display the error message, and return the original text.
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
    # Load environment variables from the .env file. Only OPENAI_API_KEY is expected.
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        print("Error: OPENAI_API_KEY not set in the environment.")
        return

    # Prompt the user for the target language (must be specified).
    target_language = input("Enter the target language (e.g., 'English', 'Portuguese', 'Spanish'): ").strip()
    if not target_language:
        print("Error: target language must be specified.")
        return

    # Prompt the user for the translation context (must be specified).
    context = input("Enter the translation context: ").strip()
    if not context:
        print("Error: translation context must be specified.")
        return

    # Prompt the user for the path to the PO file and verify that it exists.
    po_file_path = input("Enter the path to the PO file: ").strip()
    if not os.path.exists(po_file_path):
        print(f"Error: The file '{po_file_path}' does not exist.")
        return

    # Prompt the user for the progress file path.
    # If not provided, create a progress file based on the PO file name with a '_progress.json' suffix.
    progress_file_path = input("Enter the path for the progress file (press Enter to use a file-specific progress file): ").strip()
    if not progress_file_path:
        base_name, _ = os.path.splitext(po_file_path)
        progress_file_path = f"{base_name}_progress.json"

    # Clear the console to provide a clean display before starting the translation process.
    clear_console()

    # Load the PO file using the polib library.
    po = polib.pofile(po_file_path)

    # Generate the output file name for the translated file by replacing '.po' with '_translated.po'.
    if po_file_path.endswith(".po"):
        translated_file_name = po_file_path.replace(".po", "_translated.po")
    else:
        translated_file_name = po_file_path + "_translated.po"

    # Load any existing translation progress from the progress file.
    progress = load_progress(progress_file_path)
    starting_index = progress.get("index", 0)  # Resume from the last processed entry (default is 0)

    overall_start_time = time.time()  # Record the overall start time for the translation process

    # Iterate over each entry in the PO file, starting from the saved progress index.
    for i, entry in enumerate(po):
        if i < starting_index:
            continue  # Skip entries that have already been processed

        # Process only entries that have a message ID (msgid) to translate.
        if entry.msgid:
            # Skip entries where msgid starts with '#' (indicating a comment) or is non-translatable (e.g., placeholders).
            if (entry.msgid.strip().startswith("#") or 
                re.match(r"^[^a-zA-Z]*$", entry.msgid) or 
                re.match(r"^%[a-zA-Z]*$", entry.msgid) or 
                not re.search(r"[a-zA-Z]", entry.msgid)):
                print(f"Skipping line {entry.linenum}: msgid: {entry.msgid} (non-translatable, comment, or placeholder).")
                continue

            print(f"Translating line {entry.linenum}: msgid: {entry.msgid}")

            # Check if the entry contains plural forms.
            if entry.msgid_plural:
                # Iterate over each plural form translation.
                for idx in sorted(entry.msgstr_plural.keys()):
                    # For the singular form (index 0), use msgid; for other indexes, use msgid_plural.
                    source_text = entry.msgid if idx == 0 else entry.msgid_plural
                    # Skip the translation if the source text starts with '#' (indicating a comment).
                    if source_text.strip().startswith("#"):
                        print(f"Skipping plural form [{idx}] for line {entry.linenum}: source text starts with '#'")
                        continue
                    print(f"Translating plural form [{idx}] for source: {source_text}")
                    new_translation = translate_string(source_text, target_language, context)
                    print(f"New translation for form [{idx}]: {new_translation}")
                    entry.msgstr_plural[idx] = new_translation  # Update the plural translation
            else:
                # For singular entries, translate the msgid and store the result in msgstr.
                new_translation = translate_string(entry.msgid, target_language, context)
                print(f"New translation: {new_translation}")
                entry.msgstr = new_translation  # Update the singular translation

            # Save the current progress (the index of the last processed entry) to the progress file.
            save_progress(progress_file_path, i)
            # Save the updated PO file with the new translations.
            po.save(translated_file_name)

    overall_elapsed = time.time() - overall_start_time  # Calculate the total elapsed time for the process
    print(f"Translation and correction complete. File saved as '{translated_file_name}'.")
    print(f"Total translation time: {overall_elapsed:.2f} seconds.")

if __name__ == "__main__":
    main()  # Execute the main function when the script is run directly
