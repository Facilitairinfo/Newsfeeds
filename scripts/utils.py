from datetime import datetime
import dateparser

def parse_event_date(date_str):
    """
    Probeert een datumstring te parsen naar een datetime-object.
    Ondersteunt meerdere formaten en fallback via dateparser.
    """
    if not date_str:
        return None

    # Probeer eerst een aantal veelvoorkomende formaten
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            pass

    # Fallback: gebruik dateparser (begrijpt ook '15 augustus 2025')
    dt = dateparser.parse(date_str)
    return dt

# Optioneel: kleuren voor logging, als je die in build-feed gebruikt
class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
