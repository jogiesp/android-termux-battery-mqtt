import subprocess
import json
import paho.mqtt.client as mqtt
import time

# --- MQTT-Konfiguration ---
# HINWEIS: Bitte passe diese Werte an deinen MQTT-Broker an!
# Die IP-Adresse deines MQTT-Brokers.
broker = '192.168.xxx.xx' 
# Der Port deines MQTT-Brokers. Standard ist 1883.
port = 1883

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
        # Führt den Termux-Befehl aus, um Batteriedaten als JSON zu erhalten.
        # WICHTIG: Dies funktioniert nur in der Termux-App auf Android!
        battery_json = subprocess.check_output(['termux-battery-status'])
        battery = json.loads(battery_json)

        current_uA = battery.get('current', 0)
        # Konvertiert den Strom von Mikro-Ampere (uA) in Milli-Ampere (mA).
        current_mA = round(current_uA / 1000, 2)

        temperature = battery.get('temperature', 0)
        percentage = battery.get('percentage', 0)

        # Erstellt ein Wörterbuch mit den formatierten Werten.
        formatted_values = {
            'health': battery.get('health', 'unbekannt'),
            'percentage': format_value(percentage),
            'plugged': battery.get('plugged', 'unbekannt'),
            'status': battery.get('status', 'unbekannt'),
            'temperature': format_value(temperature),
            'current_mA': format_value(current_mA)
        }

        # Stellt eine Verbindung zum MQTT-Broker her.
        client = mqtt.Client()
        client.connect(broker, port, 60)

        # Veröffentlicht die Daten auf den entsprechenden MQTT-Themen.
        # Die Themen beginnen mit 'tablet/', können aber angepasst werden.
        client.publish('tablet/battery_level', str(formatted_values['percentage']))
        client.publish('tablet/battery_temperature', str(formatted_values['temperature']))
        client.publish('tablet/battery_health', str(formatted_values['health']))
        client.publish('tablet/battery_plugged', str(formatted_values['plugged']))
        client.publish('tablet/battery_status', str(formatted_values['status']))
        client.publish('tablet/battery_current_mA', str(formatted_values['current_mA']))

        # Trennt die Verbindung zum Broker.
        client.disconnect()

        print("Daten gesendet:", formatted_values)

    except FileNotFoundError:
        print("Fehler: 'termux-battery-status' wurde nicht gefunden. Stellen Sie sicher, dass Sie sich in Termux befinden und 'termux-api' installiert haben.")
    except Exception as e:
        print("Fehler bei MQTT-Verbindung oder Datenverarbeitung:", e)

if __name__ == "__main__":
    # Hauptprogramm, das die Funktion in einer Endlosschleife ausführt.
    while True:
        send_battery_info()
        # Wartet 30 Sekunden, bevor die Funktion erneut ausgeführt wird.
        # Du kannst diesen Wert an deine Bedürfnisse anpassen.
        time.sleep(30)
