def parse_title(html: str) -> str:
    marker = "<title>"
    end = "</title>"
    if marker not in html or end not in html:
        return ""
    return html.split(marker, 1)[1].split(end, 1)[0].strip()

