# **ModernKataKupas \- Indonesian Morphological Separator**

## **Overview**

ModernKataKupas is a Python library designed for the morphological separation of Indonesian words. It breaks down words into their constituent morphemes (root word, prefixes, suffixes, and reduplication markers). This rule-based tool aims to enhance Natural Language Processing (NLP) tasks, particularly for Large Language Models (LLMs) and applications in low-resource settings by providing linguistically informed sub-word units.

## **Current Status**

This project is under active development. Key implemented features include:

* Normalization of input words.  
* Segmentation of various prefix types:  
  * Simple prefixes (di-, ke-, se-).  
  * Complex prefixes with morphophonemic changes (meN-, peN-, ber-, ter-, per-).  
* Segmentation of suffixes:  
  * Particles (-lah, \-kah, \-pun).  
  * Possessive pronouns (-ku, \-mu, \-nya).  
  * Derivational suffixes (-kan, \-i, \-an).  
* Handling of layered affixes and confixes (e.g., ke-an, per-an, memper-kan).  
* Identification of full reduplication (Dwilingga, e.g., rumah-rumah, mobil-mobilan, bermain-main).  
* *Word reconstruction functionality is planned for a future update.*

## **Features**

* **Rule-Based Analysis:** Utilizes a comprehensive set of morphological rules for Indonesian.  
* **Morpheme Segmentation:** Identifies root words and affixes (prefixes, suffixes, particles, possessives).  
* **Handles Complex Morphology:**  
  * Allomorphic variations of prefixes (e.g., meN- becoming mem-, men-, meny-, etc.).  
  * Phonological adjustments/elisions at morpheme boundaries.  
  * Layered affixation (multiple prefixes and/or suffixes).  
  * Confixes (e.g., ke-an, per-an).  
* **Reduplication:** Detects full reduplication (Dwilingga), including affixed forms.  
* **Customizable Dictionary:** Allows loading of a custom root word dictionary.  
* **Extensible Rules:** Morphological rules are defined in an external JSON file for easier modification and extension.

## **Installation**

pip install modern\_kata\_kupas \# Placeholder for actual package name  
\# Or, for development:  
\# git clone \[https://github.com/neimasilk/modern\_kata\_kupas.git\](https://github.com/neimasilk/modern\_kata\_kupas.git) 
\# cd modern\_kata\_kupas  
\# pip install \-e .

Ensure you have Python 3.7+ installed.

## **Basic Usage**

from modern\_kata\_kupas import ModernKataKupas \# Ensure this import matches your \_\_init\_\_.py

\# Initialize the separator  
\# Optionally, provide paths to custom dictionary and rule files:  
\# separator \= ModernKataKupas(dictionary\_path="path/to/your/kata\_dasar.txt", rules\_file\_path="path/to/your/rules.json")  
separator \= ModernKataKupas()

\# Example 1: Simple Affixation  
result1 \= separator.segment("makanan")  
print(f"makanan \-\> {result1}") \# Expected: makan\~an

result2 \= separator.segment("dibaca")  
print(f"dibaca \-\> {result2}") \# Expected: di\~baca

\# Example 2: Complex Prefix (meN-)  
result3 \= separator.segment("memukul")  
print(f"memukul \-\> {result3}") \# Expected: meN\~pukul

result4 \= separator.segment("mengupas")  
print(f"mengupas \-\> {result4}") \# Expected: meN\~kupas

\# Example 3: Layered Affixes / Confix  
result5 \= separator.segment("keberhasilan")  
print(f"keberhasilan \-\> {result5}") \# Expected: ke\~ber\~hasil\~an

result6 \= separator.segment("mempertaruhkan")  
print(f"mempertaruhkan \-\> {result6}") \# Expected: meN\~per\~taruh\~kan

\# Example 4: Reduplication (Dwilingga)  
result7 \= separator.segment("rumah-rumah")  
print(f"rumah-rumah \-\> {result7}") \# Expected: rumah\~ulg

result8 \= separator.segment("mobil-mobilan")  
print(f"mobil-mobilan \-\> {result8}") \# Expected: mobil\~ulg\~an

result9 \= separator.segment("bermain-main")  
print(f"bermain-main \-\> {result9}") \# Expected: ber\~main\~ulg

\# Example 5: Word with particle and possessive  
result10 \= separator.segment("bukunyalah")  
print(f"bukunyalah \-\> {result10}") \# Expected: buku\~nya\~lah

## **Output Format**

The segment method returns a string where morphemes are separated by a tilde (\~). Canonical forms of affixes are used where appropriate (e.g., meN for its various allomorphs). Full reduplication (Dwilingga) is marked with \~ulg.

Examples:

* mempertaruhkan \-\> meN\~per\~taruh\~kan  
* buku-bukunya \-\> buku\~ulg\~nya  
* bermain-main \-\> ber\~main\~ulg

## **API Documentation**

### **ModernKataKupas Class**

The main class for morphological separation.

* \_\_init\_\_(self, dictionary\_path: Optional\[str\] \= None, rules\_file\_path: Optional\[str\] \= None)  
  * Initializes the separator.  
  * dictionary\_path (optional): Path to a custom root word dictionary file (UTF-8 encoded, one word per line). If not provided, a default dictionary is used.  
  * rules\_file\_path (optional): Path to a custom affix rules JSON file. If not provided, default rules are used.  
* segment(self, word: str) \-\> str:  
  * The primary method to separate an Indonesian word into its morphemes.  
  * Input: A single Indonesian word (string).  
  * Output: A string with morphemes separated by \~.  
* *reconstruct(self, segmented\_word: str) \-\> str: (To be added once implemented)*  
  * *Takes a tilde-separated morpheme string and reconstructs the original word.*

### **Exceptions**

All custom exceptions inherit from ModernKataKupasError. Key exceptions include:

* DictionaryError: Base class for dictionary-related errors.  
  * DictionaryFileNotFoundError: Raised if the dictionary file is not found.  
  * DictionaryLoadingError: Raised for errors during dictionary loading.  
* RuleError: For errors related to loading or applying morphological rules.  
* WordNotInDictionaryError: Raised when a word is expected in the dictionary but not found (usage context-dependent).  
* SeparationError: Raised for errors specifically during the separation process.  
* ReconstructionError: (Will be relevant when reconstruction is implemented) Raised for errors during word reconstruction.

## **Rules and Dictionary**

* **Root Word Dictionary:** A default list of Indonesian root words is included (typically located at src/modern\_kata\_kupas/data/kata\_dasar.txt within the package). You can provide your own dictionary file (UTF-8 encoded, one word per line) using the dictionary\_path parameter during ModernKataKupas initialization.  
* **Affix Rules:** Morphological rules are defined in a JSON file (typically src/modern\_kata\_kupas/data/affix\_rules.json within the package). This file specifies prefixes, suffixes, their allomorphs, and conditions for their application. You can supply a custom rules file using the rules\_file\_path parameter.

## **Contributing**

Contributions are welcome\! Please report issues, suggest features, or submit pull requests via the project's GitHub repository. (Replace with actual GitHub link when available).

Before contributing, please ensure your code adheres to formatting standards (e.g., using Black and Flake8 as defined in .pre-commit-config.yaml).

## **Future Work**

* Implementation of word reconstruction.  
* Handling of other reduplication types (Dwilingga Salin Suara, Dwipurwa).  
* Segmentation of loanword affixation.  
* Advanced ambiguity resolution.  
* Comprehensive benchmarking and performance optimization.

## **License**

MIT License
