# **Tech Stack and Development Guidelines for ModernKataKupas**

Project: ModernKataKupas \- Rule-Based Indonesian Morphological Separator and Reconstructor  
Document Version: 1.1  
Date: May 21, 2025

## **1\. Core Language and Environment**

* **Primary Language: Python (Version 3.9+)**  
  * **Rationale:**  
    * Widely adopted in the NLP and Machine Learning community.  
    * Rich ecosystem of libraries for text processing, data handling, and scientific computing.  
    * Good balance of readability and performance for rule-based systems and potential integration with ML models.  
    * The original "Amien Separator" concept and PySastrawi are Python-based, allowing for easier integration or adaptation of existing components if desired.  
* **Virtual Environment Management: venv or conda**  
  * **Rationale:** Essential for managing project dependencies and ensuring reproducibility. venv is built-in, while conda offers more comprehensive package management. For a library, venv is often sufficient and lighter.

## **2\. Key Libraries and Modules**

* **Indonesian Stemmer (Underlying Component):**  
  * **PySastrawi (Forked/Adapted or as a dependency):**  
    * **Rationale:** Provides a solid, rule-based foundation for Indonesian stemming, a crucial step in the ModernKataKupas algorithm. The existing kata-dasar.txt and affix stripping logic can be leveraged or serve as a strong reference.  
    * **Consideration:** If significant modifications to the stemming logic or dictionary are needed beyond what PySastrawi's API allows, forking and adapting its relevant modules might be necessary. Otherwise, using it as a direct dependency is simpler.  
* **String Manipulation and Pattern Matching:**  
  * **re (Python's built-in regex module):**  
    * **Rationale:** Fundamental for defining and applying morphological rules, detecting affix patterns, and handling morphophonemic changes.  
* **String Alignment (for identifying affix candidates):**  
  * **Custom Implementation of Needleman-Wunsch (or similar sequence alignment algorithm):**  
    * **Rationale:** As per the original paper's approach, aligning the surface word form with its stemmed root is a key step to identify potential affix segments. A Python implementation will be needed.  
    * **Consideration:** Ensure the implementation is correct and reasonably efficient for word-length strings.  
* **Data Handling and Configuration:**  
  * **json or yaml (Python's built-in json module; PyYAML for YAML):**  
    * **Rationale:** For storing and loading the aturan\_afiks (affix rule repository) and potentially the augmented kamus\_dasar or loanword lists in a human-readable and structured format. JSON is simpler with built-in support; YAML can be more readable for complex nested structures.  
* **Testing Framework:**  
  * pytest (preferred) or unittest (Python's built-in):  
    * **Rationale:** Essential for creating comprehensive unit tests for each module (normalization, reduplication, affix stripping, reconstruction) and integration tests for the end-to-end segmentation/reconstruction process. pytest offers a more concise syntax and powerful features.  
* **Packaging and Distribution:**  
  * **setuptools** and wheel**:**  
    * **Rationale:** Standard for packaging Python libraries for distribution via PyPI.  
* **Optional (for advanced features or corpus analysis during development):**  
  * **NLTK or spaCy:** For sentence tokenization, POS tagging, or other linguistic analyses if needed for advanced rule conditions or dictionary building from corpora.  
  * **pandas:** For handling and analyzing word lists or frequency data during dictionary augmentation or rule refinement.

## **3\. Development Tools and Guidelines**

* **Version Control: Git**  
  * **Rationale:** Standard for source code management, collaboration, and tracking changes. Use a platform like GitHub, GitLab, or Bitbucket for hosting.  
* IDE/Editor: Any modern Python IDE or advanced text editor.  
  * Examples: VS Code (with Python extension), PyCharm, Sublime Text, etc.  
  * Rationale: Choose based on developer preference, ensuring good Python support, debugging capabilities, and integration with linters/formatters.  
* **Linters/Formatters:** Black, Flake8**, isort**  
  * **Rationale:** To ensure code quality, consistency, and adherence to Python style guides (PEP 8). Configure these to run automatically (e.g., on save or pre-commit).  
* Continuous Integration/Continuous Deployment (CI/CD) \- Optional but Recommended:  
  * Tools: GitHub Actions, GitLab CI/CD, Jenkins.  
  * Rationale: Automate testing, linting, and potentially packaging/releasing upon commits or merges.

### **3.1 Project Development Guidelines (Inspired by "Vibe Coding Rules" Concept)**

These guidelines should be documented within the project (e.g., in a CONTRIBUTING.md or a dedicated DEVELOPMENT\_GUIDELINES.md file within the memory-bank or project root) and consistently referred to during development, whether by human developers or AI coding assistants.

* G1: Always Reference Core Design Documents:  
  * Before writing or modifying any significant piece of code, the developer (human or AI) must consult:  
    * memory-bank/ModernKataKupas\_PRD\_v1.md (Product Requirement Document)  
    * memory-bank/tech-stack.md (This document)  
    * memory-bank/architecture.md (To be created; will document the high-level software architecture, file structures, and purpose of each module/class).  
    * Chapter 3 of the Research Paper Draft (ModernIndoSubword\_Paper\_Ch1-3\_vX.md) for detailed algorithmic logic.  
  * Rationale: Ensures development stays aligned with requirements, chosen technologies, and the intended software architecture.  
* G2: Prioritize Modularity and Single Responsibility:  
  * Code must be organized into multiple, well-defined Python modules and files.  
  * Each module/class/function should have a single, clear responsibility.  
  * Avoid monolithic files containing disparate logic.  
  * Rationale: Improves code readability, maintainability, testability, and reusability.  
* G3: Adhere to Python Best Practices and Style Guides:  
  * Follow PEP 8 for code style.  
  * Use linters (Flake8) and formatters (Black, isort) to enforce style.  
  * Write clear, concise, and well-commented code, especially for complex logic.  
  * Use meaningful variable and function names.  
  * Rationale: Enhances code quality and collaboration.  
* G4: Comprehensive Unit Testing:  
  * Every new function or module implementing core logic (especially for morphological rules, segmentation, reconstruction) must be accompanied by unit tests using pytest or unittest.  
  * Aim for high test coverage.  
  * Tests should cover normal cases, edge cases, and known problematic examples.  
  * Rationale: Ensures correctness, facilitates refactoring, and prevents regressions.  
* G5: Externalize Configuration and Data:  
  * Morphological rules (aturan\_afiks), root word dictionaries (kamus\_dasar), and loanword lists must be stored in external, structured files (JSON or YAML preferred) rather than being hardcoded.  
  * Rationale: Allows for easier updates, maintenance, and extension of linguistic resources without modifying the core Python code.  
* G6: Document Architectural Decisions:  
  * The memory-bank/architecture.md file must be updated whenever:  
    * A new module or significant class is added.  
    * The overall structure of the software changes.  
    * Key design decisions are made regarding data flow or component interaction.  
  * This document should explain the purpose of each major file/module and how they interact.  
  * Rationale: Maintains a clear understanding of the software's structure for current and future developers.  
* G7: Incremental Development and Validation:  
  * Follow the implementation-plan.md (to be created) step-by-step.  
  * Validate each step with its defined tests before proceeding to the next.  
  * Update memory-bank/progress.md after successfully completing and testing each step.  
  * Rationale: Ensures a structured development process and early detection of issues.  
* G8: Clear API Design:  
  * The public API of the ModernKataKupas library should be simple, intuitive, and well-documented (using docstrings).  
  * Focus on ease of use for the target users (researchers, developers).  
  * Rationale: Promotes adoption and effective use of the library.

## **4\. Rationale for Simplicity and Robustness (Overall Stack)**

The chosen stack and guidelines prioritize:

* **Leveraging Python's Strengths for NLP:** Python's extensive NLP libraries and ease of use for text manipulation make it the natural choice.  
* **Rule-Based Core:** The core logic is rule-based, minimizing dependencies on large pre-trained models or complex ML frameworks *for the separator itself*. This aligns with the goal of creating a tool that can function well in low-resource settings or as an interpretable component.  
* **Standard Libraries:** Using built-in modules (re, json, unittest) where possible reduces external dependencies.  
* Modularity and Maintainability: The emphasis on modular design, externalized rules/data, and comprehensive testing contributes to a robust and maintainable codebase.  
* **Extensibility:** Storing rules and dictionaries in external, structured files allows for easier updates and extensions without modifying the core codebase extensively.

This stack and set of guidelines provide a robust foundation for developing ModernKataKupas as a high-quality, maintainable, and effective Python library for Indonesian morphological analysis, irrespective of specific AI-assisted coding tools.