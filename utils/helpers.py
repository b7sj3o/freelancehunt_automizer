from bs4 import BeautifulSoup


def remove_markup(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # замінюємо <br> на перенос
    for br in soup.find_all("br"):
        br.replace_with("\n")

    # замінюємо <p> на перенос (але зберігаємо текст)
    for p in soup.find_all("p"):
        p.insert_before("\n")
        p.unwrap()

    # забираємо чистий текст
    text = soup.get_text()

    # прибираємо зайві пробіли і багаторазові перенос
    lines = [line.strip() for line in text.splitlines()]
    text = "\n".join([line for line in lines if line])

    return text