from datetime import datetime
import dateparser

def parse_event_date(
    block=None,
    date_str=None,
    date_selector=None,
    date_attr=None,
    fallback_day_selector=None,
    fallback_month_selector=None,
    fallback_year_selector=None
):
    """
    Haalt een publicatiedatum uit HTML of string en zet die om naar datetime.

    Parameters:
        block: BeautifulSoup-element van het item.
        date_str: Direct aangeleverde datumstring.
        date_selector: CSS-selector voor element met datum.
        date_attr: Attribuutnaam (bijv. 'datetime') als datum in attribuut staat.
        fallback_day_selector / fallback_month_selector / fallback_year_selector:
            CSS-selectors voor losse dag-, maand- en jaarelementen.

    Returns:
        datetime.datetime of None
    """
    cleaned = None

    # 1. Rechtstreeks meegegeven string
    if date_str:
        cleaned = str(date_str).strip()

    # 2. Waarde uit attribuut
    elif block is not None and date_selector and date_attr:
        el = block.select_one(date_selector)
        if el and el.has_attr(date_attr):
            cleaned = el[date_attr].strip()

    # 3. Tekstinhoud uit element
    elif block is not None and date_selector:
        el = block.select_one(date_selector)
        if el:
            cleaned = el.get_text(strip=True)

    # 4. Samenvoegen losse dag/maand/jaar
    if not cleaned and block is not None and (
        fallback_day_selector or fallback_month_selector or fallback_year_selector
    ):
        parts = []
        for sel in (fallback_day_selector, fallback_month_selector, fallback_year_selector):
            if sel:
                el = block.select_one(sel)
                if el:
                    parts.append(el.get_text(strip=True))
        if parts:
            cleaned = " ".join(parts)

    if not cleaned:
        return None

    # 5. Bekende formaten proberen
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d-%m-%y"):
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            pass

    # 6. Laatste redmiddel: dateparser (herkent veel natuurlijke formaten)
    return dateparser.parse(cleaned)
