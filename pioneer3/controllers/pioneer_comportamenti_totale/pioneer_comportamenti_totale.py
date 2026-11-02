#FFFFFF# Copyright 1996-2024 Cyberbotics Ltd.
# Licensed under the Apache License, Version 2.0.
# https://www.apache.org/licenses/LICENSE-2.0
# Distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND.
# Adattamento Python del controller Pioneer3DX con pinza.

from controller import Robot


GRIPPER_MOTOR_MAX_SPEED = 0.1
robot = Robot()
time_step = int(robot.getBasicTimeStep())

lift_motor = robot.getDevice("lift motor")
finger_motor = robot.getDevice("finger motor::left")
left_wheel = robot.getDevice("left wheel")
right_wheel = robot.getDevice("right wheel")

# Ruote in controllo di velocita; pinza in controllo di posizione.
for motor in (left_wheel, right_wheel):
    motor.setPosition(float("inf"))
    motor.setVelocity(0.0)


def step(seconds):
    """Attende facendo avanzare la simulazione (non usa time.sleep)."""
    elapsed_time = 0
    while elapsed_time < seconds * 1000.0:
        if robot.step(time_step) == -1:
            raise SystemExit
        elapsed_time += time_step


def lift(position):
    """Imposta la posizione del sollevatore in metri, come nel codice C."""
    lift_motor.setVelocity(GRIPPER_MOTOR_MAX_SPEED)
    lift_motor.setPosition(position)


def moveFingers(position):
    """Imposta l'apertura della pinza in metri."""
    finger_motor.setVelocity(GRIPPER_MOTOR_MAX_SPEED)
    finger_motor.setPosition(position)


def moveForwards(speed):
    """Imposta la stessa velocita sulle due ruote, in rad/s."""
    left_wheel.setVelocity(speed)
    right_wheel.setVelocity(speed)


def turn(speed):
    """Ruota sul posto impostando velocita opposte sulle ruote."""
    left_wheel.setVelocity(speed)
    right_wheel.setVelocity(-speed)


def stop(seconds):
    """Ferma la base e attende il tempo indicato."""
    left_wheel.setVelocity(0.0)
    right_wheel.setVelocity(0.0)
    step(seconds)


def esegui_per(azione, valore, durata):
    """Applica un comando, attende e ferma la base al termine."""
    azione(valore)
    step(durata)
    stop(0.0)


# Le lambda memorizzano le azioni SENZA eseguirle durante la creazione
# della lista. Ogni voce e un comportamento selezionabile singolarmente.
# I comandi del main C sono riportati nello stesso ordine; le attese
# sono associate al comando. Ai primi due comandi, che nel C erano
# simultanei all'avanzamento, e assegnata un'attesa autonoma di 1 s.
# Questa lista serve a provare UN comportamento, non l'intera sequenza.
comportamenti = [
    lambda: esegui_per(lift, 0.05, 1.0),          #  0: sollevatore a 0.05 m
    lambda: esegui_per(moveFingers, 0.06, 1.0),   #  1: apre la pinza a 0.06 m
    lambda: esegui_per(moveForwards, 1.25, 2.0),  #  2: avanti per 2 s
    lambda: stop(0.5),                            #  3: stop per 0.5 s
    lambda: esegui_per(moveFingers, 0.01, 0.5),   #  4: chiude la pinza
    lambda: esegui_per(lift, 0.0, 0.5),           #  5: sollevatore a 0 m
    lambda: esegui_per(turn, 2.0, 1.0),           #  6: rotazione per 1 s
    lambda: esegui_per(moveForwards, 1.25, 5.5),  #  7: avanti per 5.5 s
    lambda: esegui_per(turn, -1.5, 1.5),          #  8: rotazione opposta per 1.5 s
    lambda: stop(0.5),                            #  9: stop per 0.5 s
    lambda: esegui_per(lift, 0.05, 0.5),          # 10: sollevatore a 0.05 m
    lambda: esegui_per(moveFingers, 0.04, 0.5),   # 11: apre la pinza a 0.04 m
    lambda: stop(0.5),                            # 12: stop finale
    
    
    lambda: esegui_per(moveFingers, 0.01, 0.5),   # 13: chiude la pinza
    lambda: esegui_per(lift, 0.0, 0.5),           # 14: sollevatore a 0 m
    lambda: esegui_per(turn, -2.1, 1.5),          # 15: rotazione opposta per 1.5 s
    lambda: stop(0.5),                            # 16: stop finale
    lambda: esegui_per(moveForwards, 1.25, 3.23), # 17: avanti per 3.23 s
    lambda: esegui_per(turn, 1.1, 1.5),           # 18: rotazione per 1.5 s
    lambda: esegui_per(lift, 0.05, 0.5),          # 19: sollevatore a 0.05 m
    lambda: esegui_per(moveFingers, 0.04, 0.5),   # 20: apre la pinza a 0.04 m
]


if __name__ == "__main__":
	# Esegue in ordine gli indici da 0 a len(comportamenti) -1
	for i in range(len(comportamenti)):
		print(f"Eseguo soltanto comportamenti[{i}]")
		comportamenti[i]()

	# Mantiene attivo Webots senza ripetere il comportamento.
	# Le ruote sono ferme; i motori della pinza mantengono il target.
	while robot.step(time_step) != -1:
		pass
