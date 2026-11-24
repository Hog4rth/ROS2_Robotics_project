# Copyright 1996-2024 Cyberbotics Ltd.
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
    """Imposta la posizione del sollevatore in metri."""
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


# Le lambda memorizzano le azioni senza eseguirle alla creazione.
# Le chiavi sono consecutive: da 0 a len(comportamenti) - 1.
# Ogni comportamento termina prima di passare al successivo.
comportamento_andata = {
    0: lambda: esegui_per(lift, 0.05, 1.0),
    1: lambda: esegui_per(moveFingers, 0.06, 1.0),
    2: lambda: esegui_per(moveForwards, 1.25, 2.0),
    3: lambda: stop(0.5),
    4: lambda: esegui_per(moveFingers, 0.01, 0.5),
    5: lambda: esegui_per(lift, 0.0, 0.5),
    6: lambda: esegui_per(turn, 2.0, 1.0),
    7: lambda: esegui_per(moveForwards, 1.25, 5.5),
    8: lambda: esegui_per(turn, -1.5, 1.5),
    9: lambda: stop(0.5),
    10: lambda: esegui_per(lift, 0.05, 0.5),
    11: lambda: esegui_per(moveFingers, 0.04, 0.5),
    12: lambda: stop(0.5),
}

comportamento_ritorno = {
    0: lambda: esegui_per(moveFingers, 0.01, 0.5),
    1: lambda: esegui_per(lift, 0.0, 0.5),
    2: lambda: esegui_per(turn, 1.5, 1.5),
    3: lambda: esegui_per(moveForwards, -1.25, 5.5),
    4: lambda: esegui_per(turn, -2.0, 1.0),
    5: lambda: stop(0.5),
    6: lambda: esegui_per(lift, 0.05, 0.5),
    7: lambda: esegui_per(moveFingers, 0.06, 0.5),
    8: lambda: esegui_per(moveForwards, -1.25, 2.0),
    9: lambda: stop(0.5),
}

# Lista dei dizionari nell'ordine di esecuzione
lista_comportamenti = [comportamento_andata, comportamento_ritorno]

if __name__ == "__main__":
    indice_dizionario = 0
    i = 0

    # Scorre prima tutti i passi del primo dizionario, poi quelli del secondo
    while robot.step(time_step) != -1:
        if indice_dizionario < len(lista_comportamenti):
            dizionario_corrente = lista_comportamenti[indice_dizionario]

            if i < len(dizionario_corrente):
                print(f"Eseguo dizionario {indice_dizionario}, passo {i}")
                dizionario_corrente[i]()
                i += 1
            else:
                # Passa al dizionario successivo e azzera il contatore dei passi
                indice_dizionario += 1
                i = 0

                if indice_dizionario == len(lista_comportamenti):
                    print("Sequenza completa (andata e ritorno) terminata.")
