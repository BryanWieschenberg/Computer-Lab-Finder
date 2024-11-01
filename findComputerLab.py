from datetime import datetime, timedelta
import csv

def readCSV(VALID_ROOMS):
    def round_time(time):
        """ Round times ending in xx:20 to xx:30, and xx:50 to xx:00 of the next hour """
        timeObj = datetime.strptime(time, "%I:%M%p")
        if datetime.strptime(time, "%I:%M%p").minute == 20:
            return timeObj.replace(minute=30)
        elif timeObj.minute == 50:
            return (timeObj + timedelta(hours=1)).replace(minute=0)
        return timeObj
    
    reserved = {"Mo": {}, "Tu": {}, "We": {}, "Th": {}, "Fr": {}}

    with open("reserved.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            day = row["Day"]
            start = row["Start"]
            end = row["End"]
            room = row["Room"]
            
            if room not in VALID_ROOMS: # Check if room is valid
                continue
            
            end = round_time(end) # Rounds end time to nearest 30 minute interval
            end = end.strftime("%I:%M%p")
            
            room = room.split()[-1]

            if room not in reserved[day]: # Add entry to reserved if the room and day are valid
                reserved[day][room] = []
            
            reserved[day][room].append((start, end))
    
    return reserved

# Function to check room availability and provide available times
from datetime import datetime, timedelta

def checkAvailability(start, end, reserved, VALID_ROOMS):
    def parse_time(time_str):
        return datetime.strptime(time_str, "%I:%M%p")
    # Prepare time slots in 30-minute intervals
    start_time = parse_time(start)
    end_time = parse_time(end)
    time_slots = []
    current_time = start_time
    
    while current_time < end_time:
        time_slots.append(current_time.strftime("%I:%M%p"))
        current_time += timedelta(minutes=30)
    
    # Initialize availability matrix for each time slot and each room-day combination
    availability_matrix = {slot: {f"{room.split()[-1]}_{day}": "0" for day in ["Mo", "Tu", "We", "Th", "Fr"] for room in VALID_ROOMS} for slot in time_slots}

    # Fill in reserved times with "."
    for day in ["Mo", "Tu", "We", "Th", "Fr"]:
        for room, times in reserved.get(day, {}).items():
            for res_start, res_end in times:
                res_start = parse_time(res_start)
                res_end = parse_time(res_end)
                
                for i, slot in enumerate(time_slots):
                    slot_time = parse_time(slot)
                    if res_start <= slot_time < res_end:
                        availability_matrix[slot][f"{room}_{day}"] = "."

    # Print the header without day suffixes for each room and with reduced spacing
    header = "        " + "  ".join(f"{room.split()[-1]}" for _ in range(5) for room in VALID_ROOMS)
    print(header)

    # Print each time slot and the corresponding availability for each room-day combination
    for slot in time_slots:
        row = f"{slot}  " + "    ".join(availability_matrix[slot][key] for key in availability_matrix[slot])
        print(row)

# Valid rooms the script will add to the roster
#   No data is available for 'Forcina Hall 411', but if we are able to get it eventually, it is valid
VALID_ROOMS = ["Forcina Hall 403", "Forcina Hall 406", "Forcina Hall 424", "STEM Building 112"]
reserved = readCSV(VALID_ROOMS)

# Display available rooms within that day
checkAvailability("8:00AM", "10:00PM", reserved, VALID_ROOMS)
