import math
import time
from dataclasses import dataclass
import pygame

from pythonosc import udp_client

client_osc = None
try:

    client_osc = udp_client.SimpleUDPClient("127.0.0.1", 8099)
except Exception as e:
    print(f"[Unreal Connect Error] {e}")
    exit(1)

AXIS_ALERON = 3
AXIS_ELEVATOR = 2
AXIS_RUDDER = 0
AXIS_THROTTLE = 1


pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No gamepad")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()

try:
    while True:
        # Odświeżenie zdarzeń pygame (wymagane, by pad nie "zasnął" lub nie zawiesił okna)
        pygame.event.pump()

        aileron = -joystick.get_axis(AXIS_ALERON)
        elevator = -joystick.get_axis(AXIS_ELEVATOR)
        rudder = -joystick.get_axis(AXIS_RUDDER)

        throttle_raw = joystick.get_axis(AXIS_THROTTLE)
        throttle = -1*throttle_raw

        buff = (f"{throttle:.1f};{aileron:.1f};{elevator:.1f};{rudder:.1f}")

        client_osc.send_message("/jsbsim-data-out", [f"{buff}"])

        # Uśpienie na 10 milisekund (100 odczytów na sekundę)
        time.sleep(0.03)

except KeyboardInterrupt:
    pass

finally:
    pygame.quit()