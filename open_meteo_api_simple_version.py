import requests
import mysql.connector
from time import localtime, strftime, sleep
import json

# MySQL database connection - replace with your own credentials
conn = mysql.connector.connect(
    host="localhost",  
    user="root",  
    password="xxxxxxxxxxx", 
    database="weather_data"  
)
# Create a cursor object
cursor = conn.cursor() 

# Get current time
def current_time(): 
    return strftime("%Y-%m-%d %H:%M:%S", localtime())

# use Open-Meteo API to collect data
def get_weather_data(): 
    response = requests.get("https://api.open-meteo.com/v1/forecast",
                            params={
                                "latitude": 49.322740,
                                "longitude": 19.551755,
                                "current": ["temperature_2m", "relative_humidity_2m", "surface_pressure", "wind_speed_10m"]
                            }
                            )
    return response.json() 

# Store data into MySQL database
def store_weather_data(cycles):
    for i in range(cycles): 
        output = get_weather_data()
        temperature = output["current"]["temperature_2m"]
        relative_humidity= output["current"]["relative_humidity_2m"]
        surface_pressure = output["current"]["surface_pressure"]
        wind_speed = output["current"]["wind_speed_10m"]
        current_time_str = current_time()
        print(f"Date and Time: {current_time_str} Temperature: {temperature}, Relative Humidity: {relative_humidity}, Surface Pressure: {surface_pressure}, Wind Speed: {wind_speed}")
        print(f"Attempt {i+1} of {cycles}  Storing data in the database and waiting for 5 seconds for next measurement...")
        # Insert data into database
        cursor.execute("INSERT INTO temperature_log (log_time, temperature, relative_humidity, surface_pressure, wind_speed) VALUES (%s, %s, %s, %s, %s)", 
                   (current_time_str, temperature, relative_humidity, surface_pressure, wind_speed))
        conn.commit()  # Commit the transaction
        sleep(5)  # Wait for 5 seconds before the next measurement

# Print the contents of the database
def print_database_contents():
    cursor.execute("SELECT * FROM temperature_log")
    rows = cursor.fetchall()
    print("\nDatabase Contents:")
    print(f"{'ID':<5} {'Log Time':<16} {'Temperature':<12} {'Humidity':<10} {'Pressure':<13} {'Wind'}")
    print("-" * 65)
    for row in rows:
        log_time_str = row[1].strftime("%d-%m-%Y %H:%M:%S")  # Format datetime 
        print(f"{row[0]:<5} {log_time_str:<20} {row[2]:<10} {row[3]:<10} {row[4]:<10} {row[5]:<10}")

# Export data from MySQL database to a JSON file
def export_to_json():
    cursor.execute("SELECT * FROM temperature_log")
    rows = cursor.fetchall()
    
    # Defining keys for JSON structure
    data = []
    for row in rows:
        data.append({
            "id": row[0],
            "log_time": row[1].strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": row[2],
            "relative_humidity": row[3],
            "surface_pressure": row[4],
            "wind_speed": row[5]
        })

    # Export to a JSON file
    with open("weather_data.json", "w") as json_file:
        json.dump(data, json_file, indent=4)
    print("Data has been exported to weather_data.json")

# Ask user for the number of cycles to run
total_cycles = int(input("How many cycles do you want to run? (one cycle is 5 second) "))
print ()

store_weather_data(total_cycles)
print ()
print_database_contents()
print ()
export_to_json()

# Close the cursor and connection
cursor.close()
conn.close()