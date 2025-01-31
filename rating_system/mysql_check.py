import mysql.connector
from mysql.connector import Error
import json

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host='16.170.225.25',  # Replace with your host
            port=3306,             # Replace with your port
            user='root',           # Replace with your username
            password='1234',       # Replace with your password
            database='iot_system'  # Replace with your database name
        )

        if connection.is_connected():
            print("Connected to the database")
            return connection
    except Error as e:
        print(f"Error while connecting to database: {e}")
        return None

def process_experiments():
    connection = connect_to_database()
    if not connection:
        return

    try:
        cursor = connection.cursor(dictionary=True)

        # Fetch all data from the experiments table
        cursor.execute("SELECT * FROM experiments")
        experiments = cursor.fetchall()

        for experiment in experiments:
            experiment_id = experiment['experiments_id']
            protocol_experiment_id = experiment['protocol_experiments_id']
            computing_experiment_id = experiment['computing_experiments_id']
            used_devices_id = json.loads(experiment['used_devices_id'])

            sensor_ids = set()
            usage_ids_from_sensors = set()
            usage_ids_from_protocol = set()
            max_range = -1
            experiments_max_nodes = -1

            interface_types = set()
            power_supply_modes = set()
            experiment_cost = 0  # Initialize cost

            # Process used_devices_id for sensor-based usage scenarios
            for device_id in used_devices_id:
                cursor.execute(
                    "SELECT sensor_id FROM sensor_device_mapping WHERE m_id = %s",
                    (device_id,)
                )
                sensors = cursor.fetchall()
                for sensor in sensors:
                    sensor_ids.add(sensor['sensor_id'])

                # Process interfaces for the device
                cursor.execute(
                    "SELECT interface_id FROM interface_device_mapping WHERE m_id = %s",
                    (device_id,)
                )
                interfaces = cursor.fetchall()
                for interface in interfaces:
                    cursor.execute(
                        "SELECT interface_type FROM interface_type WHERE interface_id = %s",
                        (interface['interface_id'],)
                    )
                    interface_type = cursor.fetchone()
                    if interface_type:
                        interface_types.add(interface_type['interface_type'])

                # Process power supply for the device
                cursor.execute(
                    "SELECT power_id FROM power_supply_device_mapping WHERE m_id = %s",
                    (device_id,)
                )
                power_supplies = cursor.fetchall()
                for power_supply in power_supplies:
                    cursor.execute(
                        "SELECT power_supply_mode FROM power_supply WHERE power_id = %s",
                        (power_supply['power_id'],)
                    )
                    power_mode = cursor.fetchone()
                    if power_mode:
                        power_supply_modes.add(power_mode['power_supply_mode'])

                # Fetch device cost from devices table
                cursor.execute(
                    "SELECT price FROM devices WHERE m_id = %s",
                    (device_id,)
                )
                device_cost = cursor.fetchone()
                if device_cost:
                    experiment_cost += device_cost['price']

            for sensor_id in sensor_ids:
                cursor.execute(
                    "SELECT usage_id FROM sensor_usage_mapping WHERE sensor_id = %s",
                    (sensor_id,)
                )
                usages = cursor.fetchall()
                for usage in usages:
                    usage_ids_from_sensors.add(usage['usage_id'])

            # Process protocol_experiment_id for protocol-based usage scenarios
            cursor.execute(
                "SELECT used_protocol_id FROM protocol_experiments WHERE protocol_experiments_id = %s",
                (protocol_experiment_id,)
            )
            protocol_experiment = cursor.fetchone()
            if protocol_experiment:
                used_protocol_ids = json.loads(protocol_experiment['used_protocol_id'])
                for protocol_id in used_protocol_ids:
                    # Fetch range and max_nodes for each protocol
                    cursor.execute(
                        "SELECT range_m, max_nodes FROM protocol WHERE protocol_id = %s",
                        (protocol_id,)
                    )
                    protocol_data = cursor.fetchone()
                    if protocol_data:
                        max_range = max(max_range, protocol_data['range_m'])
                        if experiments_max_nodes == -1:
                            experiments_max_nodes = protocol_data['max_nodes']

                    # Fetch usage scenarios for protocols
                    cursor.execute(
                        "SELECT usage_id FROM protocol_usage_scenario_mapping WHERE protocol_id = %s",
                        (protocol_id,)
                    )
                    protocol_usages = cursor.fetchall()
                    for protocol_usage in protocol_usages:
                        usage_ids_from_protocol.add(protocol_usage['usage_id'])

            # Fetch computing_experiments metrics
            cursor.execute(
                "SELECT * FROM computing_experiments WHERE computing_experiments_id = %s",
                (computing_experiment_id,)
            )
            computing_metrics = cursor.fetchone()

            # Fetch protocol_experiments metrics
            cursor.execute(
                "SELECT latency, error_rate, stability FROM protocol_experiments WHERE protocol_experiments_id = %s",
                (protocol_experiment_id,)
            )
            protocol_metrics = cursor.fetchone()

            # Fetch usage scenario names for sensor usage scenarios
            sensor_usage_scenario_names = []
            for usage_id in usage_ids_from_sensors:
                cursor.execute(
                    "SELECT usage_scenario FROM usage_scenario WHERE usage_id = %s",
                    (usage_id,)
                )
                usage = cursor.fetchone()
                if usage:
                    sensor_usage_scenario_names.append(usage['usage_scenario'])

            # Fetch usage scenario names for protocol usage scenarios
            protocol_usage_scenario_names = []
            for usage_id in usage_ids_from_protocol:
                cursor.execute(
                    "SELECT usage_scenario FROM usage_scenario WHERE usage_id = %s",
                    (usage_id,)
                )
                usage = cursor.fetchone()
                if usage:
                    protocol_usage_scenario_names.append(usage['usage_scenario'])

            # Record and print results
            sensor_scenario_count = len(usage_ids_from_sensors)
            protocol_scenario_count = len(usage_ids_from_protocol)
            total_interfaces_count = len(interface_types)
            total_power_supply_count = len(power_supply_modes)

            print(f"Experiment ID: {experiment_id}")
            print(f"Sensor Usage Scenarios: {sensor_usage_scenario_names}")
            print(f"Protocol Usage Scenarios: {protocol_usage_scenario_names}")
            print(f"Sensor Scenario Count: {sensor_scenario_count}")
            print(f"Protocol Scenario Count: {protocol_scenario_count}")
            print(f"Experiment Range (Max Range): {max_range}")
            print(f"Experiment Max Nodes (First Max Nodes): {experiments_max_nodes}")
            print(f"Interface Types: {list(interface_types)}")
            print(f"Total Interfaces Count: {total_interfaces_count}")
            print(f"Power Supply Modes: {list(power_supply_modes)}")
            print(f"Total Power Supply Count: {total_power_supply_count}")
            if computing_metrics:
                print(f"Computing Metrics: {computing_metrics}")
            if protocol_metrics:
                print(f"Protocol Metrics: {protocol_metrics}")
            print(f"Experiment Cost: {experiment_cost}")  # Print experiment cost

    except Error as e:
        print(f"Error while processing data: {e}")
    finally:
        if connection.is_connected():
            connection.close()
            print("Connection closed")

if __name__ == "__main__":
    process_experiments()