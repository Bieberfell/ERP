# ERP-System

## Projektbeschreibung

Automatisierte Warenverwaltung via Barcode-Scanning:

```
Barcode scannen
  → Produktdaten aus Open Food Facts API laden
  → Automatisch Produkt im ERP anlegen/aktualisieren
  → Lagerbestand synchronisieren
```

**MVP (Version 1):** Alleen dieser Flow wird implementiert.

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

## Nächste Schritte

1. **Custom-Addon erstellen** für Barcode + Open Food Facts Integration
2. **API-Client** zu Open Food Facts implementieren
3. **WebUI / Scanner-Integration** testen
4. **Tests** schreiben

---

## Hilfreiche Links

- Odoo Dokumentation: https://www.odoo.com/documentation/19.0/
- Odoo Developer Guide: https://www.odoo.com/documentation/19.0/developer/
- Open Food Facts API: https://world.openfoodfacts.org/data