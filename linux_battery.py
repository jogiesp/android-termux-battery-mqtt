import subprocess
import os
import re
import sys

# =================================================================
#                         1. KONFIGURATION
#    DIESE DREI WERTE MUSST DU AN DEINE UMGEBUNG ANPASSEN!
# =================================================================

# 1. Der absolute Pfad zu mosquitto_pub (Typischerweise /usr/bin/mosquitto_pub)
#    (Löst den Fehler "Konnte 'mosquitto_pub' nicht finden.")
MOSQUITTO_PUB_PATH = "/usr/bin/mosquitto_pub" 

# 2. Deine Broker-IP und Port
#    (Löst den Fehler "Connection refused.")
BROKER_IP = "192.168.1xx.xx"
BROKER_PORT = "1883" 

# 3. Das MQTT-Topic, an das gesendet werden soll
MQTT_TOPIC = "jogi/laptop/battery/percent"

# =================================================================
#                     2. FUNKTIONEN ZUM AUSLESEN
# =================================================================

def get_battery_level():
    """
    Liest den aktuellen Batterieladestand in Prozent von /sys/class/power_supply aus.
    """
    try:
        # Pfad zum Akku-Status (kann variieren, oft BAT0 oder BAT1)
        # Wir suchen nach einem Verzeichnis, das mit 'BAT' beginnt
        battery_dir = next(d for d in os.listdir('/sys/class/power_supply/') if d.startswith('BAT'))
        status_path = f"/sys/class/power_supply/{battery_dir}/capacity"
        
        with open(status_path, 'r') as f:
            percent = f.read().strip()
            return int(percent)
            
    except StopIteration:
        print("Fehler: Konnte keinen Akku unter /sys/class/power_supply/ finden.")
        return None
    except FileNotFoundError:
        print(f"Fehler: Konnte die Kapazitätsdatei nicht finden ({status_path}).")
        return None
    except Exception as e:
        print(f"Ein unerwarteter Fehler beim Auslesen der Batterie trat auf: {e}")
        return None

# =================================================================
#                       3. MQTT-VERÖFFENTLICHUNG
# =================================================================

def publish_mqtt(message):
    """
    Sendet die Nachricht mit mosquitto_pub an den MQTT-Broker.
    """
    try:
        # Die Argumente für mosquitto_pub
        command = [
            MOSQUITTO_PUB_PATH, # Der absolute Pfad!
            '-h', BROKER_IP,
            '-p', BROKER_PORT,
            '-t', MQTT_TOPIC,
            '-m', str(message), # Die Nachricht (Batterieprozent)
            '-q', '1',
            '-r' # Retain Flag: Behält den letzten Wert auf dem Broker
        ]

        # Führt den Befehl aus
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"Erfolgreich gesendet: Topic='{MQTT_TOPIC}', Wert='{message}'")

    except FileNotFoundError:
        # Tritt auf, wenn MOSQUITTO_PUB_PATH falsch ist
        print(f"FATALER FEHLER: Konnte '{MOSQUITTO_PUB_PATH}' nicht finden.")
        print("Bitte prüfen Sie, ob der Pfad in der Konfiguration korrekt ist.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        # Tritt auf, wenn mosquitto_pub einen Fehler meldet (z.B. Connection Refused)
        print("Fehler beim Senden der MQTT-Nachricht (mosquitto_pub Fehlercode):")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"Ein unbekannter Fehler beim Senden trat auf: {e}")
        sys.exit(1)


# =================================================================
#                           4. HAUPTPROGRAMM
# =================================================================

if __name__ == "__main__":
    
    battery_percent = get_battery_level()

    if battery_percent is not None:
        publish_mqtt(battery_percent)
    else:
        print("Skript beendet, da der Batteriestand nicht ermittelt werden konnte.")