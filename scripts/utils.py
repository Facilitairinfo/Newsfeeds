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
    fallback_year_selector=None
):
    """
    Probeert een datumstring te parsen naar een datetime-object.
    - Kan direct een string krijgen via `date_str`.
    - Of zelf een element zoeken in `block` m.b.v. `date_selector`.
    - Optioneel kan `fallback_year_selector` gebruikt worden om ontbrekend jaar toe te voegen.

    Geeft None terug als er geen datum herkend wordt.
    """
    cleaned = None

    # 1. Als er direct een datumstring meegegeven wordt
    if date_str:
        cleaned = str(date_str).strip()

    # 2. Zo niet, probeer uit de HTML-block te halen met de selector
    elif block is not None and date_selector:
        el = block.select_one(date_selector)
        if el:
            cleaned = el.get_text(strip=True)

    if not cleaned:
        print(f"{Colors.WARNING}⚠ Geen datumstring ontvangen in parse_event_date{Colors.ENDC}")
        return None

    # 3. Bekende formaten eerst proberen
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d-%m-%y"):
        try:
            parsed = datetime.strptime(cleaned, fmt)
            print(f"{Colors.OKGREEN}✔ Parsed date '{cleaned}' → {parsed}{Colors.ENDC}")
            return parsed
        except ValueError:
            pass

    # 4. Met dateparser proberen
    parsed = dateparser.parse(cleaned)
    if parsed:
        print(f"{Colors.OKBLUE}ℹ Parsed with dateparser: '{cleaned}' → {parsed}{Colors.ENDC}")
    else:
        print(f"{Colors.WARNING}⚠ Kon datum niet parsen: '{cleaned}'{Colors.ENDC}")

    # 5. Indien jaar ontbreekt maar fallback_year_selector aanwezig is
    if not parsed and block is not None and fallback_year_selector:
        year_el = block.select_one(fallback_year_selector)
        if year_el:
            year_text = year_el.get_text(strip=True)
            candidate = f"{cleaned} {year_text}"
            parsed = dateparser.parse(candidate)
            if parsed:
                print(f"{Colors.OKBLUE}ℹ Parsed with fallback year: '{candidate}' → {parsed}{Colors.ENDC}")

    return parsed
