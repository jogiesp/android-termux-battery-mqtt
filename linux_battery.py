import json
import paho.mqtt.client as mqtt
import time
import os

# --- MQTT-Konfiguration ---
# HINWEIS: Bitte passe diese Werte an deinen MQTT-Broker an!
# Die IP-Adresse deines MQTT-Brokers.
broker = '192.168.xxx.xx'
# Der Port deines MQTT-Brokers. Standard ist 1883.
port = 1883

def get_battery_info_linux():
    """
    Ruft die Batteriestatusinformationen von einem Linux-System ab,
    indem die Dateien im sysfs-Dateisystem gelesen werden.
    """
    # Sucht nach dem ersten Batterieverzeichnis.
    battery_path = '/sys/class/power_supply/'
    batteries = [d for d in os.listdir(battery_path) if d.startswith('BAT')]
    if not batteries:
        raise FileNotFoundError("Keine Batterie gefunden unter /sys/class/power_supply/")

    # Verwendet die erste gefundene Batterie.
    battery_dir = os.path.join(battery_path, batteries[0])

    # Liest die Werte aus den Dateien.
    with open(os.path.join(battery_dir, 'capacity')) as f:
        percentage = int(f.read().strip())

    with open(os.path.join(battery_dir, 'status')) as f:
        status = f.read().strip()

    try:
        with open(os.path.join(battery_dir, 'temp')) as f:
            # Temperatur wird oft in Tausendstel Grad Celsius angegeben.
            temperature = int(f.read().strip()) / 1000
    except FileNotFoundError:
        # Einige Systeme melden keine Temperatur.
        temperature = 0

    return {
        'health': 'unbekannt',  # Nicht direkt aus sysfs abrufbar
        'percentage': percentage,
        'plugged': 'unbekannt', # Muss über 'status' abgeleitet werden
        'status': status,
        'temperature': temperature,
        'current_mA': 0  # Nicht direkt abrufbar
    }

def format_value(value, max_chars=4):
    """
    Formatiert einen numerischen Wert, um sicherzustellen, dass er nicht zu lang ist.
    Schneidet den Wert ab, wenn er die maximale Zeichenzahl überschreitet.
    """
    s = f"{value:.4g}"
    if len(s) > max_chars:
        s = s[:max_chars]
    return s

def send_battery_info():
    """
    Ruft die Batteriestatusinformationen ab, formatiert sie und sendet sie
    über MQTT an den Broker.
    """
    try:
        # Ruft die Batteriedaten für Linux ab.
        battery = get_battery_info_linux()

        formatted_values = {
            'health': battery.get('health', 'unbekannt'),
            'percentage': format_value(battery.get('percentage')),
            # Leitet den 'plugged' Status aus dem 'status' ab.
            'plugged': 'ja' if battery.get('status') in ['Charging', 'Full'] else 'nein',
            'status': battery.get('status', 'unbekannt'),
            'temperature': format_value(battery.get('temperature')),
            'current_mA': format_value(battery.get('current_mA'))
        }

        # Stellt eine Verbindung zum MQTT-Broker her.
        client = mqtt.Client()
        client.connect(broker, port, 60)

        # Veröffentlicht die Daten auf den entsprechenden MQTT-Themen.
        # Die Themen beginnen mit 'linux/', können aber angepasst werden.
        client.publish('linux/battery_level', str(formatted_values['percentage']))
        client.publish('linux/battery_temperature', str(formatted_values['temperature']))
        client.publish('linux/battery_health', str(formatted_values['health']))
        client.publish('linux/battery_plugged', str(formatted_values['plugged']))
        client.publish('linux/battery_status', str(formatted_values['status']))
        client.publish('linux/battery_current_mA', str(formatted_values['current_mA']))

        # Trennt die Verbindung zum Broker.
        client.disconnect()

        print("Daten gesendet:", formatted_values)

    except FileNotFoundError as e:
        print(f"Fehler: {e}. Konnte keine Batteriedaten finden. Läuft der Skript auf einem Laptop?")
    except Exception as e:
        print("Fehler bei MQTT-Verbindung oder Datenverarbeitung:", e)

if __name__ == "__main__":
    # Hauptprogramm, das die Funktion in einer Endlosschleife ausführt.
    while True:
        send_battery_info()
        # Wartet 30 Sekunden, bevor die Funktion erneut ausgeführt wird.
        # Du kannst diesen Wert an deine Bedürfnisse anpassen.
        time.sleep(30)
