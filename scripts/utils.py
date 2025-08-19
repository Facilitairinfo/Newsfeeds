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
    block=None,
    date_str=None,
    date_selector=None,
    date_attr=None,
    month_selector=None,
    year_selector=None,
    fallback_year_selector=None
):
    """
    Probeert een datumstring te parsen naar een datetime-object.

    Werkt met:
    - Rechtstreeks meegegeven `date_str`
    - Een element opgehaald via `date_selector`
    - Of, als `date_attr` is opgegeven, de waarde van dat attribuut
    - Optioneel extra jaar via `fallback_year_selector`

    Onbekende extra parameters worden genegeerd, zodat oudere aanroepen compatibel blijven.
    """

    cleaned = None

    # 1. Direct aangeleverde string
    if date_str:
        cleaned = str(date_str).strip()

    # 2. Specifieke attribuutwaarde uit een element
    elif block is not None and date_selector and date_attr:
        el = block.select_one(date_selector)
        if el and el.has_attr(date_attr):
            cleaned = el[date_attr].strip()

    # 3. Tekstinhoud van een element
    elif block is not None and date_selector:
        el = block.select_one(date_selector)
        if el:
            cleaned = el.get_text(strip=True)

    if not cleaned:
        print(f"{Colors.WARNING}⚠ Geen datumstring ontvangen in parse_event_date{Colors.ENDC}")
        return None

    # 4. Bekende vaste formaten proberen
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d-%m-%y"):
        try:
            parsed = datetime.strptime(cleaned, fmt)
            print(f"{Colors.OKGREEN}✔ Parsed date '{cleaned}' → {parsed}{Colors.ENDC}")
            return parsed
        except ValueError:
            pass

    # 5. Dateparser fallback
    parsed = dateparser.parse(cleaned)
    if parsed:
        print(f"{Colors.OKBLUE}ℹ Parsed with dateparser: '{cleaned}' → {parsed}{Colors.ENDC}")
    else:
        print(f"{Colors.WARNING}⚠ Kon datum niet parsen: '{cleaned}'{Colors.ENDC}")

    # 6. Als geen jaar aanwezig is, fallback_year_selector proberen
    if not parsed and block is not None and fallback_year_selector:
        year_el = block.select_one(fallback_year_selector)
        if year_el:
            candidate = f"{cleaned} {year_el.get_text(strip=True)}"
            parsed = dateparser.parse(candidate)
            if parsed:
                print(f"{Colors.OKBLUE}ℹ Parsed with fallback year: '{candidate}' → {parsed}{Colors.ENDC}")

    return parsed
