import paho.mqtt.client as mqtt
import csv
import time

# def on_publish(client, userdata, mid, rc):
#   """Callback function called after a message is published."""
#   if rc == 0:
#       print(f"Message published successfully - mid: {mid}")
#   else:
#       print(f"Message publish failed with code: {rc}")
lastreceivedmsg = ''
def write_to_csv(message, timestamp):
  """Writes message and timestamp to a CSV file."""
  with open("pub_mqtt_data.csv", "a", newline="") as csvfile:
      writer = csv.writer(csvfile)
      writer.writerow([message, timestamp ])
def on_connect(client, userdata, flags, rc):
  """Connects to the MQTT broker and subscribes to the topic."""
  if rc == 0:
      print("Connected successfully!")
      client.subscribe("VRcycling/UserB/Speed")  # Replace with your desired topic
  else:
      print(f"Connection failed with code {rc}")
def on_message(client, userdata, msg):
  global lastreceivedmsg
  """Writes received message and timestamp to a CSV file."""
  # Get current timestamp
  timestamp = time.time()

  # Open CSV file in append mode
  # with open("sub_mqtt_data.csv", "a", newline="") as csvfile:
  #     writer = csv.writer(csvfile)
  #     writer.writerow([msg.payload.decode("utf-8"), timestamp])
  lastreceivedmsg = msg.payload.decode('utf-8')
  print(f"Received message: {msg.payload.decode('utf-8')}")
  print(f"Timestamp: {timestamp}")

# Define broker address (change if needed)
broker_address = "test.mosquitto.org"
topic = "VRcycling/UserB/Speed"  # Replace with your desired topic

# Create an MQTT client instance
Pub_client = mqtt.Client()
Sub_client = mqtt.Client()
# Set callback function for successful publishing
#client.on_publish = on_publish

# Connect to the broker
Pub_client.connect(broker_address)
Sub_client.on_connect = on_connect
Sub_client.on_message = on_message

Sub_client.connect(broker_address)
#Sub_client.loop_forever()
# Loop through messages 1 to 1000
# for message_number in range(1, 1001):
#   message = str(message_number)
 
#   # Publish the message to the topic
#   Pub_client.publish(topic, message)
#   timestamp = time.time()
#   write_to_csv(message, timestamp)
#   print(message,timestamp)
#   time.sleep(0.1)  # Add a slight delay between messages (optional)
Pub_client.loop_start()
Sub_client.loop_start()
time.sleep(2)
i=1
previous_msg = str(0)
while (i<=1000):
  message = str(i)
  
  if (previous_msg !=message):
    print(message)
    Pub_client.publish(topic, message)
    pub_time = time.time()
    previous_msg = message
    
  if (lastreceivedmsg==message):
     sub_time = time.time()
     delay = sub_time-pub_time
     write_to_csv(message, delay)
     i+=1

# Disconnect from the broker
time.sleep(30)
Pub_client.disconnect()

print("Finished publishing messages and writing to CSV file.")
