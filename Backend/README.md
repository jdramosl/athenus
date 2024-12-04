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

### Develpment branch `dev`
- For the time being, backend code exists in `dev` branch.


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

- See what's in requirements
```txt
Django>=3.2.4,<3.3
djangorestframework>=3.12.4,<3.13
psycopg2>=2.8.6,<2.9
drf-spectacular>=0.15.1,<0.16
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

## Quick Commands
### Flake8
Flake8 is the code linting for python we have (only for dev)
```shell
docker-compose run --rm app sh -c "flake8"
```

### Kicking off project
```shell
docker-compose run --rm app sh -c "django-admin startproject app ." # Create in current directory
```

### Run App orchestrated
```shell
docker-compose up
```

### Create another project in Atenus backend
You can have segmented apps in django aside from the main one, in ur case "app"
```shell
docker-compose run --rm app sh -c "python manage.py startapp <name_of_app>"
```

- Example: user auth app:
```shell
docker-compose run --rm app sh -c "python manage.py startapp user"
```

### Create super user
- Helps with Django Admin
```shell
docker compose run --rm app sh -c "python manage.py createsuperuser"
```