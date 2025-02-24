ROLE_PDF_MAPPING = {
    "contabilidad": ["Salarios.pdf"],  # Admin has access to all PDFs
    "admin": ["Salarios.pdf","tecnologias.pdf"],                     # Regular users have limited access
    "tecnologia": ["tecnologias.pdf"]             # Guests have access to public docs only
}

DEFAULT_ROLE = "tecnologia"
