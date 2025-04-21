# Doplněk Google Kalendář pro Home Assistant

Tento doplněk zobrazí vaše události z Google kalendáře ve formě dlaždice v Home Assistantu.

## Instalace

1. Vytvořte vlastní složku `google_calendar_viewer` v `addons`
2. Nakopírujte všechny soubory do složky
3. Přidejte doplněk do Home Assistant přes Supervisor > Add-on store > 3 tečky > Vlastní repozitář

## Google API

- V Google Cloud Console vytvořte OAuth klienta (typ: desktop)
- Uložte `credentials.json` do `/config`
- Spusťte doplněk a dokončete přihlášení

## Funkce

- Načtení všech kalendářů
- Výběr, které zobrazit
- Přehled událostí
- Barvy pro každý kalendář
- Možnost úprav (brzy)
