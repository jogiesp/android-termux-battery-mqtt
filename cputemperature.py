import subprocess
import os
import re
import sys
import time

# =================================================================
#                         1. KONFIGURATION
#    DIESE WERTE MÜSSEN GEPRÜFT UND GEGEBENENFALLS ANGEPASST WERDEN!
# =================================================================

# 1. Der absolute Pfad zu mosquitto_pub 
#    (Löst den Fehler "Konnte 'mosquitto_pub' nicht finden.")
MOSQUITTO_PUB_PATH = "/usr/bin/mosquitto_pub" 

# 2. Deine Broker-IP und Port
#    (Löst den Fehler "Connection refused.")
BROKER_IP = "192.168.1xx.xx" # ANPASSEN!
BROKER_PORT = "1883" 

# 3. Das MQTT-Topic, an das gesendet werden soll
MQTT_TOPIC = "mydevices/laptop/cpu/temperature" # Topic angepasst

# =================================================================
#                     2. FUNKTIONEN ZUM AUSLESEN
# =================================================================

def get_cpu_temperature():
    """
    Liest die CPU-Temperatur (in Grad Celsius) aus /sys/class/thermal/temp aus.
    Der Wert wird typischerweise in Millicelsius angegeben und hier konvertiert.
    """
    # Dies ist der gängigste Pfad unter Linux für die primäre CPU-Temperaturzone
    temp_path = "/sys/class/thermal/thermal_zone0/temp"
    
    try:
        if not os.path.exists(temp_path):
            # Alternativer Versuch, falls thermal_zone0 nicht existiert (z.B. Raspberry Pi)
            temp_path = "/sys/class/thermal/thermal_zone1/temp" 
            if not os.path.exists(temp_path):
                 raise FileNotFoundError(f"Weder thermal_zone0 noch thermal_zone1 gefunden.")

        with open(temp_path, 'r') as f:
            # Der Wert wird in Millicelsius gelesen (z.B. 45000)
            temp_milli = f.read().strip()
            
            # Konvertierung zu Grad Celsius (z.B. 45.0)
            temperature_celsius = float(temp_milli) / 1000.0
            
            print(f"[INFO] CPU-Temperatur ermittelt: {temperature_celsius}°C (Quelle: {temp_path})")
            return round(temperature_celsius, 1)
            
    except FileNotFoundError as e:
        print(f"[FEHLER] Konnte die Temperaturdatei nicht finden. Pfad: {e}. Ist das 'sensors' Paket installiert?")
        return None
    except Exception as e:
        print(f"[FEHLER] Ein unerwarteter Fehler beim Auslesen der Temperatur trat auf: {e}")
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
            MOSQUITTO_PUB_PATH, # <-- WICHTIG: Der absolute Pfad!
            '-h', BROKER_IP,
            '-p', BROKER_PORT,
            '-t', MQTT_TOPIC,
            '-m', str(message), # Die Nachricht (CPU-Temperatur)
            '-q', '1',
            '-r' # Retain Flag: Behält den letzten Wert auf dem Broker
        ]

        # Führt den Befehl aus
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"[INFO] Erfolgreich gesendet: Topic='{MQTT_TOPIC}', Wert='{message}°C'")

    except FileNotFoundError:
        # Tritt auf, wenn MOSQUITTO_PUB_PATH falsch ist
        print(f"[FATALER FEHLER] Konnte '{MOSQUITTO_PUB_PATH}' nicht finden. Pfad überprüfen!")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        # Tritt auf, wenn mosquitto_pub einen Fehler meldet (z.B. Connection Refused)
        print("[FEHLER] Fehler beim Senden der MQTT-Nachricht (mosquitto_pub Fehlercode):")
        print(f"Befehl: {' '.join(command)}")
        print(f"STDERR: {e.stderr.strip()}")
        sys.exit(1)
    except Exception as e:
        print(f"[FEHLER] Ein unbekannter Fehler beim Senden trat auf: {e}")
        sys.exit(1)


# =================================================================
#                           4. HAUPTPROGRAMM
# =================================================================

if __name__ == "__main__":
    
    # Rufe die neue Funktion auf
    cpu_temp = get_cpu_temperature()

    if cpu_temp is not None:
        publish_mqtt(cpu_temp)
    else:
        print("[INFO] Skript beendet, da die CPU-Temperatur nicht ermittelt werden konnte.")