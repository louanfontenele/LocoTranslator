# 🌍 PO Translator for Loco Translate (WordPress) 🚀

A powerful Python script that **automates** the translation of **PO (Portable Object) files** using **OpenAI's GPT-3.5 Turbo model**. It is specially designed for translating **Loco Translate plugin files** for **WordPress** but works with **any PO file**.

📌 **GitHub Repository:** [LocoTranslator](https://github.com/louanfontenele/LocoTranslator)

---

## 🏆 Features

✅ **Automated Translation:**  
Uses OpenAI's AI model to provide **context-aware** translations for software and websites.

✅ **Supports Loco Translate (WordPress Plugin):**  
Easily translates `.po` files used in **Loco Translate**, one of the most popular WordPress translation plugins.

✅ **Handles Plural & Singular Forms:**  
Translates both **singular (`msgid`)** and **plural (`msgid_plural`)** entries properly.

✅ **Resumable Progress:**  
The script automatically saves translation progress in a **JSON file**, allowing users to **resume from where they left off**.

✅ **Cross-Platform Compatibility:**  
Works on **Windows, macOS, and Linux**.

✅ **Console Auto-Cleanup:**  
Clears the terminal screen before starting the translation to keep the **output clean and readable**.

✅ **TAB Auto-Completion:**  
Allows users to **quickly navigate file paths** using the **TAB** key (if supported by the system).

---

## 🛠️ Installation

### 1️⃣ **Clone the Repository**

```bash
git clone https://github.com/louanfontenele/LocoTranslator.git
cd LocoTranslator
```

### 2️⃣ **Create a Virtual Environment (Optional but Recommended)**

#### On macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

#### On Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ **Install Dependencies**

```bash
pip install -r requirements.txt
```

### 4️⃣ **Set Up Your OpenAI API Key**

- Create a `.env` file inside the project folder and add:

  ```env
  OPENAI_API_KEY=your_openai_api_key_here
  ```

- Replace `your_openai_api_key_here` with your actual **OpenAI API key**.  
  Get your API key from **[OpenAI's platform](https://platform.openai.com/account/api-keys)**.

---

## 🚀 How to Use

### 1️⃣ **Run the Script**

```bash
python app.py
```

### 2️⃣ **Follow the Interactive Prompts**

- **Target Language:** _(e.g., "English", "Spanish", "French", "Brazilian Portuguese")_
- **Translation Context:** _(Specify a context, e.g., "WordPress plugin interface", "E-commerce website")_
- **PO File Path:** _(Enter the path of the `.po` file you want to translate — TAB auto-completion is supported!)_
- **Progress File Path:** _(Optional: Specify a progress file; otherwise, it will generate one automatically.)_

### 3️⃣ **Translation Output**

- The translated PO file will be saved as:

  ```
  originalfile_translated.po
  ```

- Progress is saved in a file like:

  ```
  originalfile_progress.json
  ```

---

## 🔎 How It Works

### 🧹 **Console Clearing Before Translation**

- The script **automatically clears the terminal** before starting to ensure a **clean output**.
- It works on **Windows (`cls`)**, **macOS, and Linux (`clear`)**.

### 📝 **Handling PO File Entries**

- The script **reads** `.po` files and translates only the necessary parts.
- It **skips**:
  - **Comments (`#` lines)**
  - **Placeholders (`%` and special symbols)**
  - **Entries with no actual text**

### 🔀 **Singular & Plural Translations**

- **Singular (`msgid`)** is translated normally.
- **Plural (`msgid_plural`)** entries are **handled correctly** by translating each form separately.

### 🔄 **Progress Tracking**

- After **each translation**, the script **saves progress** in a JSON file.
- If interrupted, you can **resume** from where you left off!

---

## 🏗️ Example Use Case: Translating Loco Translate PO Files

Loco Translate is a **popular WordPress plugin** that **manages website translations**. This script **automates** the translation of `.po` files used by Loco Translate.

🔹 **Example PO File Entry Before Translation:**

```po
msgid "Add to Cart"
msgstr ""
```

🔹 **After Translation (to Spanish, for example):**

```po
msgid "Add to Cart"
msgstr "Añadir al carrito"
```

📌 **Learn more about Loco Translate:**  
🔗 [Loco Translate Plugin](https://wordpress.org/plugins/loco-translate/)

📌 **Official GitHub Repository:**  
🔗 [LocoTranslator GitHub](https://github.com/louanfontenele/LocoTranslator)

---

## 🖥️ Supported Platforms

✔️ **Windows:** Full support with Python. If **TAB auto-completion** doesn’t work, install `pyreadline`.  
✔️ **macOS & Linux:** Fully supported with Python and built-in terminal functionality.

---

## 🤝 Contributing

We welcome contributions! 🎉

### 📝 **How to Contribute:**

1. **Fork the Repository**
2. **Create a New Branch** (`feature-branch`)
3. **Make Your Changes**
4. **Submit a Pull Request (PR)**

For major changes, please open an **issue** first to discuss your idea.

---

## 📜 License

This project is licensed under the **GNU License**. See the [`LICENSE`](LICENSE) file for details.

---

## 🎯 Final Thoughts

This script is a **game-changer** for those working with **Loco Translate and WordPress translations**. It **saves time, improves accuracy, and automates** tedious translation work.

🚀 **Try it out today and make your translation process effortless!**
