from django.core.exceptions import ValidationError

def validate_file_size(file):
    max_size = 5 * 1024 * 1024  
    if file.size > max_size:
        raise ValidationError("O arquivo não pode ser maior que 5MB.")
    
def validate_file_extension(file):
    allowed_extensions = ['pdf', 'jpg', 'png', 'jpeg', 'webp']
    ext = file.name.split('.')[-1].lower()

    if ext not in allowed_extensions:
        raise ValidationError(
            f"Tipo de arquivo não permitido. Use: {', '.join(allowed_extensions)}"
        )
    