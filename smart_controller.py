import traci
import random
import statistics

SUMO_BINARY = "sumo-gui"

sumoCmd = [
    SUMO_BINARY,
    "-c",
    "smart.sumocfg",
    "--start"
]

# -----------------------------
# START SUMO
# -----------------------------

traci.start(sumoCmd)

print("Simulation Started")

# -----------------------------
# DATA STORAGE
# -----------------------------

vehicle_wait_times = []
vehicle_speeds = []

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

def detect_congestion(edge_id):

    vehicle_number = traci.edge.getLastStepVehicleNumber(edge_id)

    mean_speed = traci.edge.getLastStepMeanSpeed(edge_id)

    if vehicle_number > 10 and mean_speed < 5:
        return True

    return False


def adaptive_traffic_light(tls_id):

    controlled_lanes = traci.trafficlight.getControlledLanes(tls_id)

    total_wait = 0

    for lane in controlled_lanes:
        total_wait += traci.lane.getWaitingTime(lane)

    current_phase = traci.trafficlight.getPhase(tls_id)

    # Increase green duration dynamically
    if total_wait > 100:
        traci.trafficlight.setPhaseDuration(tls_id, 40)

    else:
        traci.trafficlight.setPhaseDuration(tls_id, 15)


def reroute_vehicle(vehicle_id):

    try:
        traci.vehicle.rerouteTraveltime(vehicle_id)

    except:
        pass


# -----------------------------
# MAIN SIMULATION LOOP
# -----------------------------

step = 0

while step < 1000:

    traci.simulationStep()

    vehicles = traci.vehicle.getIDList()

    # -------------------------
    # VEHICLE ANALYTICS
    # -------------------------

    for veh in vehicles:

        speed = traci.vehicle.getSpeed(veh)

        wait = traci.vehicle.getWaitingTime(veh)

        vehicle_speeds.append(speed)

        vehicle_wait_times.append(wait)

        # Dynamic speed control
        if speed < 2:
            new_speed = random.uniform(5, 15)
            traci.vehicle.setSpeed(veh, new_speed)

    # -------------------------
    # CONGESTION DETECTION
    # -------------------------

    edges = traci.edge.getIDList()

    for edge in edges:

        if edge.startswith(":"):
            continue

        congested = detect_congestion(edge)

        if congested:

            print(f"[CONGESTION] Edge: {edge}")

            edge_vehicles = traci.edge.getLastStepVehicleIDs(edge)

            for veh in edge_vehicles:
                reroute_vehicle(veh)

    # -------------------------
    # SMART TRAFFIC LIGHTS
    # -------------------------

    tls_ids = traci.trafficlight.getIDList()

    for tls in tls_ids:
        adaptive_traffic_light(tls)

    # -------------------------
    # LIVE STATISTICS
    # -------------------------

    if step % 50 == 0:

        avg_speed = statistics.mean(vehicle_speeds) \
            if vehicle_speeds else 0

        avg_wait = statistics.mean(vehicle_wait_times) \
            if vehicle_wait_times else 0

        print("\n======================")
        print(f"STEP: {step}")
        print(f"Vehicles: {len(vehicles)}")
        print(f"Average Speed: {avg_speed:.2f}")
        print(f"Average Waiting: {avg_wait:.2f}")
        print("======================\n")

    step += 1

# -----------------------------
# CLOSE SIMULATION
# -----------------------------

traci.close()

print("Simulation Ended")