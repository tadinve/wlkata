import requests
import json
import time
import re


# Initialise position and idlecounter
prev_position = [0,0,0]
idle_count = 0

# Set the URL of the API endpoint
api_url = 'https://c9kuif0njh.execute-api.us-east-2.amazonaws.com/devices'


# Extract the numbers in the log line. Cheap Trick instead of parsing.
def extract_numbers(log_line):
    pattern = r'[-+]?\d*\.\d+|[-+]?\d+'
    numbers = re.findall(pattern, log_line)
    numbers = [float(num) for num in numbers]
    return numbers


# Function to make the API call and post the json and print the respond from the API
def post_json_to_api(url, payload):
    headers = {'Content-Type': 'application/json'}
    auth = ('troy_cline@bmc.com', 'helixdemo2022')
    print('Payload:', payload)
    response = requests.post(url, headers=headers, data=json.dumps(payload), auth=auth)
    print('Response:', response.status_code)
    print('Response content:', response.content)
    print('---')


# Process the logline and keep track if it has moved in position. If not moved, then send error.
def process_log_line(log_line,deviceId):
    global idle_count
    global prev_position
    numbers = extract_numbers(log_line)
    if prev_position[0]==numbers[13] and prev_position[1]==numbers[14] and prev_position[2]==numbers[15]:
        idle_count=idle_count+1
    else:
        idle_count=0

    prev_position[0]=numbers[13]
    prev_position[1]=numbers[14]
    prev_position[2]=numbers[15]

    if idle_count<5:
        # Define the JSON payload to send
        json_payload = {
            "deviceId": deviceId,
            "baseRotation": numbers[6],
            "lowerArm": numbers[7],
            "upperArm": numbers[8],
            "wristRotation": numbers[9],
            "wristAngle": numbers[10],
            "endAngle": numbers[11],
            "suction": 1,
            "speed": 30,
        }
    else:
        # Define the JSON payload to send
        json_payload = {
            "deviceId": "17",
            "errortitle": "Arm Idle/Waiting",
            "errorMessage": "Process Inoperational Check Packaging Station",
        }

    post_json_to_api(api_url, json_payload)



# Loop continuously for testing. This will send data for 25 seconds then start showing error. Restart the program to see data again and error dissapear
# ArmIDs are 17 and 18

interval = 5
log_line = "2023-05-23 15:09:20|<Run,Angle(ABCDXYZ):-0.656,-47.669,-1.659,0.000,1.014,5.897,41.516,Cartesian coordinate(XYZ RxRyRz):169.948,2.820,99.273,-0.437,-0.268,-0.160,Pump PWM:0,Valve PWM:0,Motion_MODE:1>"
# Open the file
with open('com9.txt', 'r') as file:
    # Loop through each line in the file
    i = 0
    for line in file:
        i += 1
        if len(line) > 10:  # there is data in the line
            print(line.strip())  # strip() is used to remove the newline character at the end
            process_log_line(line,17)
        if i > 5:
            break