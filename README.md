# ERP-System
##Aufteilung
Lorenz 1 Einleitung 1.1 Problemstellung 1.2 Zielsetzung und Aufbau der Arbeit 2 Grundlagen 2.1 ERP-Systeme und Produktstammdaten 2.2 Barcodes und Produktidentifikation 2.3 Schnittstellen und Open-Food-Facts-API 

Leonard 3 Odoo als Systembasis 3.1 Produkt- und Lagerverwaltung in Odoo 3.2 Erweiterung durch ein Custom-Submodul 4 Konzeption und Umsetzung des Barcode-API-Submoduls 4.1 Anforderungen an das Submodul 4.2 Prozessablauf vom Barcode-Scan bis zum Produktdatensatz 4.3 API-Abfrage und Datenübernahme aus Open Food Facts 4.4 Automatische Produktanlage in Odoo 4.5 Integration in Lagerprozesse 

Zusammen 5 Analyse der Lösung 5.1 Vorteile gegenüber manueller Produktpflege 5.2 Grenzen, Fehlerfälle und Datenqualität 6 Fazit und Ausblick
## Projektbeschreibung

Automatisierte Warenverwaltung via Barcode-Scanning:

```
Barcode scannen
  → Produktdaten aus Open Food Facts API laden
  → Automatisch Produkt im ERP anlegen/aktualisieren
  → Lagerbestand synchronisieren
```

**MVP (Version 1):** Dieser Kern-Flow ist implementiert und lauffaehig.

## Neue Features

- **Custom App: Barcode OFF**
  - Eigener Menuepunkt in Odoo: `Barcode OFF -> Import Product`
  - Wizard fuer Barcode-Import mit Menge und Lagerort
- **Open Food Facts Integration mit Fallback**
  - API-Abruf ueber `v2` mit Fallback auf `v0`
  - User-Agent Header fuer stabile OFF-Anfragen
  - Barcode-Variantenlogik fuer 12/13-stellige Codes
- **Intelligente Produktanlage/-pflege**
  - Neue Produkte werden automatisch in Odoo angelegt
  - Bestehende Produkte werden anhand des Barcodes aktualisiert
  - Kategorie wird aus OFF-Tags uebernommen/neu angelegt
- **Erweitertes Daten-Mapping**
  - Name, interne Beschreibung und Verkaufsbeschreibung
  - Marke, Packungsmenge, Nutri-Score, NOVA-Gruppe
  - Logistikfelder (Gewicht/Volumen) aus OFF-Einheiten
  - Produktbild-Import (`image_1920`) von OFF
- **Optionale Bestandsbuchung**
  - Direkte Bestandsanpassung im gewaehlten internen Lagerort
- **Barcode-Scanner Integration**
  - USB-Scanner wird automatisch erkannt und befuellt das Barcode-Feld
  - Unterstuetzte Scanner: HID Keyboard Wedge Mode (Standardscanner)
- **Intelligente Fallback-Strategie**
  - Wenn OFF keinen Treffer liefert: automatisch Minimal-Produkt erstellen
  - Kein Fehler mehr bei unbekannten Barcodes
  - Benutzer kann Produktdaten nachtraeglich manuell ergaenzen

## Verwendete Module

- **Inventory** - Lagerverwaltung
- **Purchase** - Einkaufsmodul
- **Sales** - Verkaufsmodul
- **Community Barcode Modul** - Barcode-Integration

---

## Setup für Entwicklung

### Voraussetzungen

- **Python 3.12** (oder neuer)
- **PostgreSQL 12+** (bereits installiert unter `C:\Program Files\Odoo 19.0.20260318\PostgreSQL`)
- **Git**

### 1. Repository clonen / im Verzeichnis navigieren

```powershell
cd D:\ERP-System\odoo
```

### 2. Python Virtual Environment erstellen

```powershell
py -3.12 -m venv .venv
```

Falls `py -3.12` nicht funktioniert: Python 3.12 installieren (https://www.python.org/downloads/)

### 3. Dependencies installieren

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Hinweis:** Dauer ~3-5 Minuten, abhängig von Internetverbindung.

### 4. Konfiguration überprüfen

Die Datei `odoo/odoo.conf` sollte folgende Werte haben:

```ini
[options]
db_host = localhost
db_port = 5432
db_user = openpg
db_password = openpgpwd
http_interface = 127.0.0.1
http_port = 8069
addons_path = D:\ERP-System\odoo\addons
```

Falls nicht vorhanden, wird sie automatisch beim ersten Start erstellt.

### 5. Datenbank initialisieren (nur beim ersten Mal)

```powershell
cd D:\ERP-System\odoo
.\.venv\Scripts\python.exe odoo-bin -c odoo.conf -d erp_dev -i base --stop-after-init
```

Das installiert das base-Modul und erstellt alle notwendigen Tabellen. Dauer: ~30-60 Sekunden.

### 6. Odoo starten

```powershell
cd D:\ERP-System\odoo
.\.venv\Scripts\python.exe odoo-bin -c odoo.conf -d erp_dev
```

Expected Output:
```
INFO ? odoo: Odoo version 19.0
INFO ? odoo.service.server: HTTP service (werkzeug) running on ...8069
```

### 7. Im Browser öffnen

Navigiere zu: **http://127.0.0.1:8069**

- **Datenbank:** erp_dev
- **Email:** (siehe Setup-Dialog)
- **Passwort:** (siehe Setup-Dialog)

---

## Barcode OFF Feature nutzen

### Module aufgraden (nach Code-Aenderungen)

Wenn du die Scanner- oder Fallback-Features testen willst, fuehre das Upgrade aus:

```powershell
cd C:\playground\ERP\odoo
.\.\ venv\Scripts\python.exe odoo-bin -c odoo.conf -d erp_dev --http-port=8070 -u barcode_open_food_facts
```

### Scanner einrichten

1. **Scanner-Hardware vorbereiten**
   - Scanner muss im **HID Keyboard Wedge Mode** sein (Standardmodus)
   - Suffix sollte **Enter** oder **Tab** sein
   - Teste vorher in Editor/Notepad: Scanner-Input sollte Ziffern schreiben

2. **Im Wizard scannen**
   - Oeffne: **Barcode OFF > Import Product**
   - Klick in das Barcode-Feld
   - Barcode mit Scanner einscannen → Feld wird automatisch befuellt
   - Menge + Lagerort waehlen (optional)
   - **Import** klicken

### Fallback-Verhalten

Drei Szenarien beim Import:

| Szenario | Verhalten | Ergebnis |
|----------|-----------|----------|
| **OFF liefert Treffer** | Vollstaendiges Daten-Mapping | Produkt mit Name, Bild, Gewicht, Kategorie, etc. |
| **OFF: kein Treffer (Fallback)** | Minimal-Produkt wird erstellt | Produkt mit nur Barcode + "Unknown Product (XXXXX)" als Name|
| **Produkt existiert bereits** | Update mit neuen OFF-Daten | Nur neue Felder werden gefuellt, vorhandene bleiben erhalten |

**Fallback Erkennungszeichen:**
- Produktname: `Unknown Product (12345678901)`
- Interne Beschreibung: *"Automatically created because no Open Food Facts match was found."*

### Testbarcodes

Zum Testen kannst du diese gültigen OFF-Barcodes verwenden:

```
3017620422003  → Vodka
737628064502   → Wasser
5060292300396  → Kakaopuder
```

Und einen Fake-Barcode zum Fallback testen:
```
9999999999999  → loest Fallback aus
```

---

## PostgreSQL Zugangsdaten

- **Host:** localhost
- **Port:** 5432
- **User:** openpg
- **Passwort:** openpgpwd
- **Datenbank:** erp_dev

Falls du psql (Command-Line) nutzen möchtest:

```powershell
$env:PGPASSWORD='openpgpwd'; & "C:\Program Files\Odoo 19.0.20260318\PostgreSQL\bin\psql.exe" -U openpg -h localhost -p 5432 -d erp_dev
```

---

## Troubleshooting

### Problem: `py -3.12` nicht gefunden

**Lösung:** Python 3.12 installieren: https://www.python.org/downloads/

### Problem: PostgreSQL Verbindung schlägt fehl

**Lösung:** PostgreSQL-Dienst prüfen:
```powershell
Get-Service PostgreSQL_For_Odoo | Start-Service
```

### Problem: Port 8069 bereits in Verwendung

**Lösung:** In `odoo.conf` ändern:
```ini
http_port = 8070  # oder ein anderer freier Port
```

### Warnung: "Postgres version is 120004, lower than minimum required 130000"

Das ist ok für lokale Entwicklung. Für Production sollte PostgreSQL 13+ verwendet werden.

---

## Status und Naechste Schritte

### Erledigt (MVP v1.0)
- ✅ Barcode-Scanner Integration (HID Keyboard Wedge)
- ✅ Fallback-Strategie (Minimal-Produkt bei OFF-Treffer-Ausfall)
- ✅ Open Food Facts API mit v2→v0 Fallback
- ✅ Intelligentes Daten-Mapping (Name, Bild, Gewicht, Kategorie, Nutri-Score, etc.)
- ✅ Optionale Bestandsbuchung

### Geplant (nächste Iterationen)
1. **Auto-Import beim Scanner** (Enter drücken startet automatisch Import)
2. **Feld-Mapping erweitern** (Herkunft, Allergene, Naehrwertinfo)
3. **Strukturiertes Logging** (erfolgreiche Imports, Fallback-Rate, API-Performance)
4. **Benutzer-Feedback im Wizard** (Success/Warning-Messages nach Import)
5. **Automatisierte Tests** (Unit-Tests fuer OFF-API, Integration Tests fuer Wizard)
6. **Scanner-Konfiguration** (Scanner-Präfixe, Timeouts, optionales Beep)

---

## Hilfreiche Links

- Odoo Dokumentation: https://www.odoo.com/documentation/19.0/
- Odoo Developer Guide: https://www.odoo.com/documentation/19.0/developer/
- Open Food Facts API: https://world.openfoodfacts.org/data
