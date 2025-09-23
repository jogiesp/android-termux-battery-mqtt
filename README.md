# Termux MQTT Battery Monitor

Ein schlankes Python-Skript für Android-Geräte, das über Termux läuft und kontinuierlich Batterieinformationen (Ladezustand, Temperatur, Stromverbrauch) via MQTT an einen Broker sendet. Ideal für die Integration in Home-Assistant oder andere IoT-Systeme.

## 📱 Funktionen

- **Kontinuierliche Überwachung**: Sendet alle 30 Sekunden aktuelle Batteriedaten
- **MQTT-Integration**: Kompatibel mit Home Assistant und anderen MQTT-basierten Systemen
- **Umfassende Daten**: Batteriestand, Temperatur, Ladestatus, Gesundheit und Stromverbrauch
- **Hintergrund-Ausführung**: Läuft dauerhaft über tmux-Sessions
- **Ressourcenschonend**: Minimaler Einfluss auf die Geräteleistung

## 📋 Voraussetzungen

- **Android-Gerät**
- **Termux** - Terminal-Emulator für Android
- **MQTT-Broker** - lokal oder remote verfügbar
- **Netzwerkverbindung** - WLAN oder mobile Daten

## 🛠️ Installation

### 1. Termux aktualisieren und Pakete installieren

Führe in der Termux-Konsole die folgenden Befehle aus, um die erforderlichen Pakete zu installieren:

```bash
pkg update && pkg upgrade
pkg install python tmux git
pip install paho-mqtt

2. Termux-API App installieren

Installiere zusätzlich die Termux:API App aus dem F-Droid Store, um auf die Batteriedaten zugreifen zu können.

3. Projekt herunterladen

Klone das Repository auf dein Gerät oder erstelle die Datei manuell:
Bash

git clone https://github.com/jogiesp/termux-battery-mqtt
cd termux-battery-mqtt

⚙️ Konfiguration

MQTT-Broker einrichten

Passe die Broker-Einstellungen im Skript battery_monitor.py an:
Python

broker = '192.16x.1xx.xx'  # IP-Adresse deines MQTT-Brokers
port = 1883                # Standard MQTT-Port

MQTT-Topics

# MQTT-basierter Akku-Monitor

## Überblick

Dieses Skript ist für die Überwachung von Akku-Informationen konzipiert und sendet diese Daten an einen MQTT-Broker. Die gesammelten Daten umfassen den Ladestand, die Temperatur, den Zustand, den Ladezustand (ob angeschlossen), den Status und den Stromverbrauch in Milliampere (mA).

### MQTT-Topics

Das Skript veröffentlicht Daten auf den folgenden MQTT-Topics. Der erste Teil des Topic-Pfads, z. B. `tablet`,
kann direkt im Skript an deine Bedürfnisse angepasst werden, um es beispielsweise für ein Handy (`handy`) oder ein Android-Gerät (`android`) zu verwenden.

* `tablet/battery_level`
* `tablet/battery_temperature`
* `tablet/battery_health`
* `tablet/battery_plugged`
* `tablet/battery_status`
* `tablet/battery_current_mA`

---

## 🚀 Verwendung

### Hintergrund-Ausführung mit `tmux`

Um sicherzustellen, dass das Skript auch nach dem Beenden deiner Terminal-Sitzung weiterläuft,
ist die Verwendung von `tmux` eine hervorragende Methode.

1.  **Neue `tmux`-Session erstellen:**
    ```bash
    tmux new-session -d -s battery_monitor
    ```

2.  **In die Session wechseln und das Skript starten:**
    ```bash
    tmux attach-session -t battery_monitor
    python battery_monitor.py
    ```

3.  **Die Session verlassen (das Skript läuft weiter):**
    Drücke `Strg + B`, gefolgt von `D`.

---

## 🏠 Integrationen

### Home Assistant

Du kannst die Akku-Daten ganz einfach in Home Assistant integrieren,
indem du die folgenden Sensoren zu deiner `configuration.yaml`
Datei hinzufügst.

```yaml
mqtt:
  sensor:
    - name: "Tablet Battery Level"
      state_topic: "tablet/battery_level"
      unit_of_measurement: "%"
      device_class: battery
      
    - name: "Tablet Battery Temperature"
      state_topic: "tablet/battery_temperature"
      unit_of_measurement: "°C"
      device_class: temperature
      
    - name: "Tablet Battery Current"
      state_topic: "tablet/battery_current_mA"
      unit_of_measurement: "mA"
      icon: "mdi:current-dc"
      
    - name: "Tablet Battery Status"
      state_topic: "tablet/battery_status"
      icon: "mdi:battery-charging"
      
    - name: "Tablet Battery Health"
      state_topic: "tablet/battery_health"
      icon: "mdi:battery-heart"
      
    - name: "Tablet Battery Plugged"
      state_topic: "tablet/battery_plugged"
      icon: "mdi:power-plug"

🏠 ioBroker-Integration

ioBroker verwendet eine grafische Benutzeroberfläche zur Konfiguration, daher gibt es hier keine
Code-Blöcke zum Kopieren, wie sie bei Home Assistant verwendet werden. Stattdessen musst du den
MQTT-Adapter in ioBroker konfigurieren, um die Daten zu empfangen.

Schritt-für-Schritt-Anleitung

    MQTT-Adapter installieren:
    Navigiere in ioBroker zum Reiter "Adapter" und suche nach dem MQTT-Adapter. Klicke auf die
    Schaltfläche,um ihn zu installieren.

    Adapter-Instanz konfigurieren:
    Sobald die Installation abgeschlossen ist, klicke auf die Schaltfläche "Neue Instanz hinzufügen".
    Wähle in den Einstellungen "Client/subscriber" und gib die IP-Adresse und den Port deines
    MQTT-Brokers an, den du auch in deinem Python-Skript nutzt.

    Datenpunkte anzeigen:
    Sobald der Adapter läuft und das Skript Daten sendet, erstellt ioBroker automatisch Datenpunkte
    unter dem Objektbaum mqtt.0. Du kannst die Datenpunkte dann unter dem Reiter "Objekte" finden und
    in Visualisierungen, Skripten oder Automatisierungen verwenden.
