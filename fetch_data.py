import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


API_URL = (
    "https://clubconnector.sovd.cloud/api/anwesende/"
    "47fc873e-1bc1-431a-9111-e66d5abefa67-070367/23"
)

DATA_FILE = Path("data.json")
MAXIMUM_ANZAHL_MESSWERTE = 24 * 31
# 24 Messwerte pro Tag x 31 Tage = maximal ein Monat


def lade_bisherige_daten():
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as datei:
            daten = json.load(datei)

        if isinstance(daten, list):
            return daten

        return []

    except json.JSONDecodeError:
        return []


def frage_api_ab():
    request = urllib.request.Request(
        API_URL,
        headers={
            "Accept": "application/json",
            "User-Agent": "GitHub-Actions-Data-Agent"
        }
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main():
    api_daten = frage_api_ab()

    if "count" not in api_daten:
        raise ValueError("Die API-Antwort enthält keinen Wert 'count'.")

    if "maxCount" not in api_daten:
        raise ValueError("Die API-Antwort enthält keinen Wert 'maxCount'.")

    count = int(api_daten["count"])
    max_count = int(api_daten["maxCount"])

    jetzt = datetime.now(timezone.utc)

    neuer_messwert = {
        "timestamp": jetzt.isoformat(),
        "zeit": jetzt.strftime("%d.%m.%Y %H:%M"),
        "count": count,
        "maxCount": max_count
    }

    messwerte = lade_bisherige_daten()
    messwerte.append(neuer_messwert)

    # Nur die letzten Messwerte behalten
    messwerte = messwerte[-MAXIMUM_ANZAHL_MESSWERTE:]

    with DATA_FILE.open("w", encoding="utf-8") as datei:
        json.dump(
            messwerte,
            datei,
            ensure_ascii=False,
            indent=2
        )

    print(
        f"Messwert gespeichert: "
        f"count={count}, maxCount={max_count}, "
        f"Zeit={neuer_messwert['timestamp']}"
    )


if __name__ == "__main__":
    main()
