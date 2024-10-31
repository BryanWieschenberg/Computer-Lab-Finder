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
            
            if room not in reserved[day]: # Add entry to reserved if the room and day are valid
                reserved[day][room] = []
            
            reserved[day][room].append((start, end))
    
    return reserved

# Function to check room availability and provide available times
from datetime import datetime, timedelta

def checkAvailability(day, start, end, reserved, VALID_ROOMS):
    def parse_time(time_str):
        """Convert a time string like '9:30AM' to a datetime object for comparisons."""
        return datetime.strptime(time_str, "%I:%M%p")
    
    def format_time(time_obj):
        """Convert a datetime object back to string format like '9:30AM'."""
        return time_obj.strftime("%I:%M%p")

    # Parse the start and end times
    start_time = parse_time(start)
    end_time = parse_time(end)
    
    # Initialize output dictionary for available rooms
    available_rooms = {}

    # Loop through all valid rooms
    for room in VALID_ROOMS:
        # Get the reserved times for this room on the specified day
        reserved_times = reserved.get(day, {}).get(room, [])
        
        # Sort reserved times to handle sequential intervals
        reserved_times = [(parse_time(r_start), parse_time(r_end)) for r_start, r_end in reserved_times]
        reserved_times.sort()

        # Track the current time for available intervals
        current_time = start_time
        available_times = []

        for res_start, res_end in reserved_times:
            # If there's an available interval before the reserved slot, add it
            if current_time < res_start:
                next_time = min(res_start, end_time)
                if current_time < next_time:  # Check to ensure we have a non-zero interval
                    available_times.append((format_time(current_time), format_time(next_time)))
            
            # Move current time forward past the reserved interval
            if current_time < res_end:
                current_time = res_end
        
        # After the last reservation, check if there's remaining time
        if current_time < end_time:
            available_times.append((format_time(current_time), format_time(end_time)))
        
        # Only add room to available_rooms if there are available times
        if available_times:
            available_rooms[room] = available_times
    
    # Output results
    print(f"--- {day}: {start} - {end} ---")
    for room, times in available_rooms.items():
        print(f"{room}:")
        for time_slot in times:
            print(f"> {time_slot[0]} - {time_slot[1]}")

# Valid rooms the script will add to the roster
#   No data is available for 'Forcina Hall 411', but if we are able to get it eventually, it is valid
VALID_ROOMS = ["Forcina Hall 403", "Forcina Hall 406", "Forcina Hall 424", "STEM Building 112"]
reserved = readCSV(VALID_ROOMS)

day = input("Day (Mo|Tu|We|Th|Fr): ")
start = input("Start Time (H:MMam/pm): ")
end = input("End Time (H:MMam/pm): ")

# Display available rooms with time ranges
checkAvailability(day, start, end, reserved, VALID_ROOMS)
