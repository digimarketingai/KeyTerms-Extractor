# 🔤 KeyTerms Extractor 術語提取器

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

### 📖 Description

KeyTerms Extractor is an AI-powered tool that automatically extracts key terms from any text and provides:
- **Bilingual translations** (English ↔ Traditional Chinese)
- **Clear definitions** in both languages
- **Term categorization** (technical, concept, proper noun, etc.)
- **Custom extraction filters** (focus on specific domains like medical, legal, technical, etc.)

### ✨ Features

- 🌐 **Bilingual Support**: English and Traditional Chinese translations
- 🎯 **Smart Extraction**: Automatically identifies important terminology
- 🔧 **Customizable**: Add custom prompts to filter by domain
- 📊 **Multiple Outputs**: Table, Markdown, JSON, CSV export
- 🚀 **Easy to Use**: Simple API and Gradio web interface
- ☁️ **Colab Ready**: Run directly in Google Colab

### 🚀 Quick Start

#### Option 1: Google Colab (Easiest)

```python
# Run in Google Colab
!pip install mistralai gradio -q

# Clone the repository
!git clone https://github.com/digimarketingai/KeyTerms-Extractor.git
%cd KeyTerms-Extractor

# Set your API key
import os
os.environ["MISTRAL_API_KEY"] = "your-api-key-here"

# Launch the Gradio interface
!python app.py
