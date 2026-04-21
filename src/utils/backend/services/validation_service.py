def validate_file(rows):
    for r in rows:
        if not r:
            raise ValueError("Fichier vide ou invalide")