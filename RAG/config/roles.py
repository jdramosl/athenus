ROLE_PDF_MAPPING = {
    "admin": ["rbf.pdf", "art1.pdf"],  # Admin has access to all PDFs
    "user": ["rbf.pdf"],                     # Regular users have limited access
    "guest": ["art2.pdf"]             # Guests have access to public docs only
}

DEFAULT_ROLE = "user"
