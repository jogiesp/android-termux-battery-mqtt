import subprocess
import json
import paho.mqtt.client as mqtt
import time

broker = '192.168.178.37'
port = 1883

def format_value(value, max_chars=4):
    s = f"{value:.4g}"
    if len(s) > max_chars:
        s = s[:max_chars]
    return s

def send_battery_info():
    battery_json = subprocess.check_output(['termux-battery-status'])
    battery = json.loads(battery_json)

    current_uA = battery.get('current', 0)
    # Vorzeichen nicht umdrehen, so wie Ampere-App es liefert
    current_mA = round(current_uA / 1000, 2)

    temperature = battery.get('temperature', 0)
    percentage = battery.get('percentage', 0)

    formatted_values = {
        'health': battery.get('health', 'unbekannt'),
        'percentage': format_value(percentage),
        'plugged': battery.get('plugged', 'unbekannt'),
        'status': battery.get('status', 'unbekannt'),
        'temperature': format_value(temperature),
        'current_mA': format_value(current_mA)
    }

    client = mqtt.Client()
    try:
        client.connect(broker, port, 60)

        client.publish('tablet/battery_level', str(formatted_values['percentage']))
        client.publish('tablet/battery_temperature', str(formatted_values['temperature']))

        client.publish('tablet/battery_health', str(formatted_values['health']))
        client.publish('tablet/battery_plugged', str(formatted_values['plugged']))
        client.publish('tablet/battery_status', str(formatted_values['status']))
        client.publish('tablet/battery_current_mA', str(formatted_values['current_mA']))

        client.disconnect()

        print("Daten gesendet:", formatted_values)
    except Exception as e:
        print("Fehler bei MQTT-Verbindung:", e)

if __name__ == "__main__":
    while True:
        send_battery_info()
        time.sleep(30)
