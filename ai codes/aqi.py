AQI_BREAKPOINTS = {
    "PM25": [
        (0, 30, 0, 50),
        (31, 60, 51, 100),
        (61, 90, 101, 200),
        (91, 120, 201, 300),
        (121, 250, 301, 400),
        (251, 500, 401, 500)
    ],
    "PM10": [
        (0, 50, 0, 50),
        (51, 100, 51, 100),
        (101, 250, 101, 200),
        (251, 350, 201, 300),
        (351, 430, 301, 400),
        (431, 600, 401, 500)
    ]
}
def get_category(aqi):
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Satisfactory"
    elif aqi <= 200:
        return "Moderate"
    elif aqi <= 300:
        return "Poor"
    elif aqi <= 400:
        return "Very Poor"
    else:
        return "Severe"
def calculate_aqi(pollutant, concentration):
    if pollutant not in AQI_BREAKPOINTS:
        return None
    
    for bp_low, bp_high, aqi_low, aqi_high in AQI_BREAKPOINTS[pollutant]:
        if bp_low <= concentration <= bp_high:
            aqi = ((aqi_high - aqi_low) / (bp_high - bp_low)) * \
                  (concentration - bp_low) + aqi_low
            return round(aqi)
    return None
def aqi_agent(file_name):
    sensor_data = {}
    with open(file_name, "r") as file:
        for line in file:
            key, value = line.strip().split("=")
            sensor_data[key] = float(value)

    max_aqi = 0
    dominant_pollutant = ""
    for pollutant, value in sensor_data.items():
        aqi = calculate_aqi(pollutant, value)
        if aqi and aqi > max_aqi:
            max_aqi = aqi
            dominant_pollutant = pollutant
    category = get_category(max_aqi)
    print("Dominant Pollutant:", dominant_pollutant)
    print("AQI Value:", max_aqi)
    print("Category:", category)
aqi_agent("sensor_data.txt")
