 # Automated Metadata Extraction for Neuroscience Models using LLMs

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 Project Overview

This project develops an innovative pipeline that leverages Large Language Models (LLMs) to automatically extract metadata from computational neuroscience model **source code**. The system aims to enhance model discoverability and reusability in neuroscience research by automating the metadata annotation process.

### Key Features
- Automated metadata extraction using state-of-the-art LLMs
- Intelligent file screening and preprocessing pipeline
- High-quality classification for neuroscience model codes
- Comprehensive evaluation framework

## Tech Stack

- **Core Technologies**:
  - Python 3.8+
  - OpenAI GPT API
  - Azure Authentication
  - ModelDB API

- **Key Libraries**: Requirements are specified in `requirements.yml`

## Results & Impact

Our LLM-based approach has demonstrated significant improvements over traditional rule-based methods:

- Successfully automated metadata extraction from complex neuroscience model code
- Achieved higher precision and recall in identifying model applications compared to rule-based approaches
- Reduced manual effort in metadata assignment
- Enhanced accessibility of neuroscience models for researchers

## 🚀 Quick Start

1. **Setup Environment**:
   ```bash
   # Clone the repository
   git clone [repository-url]
   cd CodeAnalysis

   # Install dependencies
   pip install -e .
   ```

2. **Configuration**:
   - Ensure you have necessary API keys for OpenAI GPT
   - Configure Azure authentication if accessing OneDrive

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
