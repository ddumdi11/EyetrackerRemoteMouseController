# Eyetracker Remote Mouse Controller für Notebooks

🎯 **Status: Funktionsfähiger Prototyp verfügbar!** 

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-green.svg)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-red.svg)](https://mediapipe.dev/)

## Schnellstart

### Sofort testen (Basis-Prototyp):
```bash
# Repository klonen
git clone <REPO_URL>
cd EyetrackerRemoteMouseController

# Virtual Environment aktivieren und Dependencies installieren
.venv\Scripts\activate
pip install -r requirements.txt

# Basis-Prototyp starten (Kopfsteuerung)
python main.py
```

**Steuerung:** Bewegen Sie Ihren Kopf um die Maus zu steuern. Drücken Sie 'q' zum Beenden, 'c' zum Zentrieren.

---

## 1. Projektübersicht

Dieses Projekt zielt darauf ab, einen innovativen und ressourcenschonenden Eyetracker-RemoteMouse-Controller für Notebooks zu entwickeln. Das System ermöglicht die Steuerung des Mauszeigers und die Ausführung von Mausklicks ausschließlich durch Augen- und Kopfbewegungen, unter Verwendung der integrierten Webcam des Notebooks. Das ultimative Ziel ist es, die Abhängigkeit von physischen Mäusen oder Touchpads zu reduzieren oder ganz zu eliminieren und so eine intuitive, ermüdungsfreie Interaktion zu ermöglichen.

## 2. Kernfunktionen und Anforderungen

### 2.1 Start und Beenden des Programms

*   **Programmstart:** Das Hauptprogramm wird durch einen Doppelklick mit der rechten Maustaste (oder Touchpad-Taste) ausgelöst, unabhängig von der aktuellen Position des Mauszeigers.
*   **Automatisches Beenden:** Wenn der Mauszeiger eine einstellbare Zeit (Standard: 5-10 Sekunden) in seiner Ruheposition verweilt, ohne dass eine erkennbare Augenbewegung zur Mauszeigerverschiebung erfolgt, beendet sich das Programm automatisch. Es muss dann wie oben beschrieben neu gestartet werden.

### 2.2 Mauszeiger-Status und Visualisierung

*   **Ruheposition:** Nach dem Start des Programms oder nach jeder durchgeführten Aktion befindet sich der Mauszeiger in seiner vertikal und horizontal zentrierten Ruheposition in der Bildschirmmitte.
*   **Visuelle Rückmeldung:** In der Ruheposition ist der Mauszeiger deutlich sichtbar größer, um den aktiven Status des Eyetrackers zu signalisieren.
*   **Rückkehr in die Ruheposition:**
    *   Nach jeder erfolgreich ausgeführten Aktion (Mauszeiger verschoben und Trigger erkannt) kehrt der Mauszeiger sofort in seine Ruheposition zurück.
    *   Wenn länger als eine einstellbare Zeit (Standard: 1 Sekunde) kein Blick- oder Kopfbewegungsbefehl erfolgt, kehrt der Mauszeiger ebenfalls in seine Ruheposition zurück.

### 2.3 Mauszeiger-Steuerung durch Augenbewegung

*   **Bewegung aus der Ruheposition:** Wenn der Benutzer den zentrierten Mauszeiger mit den Augen fixiert und eine **annähernd lineare Augenbewegung** von der Bildschirmmitte weg ausführt, folgt der Mauszeiger dieser Bewegung. Kreiselnde, zick-zack- oder wellenförmige Augenbewegungen aus der Ruheposition heraus werden ignoriert, um unbeabsichtigte Bewegungen zu vermeiden.
*   **Fixierung und Halten:** Der Mauszeiger bleibt an der Stelle stehen, an die er verschoben wurde und wo der Benutzer ihn **länger als eine Sekunde ununterbrochen** (ohne Blinzeln) fixiert hat.
*   **Feinjustierung:** Nach der Erkennung einer annähernd linearen Bewegung und dem Erreichen der Zielregion ist für eine kurze, einstellbare Zeitspanne (Standard: 0.5 Sekunden) eine Feinjustierung des Mauszeigers durch subtile Augenbewegungen möglich, bevor die Position endgültig fixiert wird.

### 2.4 Aktionen und Trigger

*   **Aktionsausführung:** Sobald der Mauszeiger an einer gewünschten Position fixiert wurde, kann durch einen spezifischen Trigger eine Aktion ausgeführt werden.
*   **Beispiele für Trigger (erweiterbar):**
    *   **Kopfnicken:** Ein kurzes, klares Nicken mit dem Kopf.
    *   **Augen schließen:** Kurzes, vollständiges Schließen beider Augen.
*   **Standardaktion:** Die Standardaktion ist ein Doppelklick. Das System sollte jedoch erweiterbar sein, um andere Aktionen (z.B. Rechtsklick, Einzelklick, Scrollen) durch verschiedene Trigger oder Trigger-Kombinationen zu ermöglichen.

## 3. Technische Umsetzung

### 3.1 Verwendete Technologien (Vorschläge)

*   **Programmiersprache:** Python 3.8+ (breite Verfügbarkeit von ML- und CV-Bibliotheken)
*   **Computer Vision Stack:**
    *   **OpenCV** - Kamerazugriff und Bildverarbeitung
    *   **MediaPipe** - Hochperformante Gesichts- und Landmark-Detektion (468 Punkte)
    *   **NumPy** - Numerische Operationen und Datenverarbeitung
*   **Systemsteuerung:**
    *   **PyAutoGUI** - Maus-/Tastaturereignisse
    *   **Windows API (ctypes)** - Native Cursor-Kontrolle und visuelle Rückmeldung
*   **Konfiguration:** YAML-basierte Einstellungen mit JSON-Kalibrierungsdaten

### 3.2 Kalibrierung

*   **Notwendigkeit:** Eine präzise individuelle Kalibrierung ist entscheidend für die Genauigkeit des Eyetrackers.
*   **Kalibrierungsprogramm:** Es wird eine separate ausführbare Datei oder ein Skript (`calibration.exe` oder `calibrate.py`) bereitgestellt, das die Kalibrierungsdaten für das Hauptprogramm erzeugt und speichert.
*   **Initialisierung:** Beim ersten Start des Hauptprogramms prüft dieses, ob gültige Kalibrierungsdaten vorliegen.
    *   **Keine Daten:** Wenn keine Daten gefunden werden, wird der Benutzer entsprechend informiert (z.B. durch eine Meldung) und das Kalibrierungsprogramm wird automatisch gestartet.
    *   **Daten vorhanden:** Sind Daten vorhanden, wird das Hauptprogramm normal gestartet.
*   **Aktualisierung:** Die Kalibrierung sollte jederzeit über das dedizierte Kalibrierungsprogramm aktualisierbar sein.
*   **Kalibrierungsprozess:** Der Benutzer wird aufgefordert, verschiedene Punkte auf dem Bildschirm zu fixieren (z.B. ein 3x3-Raster), während die Blickrichtung erfasst wird, um eine individuelle Blickrichtungsmatrix oder ein Modell zu erstellen.

### 3.3 Architekturelle Überlegungen

*   **Modulare Struktur:** Das Projekt sollte modular aufgebaut sein, um eine einfache Erweiterung und Wartung zu ermöglichen (z.B. separate Module für Kamerazugriff, Gesichtserkennung, Blickrichtungsschätzung, Maussteuerung, Triggererkennung).
*   **Performance:** Besondere Aufmerksamkeit muss der Echtzeitverarbeitung und der Ressourcenschonung gewidmet werden, um eine flüssige Benutzererfahrung zu gewährleisten, auch auf weniger leistungsstarken Notebooks.
*   **Konfigurationsdateien:** Einstellbare Parameter (Timer für Inaktivität, Korrekturzeitraum, Triggerschwellenwerte) sollten in einer Konfigurationsdatei gespeichert werden, um eine einfache Anpassung durch den Benutzer zu ermöglichen.

## 4. Akzeptanzkriterien

*   Der Mauszeiger kann präzise und reaktionsschnell durch Augenbewegungen gesteuert werden.
*   Trigger (z.B. Kopfnicken, Augen schließen) werden zuverlässig erkannt und lösen die korrekten Aktionen aus.
*   Das Programm startet und beendet sich wie spezifiziert.
*   Die Kalibrierung ist einfach durchzuführen und speichert zuverlässig Benutzerdaten.
*   Die visuelle Rückmeldung des Mauszeigers ist klar und hilfreich.
*   Das System ist stabil und verursacht keine übermäßige CPU-/Batterielast bei normaler Nutzung.

## 5. Aktuelle Implementierung

### ✅ Implementierte Features (v1.0 Prototyp):
- **Basis-Kopfsteuerung** - Funktionsfähige Maussteuerung durch Kopfbewegungen
- **MediaPipe Integration** - Robuste Gesichtserkennung mit 468 Landmarks
- **Echtzeit-Performance** - Optimiert für 30+ FPS auf Standard-Hardware
- **Debug-Visualisierung** - Live-Feedback der Gesichtserkennung
- **Modulare Architektur** - Austauschbare Komponenten für einfache Erweiterung

### 🔄 In Entwicklung (v2.0):
- **3x3-Kalibrierungssystem** - Präzise individuelle Gaze-Estimation
- **Trigger-Erkennung** - Blinzeln und Kopfnicken für Aktionen
- **Erweiterte Maussteuerung** - Ruheposition, Auto-Return, vergrößerter Cursor
- **Konfigurationssystem** - YAML-basierte Einstellungen

### 🚀 Geplante Features (v3.0+):
- Echte Augenbewegungssteuerung (Eye-Tracking)
- Mehrere Aktionstypen (Rechts-/Linksklick, Scrollen)
- Multi-Monitor-Unterstützung
- GUI für Einstellungen
- Erweiterte Trigger-Kombinationen

---

## 6. Installation & Setup

### Voraussetzungen:
- Python 3.8 oder höher
- Webcam (integriert oder USB)
- Windows 10/11 (primär getestet)

### Installation:
```bash
# 1. Repository klonen
git clone https://github.com/yourusername/EyetrackerRemoteMouseController.git
cd EyetrackerRemoteMouseController

# 2. Virtual Environment erstellen
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Dependencies installieren
pip install -r requirements.txt

# 4. Basis-Prototyp testen
python main.py
```

### Troubleshooting:
- **Kamera nicht gefunden:** Prüfen Sie `config.yaml` → `camera.device_id`
- **Performance-Probleme:** Reduzieren Sie Auflösung in `config.yaml`
- **Windows Cursor-Probleme:** Programm als Administrator ausführen

---

## 7. GitHub Repository Setup

### Repository erstellen:
1. Auf GitHub neues Repository erstellen: `EyetrackerRemoteMouseController`
2. Local repository mit GitHub verbinden:

```bash
# Remote hinzufügen
git remote add origin https://github.com/yourusername/EyetrackerRemoteMouseController.git

# Ersten Push durchführen
git branch -M main
git push -u origin main
```

### Für Entwickler:
```bash
# Repository klonen und Setup
git clone https://github.com/yourusername/EyetrackerRemoteMouseController.git
cd EyetrackerRemoteMouseController

# Virtual Environment und Dependencies
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Development mit Debug-Logs
python main.py --log-level DEBUG
```

---

## 8. Projektstruktur

```
EyetrackerRemoteMouseController/
├── main.py                 # 🚀 Hauptanwendung (Prototyp)
├── eye_tracker.py          # 👁️ MediaPipe-basierte Gesichtserkennung
├── mouse_controller.py     # 🖱️ Windows-optimierte Maussteuerung
├── trigger_detector.py     # ⚡ Blinzel-/Kopfnicken-Erkennung
├── calibration.py          # 📐 3x3-Kalibrierungssystem
├── config.py              # ⚙️ YAML-Konfigurationsverwaltung
├── utils.py               # 🛠️ Performance-Monitoring & Utilities
├── requirements.txt       # 📦 Python-Dependencies
├── .gitignore            # 🚫 Git-Ignore-Regeln
├── CLAUDE.md             # 📖 Technische Dokumentation
└── README.md             # 📋 Diese Datei
```

---

## 9. Zukünftige Erweiterungen

*   **Präzisions-Verbesserungen:** Machine Learning für adaptive Kalibrierung
*   **Erweiterte Trigger:** Anpassbare Gesten für verschiedene Aktionen
*   **Cross-Platform:** Linux/macOS Unterstützung
*   **Accessibility Integration:** Windows Accessibility API
*   **Performance-Optimierung:** GPU-Acceleration für CV-Pipeline
*   **User Interface:** Electron-basierte Setup-/Konfigurations-GUI
