import traci

sumoCmd = ["sumo-gui", "-c", "try.sumocfg"]

traci.start(sumoCmd)

step = 0

while step < 100:

    traci.simulationStep()

    vehicles = traci.vehicle.getIDList()

    print("Vehicles:", vehicles)

    for veh in vehicles:
        speed = traci.vehicle.getSpeed(veh)
        print(f"{veh} speed = {speed}")

    step += 1

traci.close()