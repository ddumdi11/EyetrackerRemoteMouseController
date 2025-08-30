# Eyetracker-RemoteMouse-Controller - Claude Development Guide

## Projektübersicht
Innovativer Eyetracker-RemoteMouse-Controller für Notebooks, der ausschließlich die integrierte Webcam nutzt.
Ermöglicht Maussteuerung durch Augen- und Kopfbewegungen ohne physische Maus/Touchpad.
**🎯 Ziel:** Intuitive, ermüdungsfreie Computer-Interaktion durch Blicksteuerung.

## Technische Anforderungen
- Python 3.8+ mit Computer Vision Bibliotheken
- OpenCV für Webcam-Zugriff und Bildverarbeitung
- Dlib für Gesichts- und Landmark-Detektion
- PyAutoGUI für Maus-/Tastatursteuerung
- Windows 11 kompatibel (primäres Zielssystem)

## Projektstruktur
```
EyetrackerRemoteMouseController/
├── main.py                  # Haupt-Eyetracker-Anwendung
├── calibration.py          # Kalibrierungsprogramm
├── eye_tracker.py          # Eye-Tracking-Engine (OpenCV + Dlib)
├── mouse_controller.py     # Maussteuerung und Cursor-Verwaltung
├── trigger_detector.py     # Trigger-Erkennung (Kopfnicken, Blinzeln)
├── config.py              # Konfiguration und Einstellungen
├── utils.py               # Hilfsfunktionen
├── requirements.txt       # Abhängigkeiten
├── README.md             # Benutzeranleitung
└── CLAUDE.md            # Diese Datei
```

## Entwicklungsrichtlinien
- **Performance-First**: Echtzeitverarbeitung bei niedriger CPU-Last
- **Windows-First**: Native Windows API Integration über ctypes
- **Robustheit**: Graceful Degradation bei schlechten Lichtverhältnissen
- **Modulares Design**: Austauschbare Komponenten für verschiedene Tracking-Algorithmen
- **Type Hints**: Für bessere Code-Qualität und Entwicklerfreundlichkeit
- **Logging**: Ausführliche Telemetrie für Debugging und Performance-Optimierung

## Core Features
1. **Program Lifecycle**: Rechts-Doppelklick Start → Auto-Stop nach Inaktivität
2. **Rest Position**: Zentrierte Cursor-Ruheposition mit visueller Vergrößerung
3. **Linear Eye Movement**: Erkennung bewusster linearer Augenbewegungen (keine Zick-Zack-Muster)
4. **Gaze Fixation**: Mindestens 1 Sekunde Fixierung für Positionsbestätigung
5. **Fine Adjustment**: 0.5s Feinjustierungs-Zeitfenster nach initialer Positionierung
6. **Trigger Detection**: Kopfnicken und Augenschließen für Aktionsauslösung
7. **Action Execution**: Standard-Doppelklick mit Erweiterbarkeit für weitere Aktionen
8. **Individual Calibration**: 3x3-Raster-Kalibrierung für präzise Blickrichtungsschätzung
9. **Visual Feedback**: Vergrößerter Cursor in Ruheposition als Aktivitätsindikator

## Computer Vision Pipeline
**Webcam-Zugriff:**
- OpenCV `cv2.VideoCapture(0)` für Kamera-Interface
- Optimale Auflösung: 640x480 oder 1280x720 je nach Hardware
- 30 FPS Ziel-Framerate für flüssige Reaktionen

**Gesichts- und Landmark-Detektion:**
- Dlib's `get_frontal_face_detector()` für Gesichtserkennung
- 68-Punkt Facial Landmark Modell für Augenpositionen
- Robuste Tracking-Algorithmen für Kopfbewegungen

**Blickrichtungsschätzung:**
- Pupillen-Zentrum-Extraktion aus Augen-ROI
- Kalibrierungsmatrix für Screen-zu-Gaze-Mapping
- Gleitender Durchschnitt zur Rauschunterdrückung
- Linear Movement Detection über Bewegungsvektor-Analyse

## Testing Approach
- **Hardware-Tests**: Verschiedene Webcam-Qualitäten und Beleuchtungsbedingungen
- **Präzisions-Tests**: Kalibrierungs-Genauigkeit über verschiedene Nutzerprofile
- **Performance-Tests**: CPU-Last und Reaktionszeit-Messungen
- **Robustheit**: Verhalten bei Gesichts-Verlust oder extremen Kopfbewegungen
- **Usability**: Ermüdungstests und Lernkurven-Analyse

## Deployment
- Standalone Python-Script für Entwicklung
- PyInstaller für .exe-Distribution mit allen Dependencies
- Installer mit automatischer Kalibrierungsroutine

## 🎯 Aktueller Status - Projektbeginn
- **Konzeptphase**: ✅ README.md und technische Spezifikation vollständig
- **CLAUDE.md**: ✅ Aktualisiert für Eyetracker-Projekt
- **Architektur**: ⏳ Modulares Design geplant
- **Dependencies**: ⏳ OpenCV + Dlib + PyAutoGUI Stack
- **Prototyp**: ⏳ Noch nicht implementiert

## 📋 Development Roadmap
**Phase 1 - Grundlagen (Proof of Concept)**
- ⏳ Webcam-Zugriff und Gesichtserkennung
- ⏳ Einfache Augenpunkt-Detektion
- ⏳ Basis-Maussteuerung ohne Kalibrierung
- ⏳ Primitive Trigger-Erkennung (Blinzeln)

**Phase 2 - Kalibrierung und Präzision**
- ⏳ 3x3-Raster-Kalibrierungssystem
- ⏳ Blickrichtungs-Mapping-Algorithmus
- ⏳ Lineare Bewegungserkennung
- ⏳ Feinjustierungs-Mechanismus

**Phase 3 - Produktionsreife**
- ⏳ Robuste Start/Stop-Mechanismen
- ⏳ Cursor-Visualisierung und Feedback
- ⏳ Konfigurierbare Timer und Schwellenwerte
- ⏳ Windows API Integration für Cursor-Kontrolle

**Phase 4 - Erweiterte Features**
- ⏳ Mehrere Trigger-Typen (Kopfnicken, Augenbewegungen)
- ⏳ Verschiedene Aktionstypen (Rechts-/Linksklick, Scrollen)
- ⏳ Multi-Monitor-Unterstützung
- ⏳ Benutzeroberfläche für Einstellungen

## Installation (Core Dependencies)
```bash
pip install opencv-python dlib pyautogui numpy
# Zusätzlich: dlib shape predictor model herunterladen
```

## 🎯 Kritische Erfolgsfaktoren
- **Kalibrierung**: Individuelle Anpassung ist absolut entscheidend
- **Performance**: <100ms Latenz für natürliche Interaktion
- **Robustheit**: Graceful Degradation bei Hardware-Problemen
- **Ergonomie**: Ermüdungsfreie Nutzung über längere Zeiträume

## 🔄 Benutzer-Workflow 
1. **Kalibrierung** → Einmalig 3x3-Raster-Setup durchführen
2. **Programmstart** → Rechts-Doppelklick aktiviert Eyetracker
3. **Blicksteuerung** → Lineare Augenbewegung von Bildschirmmitte
4. **Positionierung** → 1s Fixierung + 0.5s Feinjustierung
5. **Aktion** → Kopfnicken/Blinzeln für Doppelklick
6. **Auto-Ende** → Nach 5-10s Inaktivität automatischer Stop

## 🛠️ Kernkomponenten-Architektur

### Eye Tracker Engine
```python
class EyeTracker:
    def __init__(self):
        self.face_detector = dlib.get_frontal_face_detector()
        self.landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        
    def get_gaze_point(self, frame):
        # 1. Gesicht detektieren
        # 2. 68 Landmarks extrahieren
        # 3. Augen-ROI bestimmen
        # 4. Pupillen-Zentrum berechnen
        # 5. Kalibrierungsmatrix anwenden
        return screen_x, screen_y
```

### Mouse Controller
```python
class MouseController:
    def __init__(self):
        self.rest_position = (screen_width // 2, screen_height // 2)
        self.is_active = False
        
    def set_enlarged_cursor(self):
        # Windows API für vergrößerten Cursor
        
    def smooth_move_to(self, target_x, target_y):
        # Sanfte Bewegung zur Zielposition
        
    def return_to_rest(self):
        # Rückkehr zur Bildschirmmitte
```

### Linear Movement Detector
```python
class LinearMovementDetector:
    def is_linear_movement(self, gaze_points, threshold=0.15):
        # Analysiert Bewegungsvektor auf Linearität
        # Filtert Zick-Zack und kreiselnde Bewegungen
        # Retourniert True für bewusste Bewegungen
```

## 🚦 Technische Herausforderungen & Lösungsansätze

**Herausforderung 1: Beleuchtungsabhängigkeit**
- *Lösung*: Adaptive Schwellenwerte + Infrarot-Unterstützung falls verfügbar

**Herausforderung 2: Individuelle Kalibrierung**
- *Lösung*: Machine Learning für adaptive Verbesserung über Zeit

**Herausforderung 3: Performance vs. Genauigkeit**
- *Lösung*: Multi-Threading + optimierte OpenCV-Pipeline

**Herausforderung 4: Falsch-Positive bei Triggern**
- *Lösung*: Kombinierte Trigger + Confidence-Scoring