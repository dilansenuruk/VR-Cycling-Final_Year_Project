import paho.mqtt.client as mqtt
import csv
import time

def on_connect(client, userdata, flags, rc):
  """Connects to the MQTT broker and subscribes to the topic."""
  if rc == 0:
      print("Connected successfully!")
      client.subscribe("VRcycling/UserB/Speed")  # Replace with your desired topic
  else:
      print(f"Connection failed with code {rc}")

def on_message(client, userdata, msg):
  """Writes received message and timestamp to a CSV file."""
  # Get current timestamp
  timestamp = time.time()

  # Open CSV file in append mode
  with open("sub_mqtt_data.csv", "a", newline="") as csvfile:
      writer = csv.writer(csvfile)
      writer.writerow([msg.payload.decode("utf-8"), timestamp])

  print(f"Received message: {msg.payload.decode('utf-8')}")
  print(f"Timestamp: {timestamp}")

# Define broker address (change if needed)
broker_address = "192.168.136.187"

# Create an MQTT client instance
client = mqtt.Client()

# Set callback functions
client.on_connect = on_connect
client.on_message = on_message

# Connect to the broker
client.connect(broker_address)

# Start the client loop (to receive messages)
client.loop_forever()
