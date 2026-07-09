# ERP-System: Barcode-gestützte Produktverwaltung

## Projektbeschreibung

Automatisierte Warenverwaltung via Barcode-Scanning mit Integration von Open Food Facts:

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
- **PostgreSQL 13+** (wird mit Odoo mitgeliefert)
- **Git**
- **Windows PowerShell 5.1+**

### 1. Verzeichnis navigieren

```powershell
cd C:\playground\ERP\odoo
```

### 2. Python Virtual Environment erstellen (falls noch nicht vorhanden)

```powershell
py -3.12 -m venv .venv
```

Falls `py -3.12` nicht funktioniert: Python 3.12 installieren (https://www.python.org/downloads/)

### 3. Virtual Environment aktivieren

```powershell
.\.venv\Scripts\Activate.ps1
```

**Hinweis:** Falls ein ExecutionPolicy-Fehler auftritt:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

### 4. Python-Abhängigkeiten installieren

```powershell
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

**Zusatzpaket** (wegen `account_peppol` Abhängigkeit):

```powershell
python -m pip install phonenumbers
```

**Hinweis:** Dauer ~3-5 Minuten, abhängig von Internetverbindung.

### 5. Konfiguration überprüfen

Die Datei `odoo/odoo.conf` sollte folgende Werte haben:

```ini
[options]
admin_passwd = admin
db_host = localhost
db_port = 5432
db_user = openpg
db_password = openpgpwd
http_interface = 127.0.0.1
http_port = 8070
addons_path = C:\playground\ERP\odoo\addons
```

Falls nicht vorhanden, wird sie automatisch beim ersten Start erstellt.

### 6. Datenbank initialisieren (nur beim ersten Mal)

```powershell
python odoo-bin -c odoo.conf -d erp_dev -i base --stop-after-init
```

Das installiert das base-Modul und erstellt alle notwendigen Tabellen. Dauer: ~1-2 Minuten.

### 7. Odoo starten

```powershell
python odoo-bin -c odoo.conf -d erp_dev --http-port=8070
```

**⚠️ WICHTIG:** Vor dem Start die PowerShell-Umgebungsvariable `PGPASSWORD` leeren (falls gesetzt):

```powershell
Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
```

Expected Output:
```
INFO ? odoo: Odoo version 19.0
INFO ? odoo.service.server: HTTP service (werkzeug) running on http://127.0.0.1:8070
```

### 8. Im Browser öffnen

Navigiere zu: **http://127.0.0.1:8070**

Login-Daten siehe Setup-Dialog beim ersten Zugriff.

---

## Barcode OFF Feature nutzen

### Status: MVP implementiert

Das Custom-Addon `barcode_open_food_facts` ist derzeit nicht im Repository tracked (untracked local addon).  
Falls die Modul-Datei vorhanden ist, kann es mit folgendem Befehl aktualisiert werden:

### Modul aktualisieren (nach Code-Änderungen)

```powershell
python odoo-bin -c odoo.conf -d erp_dev --http-port=8070 -u barcode_open_food_facts
```

### Scanner einrichten

1. **Scanner-Hardware vorbereiten**
   - Scanner muss im **HID Keyboard Wedge Mode** sein (Standardmodus)
   - Suffix sollte **Enter** oder **Tab** sein
   - Teste vorher in Editor/Notepad: Scanner-Input sollte Ziffern schreiben

2. **Im Wizard scannen**
   - Odoo: **Barcode OFF → Import Product**
   - Klick in das Barcode-Feld
   - Barcode mit Scanner einscannen → Feld wird automatisch befüllt
   - Menge + Lagerort wählen (optional)
   - **Import** klicken

### Fallback-Verhalten

Drei Szenarien beim Import:

| Szenario | Verhalten | Ergebnis |
|----------|-----------|----------|
| **OFF liefert Treffer** | Vollständiges Daten-Mapping | Produkt mit Name, Bild, Gewicht, Kategorie, etc. |
| **OFF: kein Treffer (Fallback)** | Minimal-Produkt erstellen | Produkt mit Barcode + "Unknown Product (XXXXX)" als Name |
| **Produkt existiert bereits** | Update mit neuen OFF-Daten | Nur neue Felder werden gefüllt, vorhandene bleiben erhalten |

**Fallback Erkennungszeichen:**
- Produktname: `Unknown Product (12345678901)`
- Interne Beschreibung: *"Automatically created because no Open Food Facts match was found."*

### Testbarcodes

Gültige Open Food Facts Barcodes zum Testen:

```
3017620422003  → Vodka
737628064502   → Wasser
5060292300396  → Kakaopuder
```

Fake-Barcode zum Fallback testen:
```
9999999999999  → Fallback-Szenario
```

---

## Bekannte Probleme & Lösungen

### 🔧 UnicodeDecodeError bei DB-Verbindung

**Symptom:** `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xfc...`

**Ursache:** PowerShell-Umgebungsvariable `PGPASSWORD` überschreibt `db_password` aus `odoo.conf`.

**Lösung:** Vor Odoo-Start ausführen:

```powershell
Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
```

**Verifikation** (optional):

```powershell
python -c "import odoo; from odoo.tools import config; config.parse_config(['-c','odoo.conf','-d','erp_dev']); print(repr(config['db_password']))"
```

### 🔄 Port 8070 belegt

Wenn Port 8070 belegt ist: Port in `odoo.conf` ändern:

```ini
http_port = 8071  # oder ein anderer freier Port
```

### 📦 PostgreSQL Version

Lokal installiert: PostgreSQL 12.x  
Odoo 19 fordert: PostgreSQL 13+  
**Status:** Funktioniert lokal, für Produktion Upgrade auf PG 13+ empfohlen.

---

## PostgreSQL Zugangsdaten

- **Host:** localhost
- **Port:** 5432
- **User:** openpg
- **Passwort:** openpgpwd
- **Datenbank:** erp_dev

Falls psql (Command-Line) nutzen:

```powershell
$env:PGPASSWORD='openpgpwd'; psql -U openpg -h localhost -p 5432 -d erp_dev
```

---

## Arbeitsteilung (Abschlussarbeit)

### Lorenz
- Kapitel 1: Einleitung (Problemstellung, Zielsetzung)
- Kapitel 2: Grundlagen (ERP, Barcodes, Open Food Facts API)

### Leonard
- Kapitel 3: Odoo als Systembasis (Produkt-/Lagerverwaltung, Custom-Submodul)
- Kapitel 4: Konzeption & Umsetzung (Requirements, Prozessablauf, API-Integration, Produktanlage)

### Gemeinsam
- Kapitel 5: Analyse (Vorteile, Grenzen, Datenqualität)
- Kapitel 6: Fazit & Ausblick

- Odoo Dokumentation: https://www.odoo.com/documentation/19.0/
- Odoo Developer Guide: https://www.odoo.com/documentation/19.0/developer/
- Open Food Facts API: https://world.openfoodfacts.org/data
