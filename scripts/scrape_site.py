published = parse_event_date(
    block,
    date_selector=site.get("date_selector"),
    date_attr=site.get("date_attr"),
    fallback_day_selector=site.get("fallback_day_selector"),
    fallback_month_selector=site.get("fallback_month_selector"),
    fallback_year_selector=site.get("fallback_year_selector")
)
