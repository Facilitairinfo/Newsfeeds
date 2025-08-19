from datetime import datetime
import dateparser

class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

def parse_event_date(
    date_str=None,
    date_selector=None,
    month_selector=None,
    year_selector=None,
    fallback_year_selector=None
):
    """
    Probeert een datumstring te parsen naar een datetime-object.
    Ondersteunt meerdere formaten en fallback via dateparser.
    Alle extra parameters (selectors) worden genegeerd, maar zijn aanwezig
    om compatibel te blijven met bestaande code.
    """
    # Als er een directe datumstring is, probeer die te parsen
    if date_str:
        cleaned = str(date_str).strip()
        # Probeer bekende formaten
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
            try:
                parsed = datetime.strptime(cleaned, fmt)
                print(f"{Colors.OKGREEN}✔ Parsed date '{cleaned}' → {parsed}{Colors.ENDC}")
                return parsed
            except ValueError:
                pass

        # Fallback naar dateparser
        parsed = dateparser.parse(cleaned)
        if parsed:
            print(f"{Colors.OKBLUE}ℹ Parsed with dateparser: '{cleaned}' → {parsed}{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}⚠ Kon datum niet parsen: '{cleaned}'{Colors.ENDC}")
        return parsed

    # Geen date_str beschikbaar — hier kun je in de toekomst selector‑logica toevoegen
    print(f"{Colors.WARNING}⚠ Geen datumstring ontvangen in parse_event_date{Colors.ENDC}")
    return None
