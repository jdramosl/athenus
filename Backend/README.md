# Athenus Backend

The backend for Athenus is built using **Django**, a powerful and versatile Python web framework. It serves as the backbone for managing business logic, API endpoints, and integration with the large language models (Ollama and Mistral) that power the chatbot functionality.

## Author

- Juanse

## Requirements

To set up and run the backend, ensure you have the following installed:
- Python 3.9 or higher
- pip
- Django 4.x or higher

## Getting Started

### 1. Go to backend and setup Python.
```bash
cd athenus-backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install
```bash
pip install -r requirements.txt
```

### 3. Project Structure

```bash
athenus-backend/
│
├── athenus/           # Django project configuration files
├── chatbot/           # App for managing chatbot APIs and logic
├── users/             # App for user authentication and management
├── requirements.txt   # List of Python dependencies
```