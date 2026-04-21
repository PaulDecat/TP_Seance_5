import csv

def parse_csv(file):
    try:
        decoded = file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded)
        return list(reader)
    except:
        raise ValueError("CSV invalide")