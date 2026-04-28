import requests
import pandas as pd
import logging

# basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def fetch_weather_to_csv(start_date: str, end_date: str, output_csv: str):
    """Fetch historical weather data from Open-Meteo and save to CSV."""
    
    # Gwangyang, South Korea
    latitude = 34.975
    longitude = 127.589
    
    # API URL
    url = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        f"&start_date={start_date}"
        f"&end_date={end_date}"
        f"&hourly=temperature_2m,precipitation,relative_humidity_2m,windspeed_10m"
        f"&timezone=Asia%2FSeoul"
    )
    
    logger.info(f"Fetching weather data from {start_date} to {end_date}...")
    
    try:
        # Fetch weather data
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if "hourly" not in data:
            logger.error("Invalid API response: 'hourly' data is missing.")
            return

        # Convert the JSON 'hourly' dictionary into a dataFrame
        hourly_data = data["hourly"]
        df = pd.DataFrame(hourly_data)
        
        # Export to CSV
        df.to_csv(output_csv, index=False)
        logger.info(f"Success! Inserted {len(df)} records into {output_csv}")
        
    except requests.Timeout:
        logger.error("API request timed out.")
    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Define timeframe and target file
    START_DATE = "2018-01-01"
    END_DATE = "2018-12-31"
    OUTPUT_FILE = "gwangyang_weather_2018.csv"
    
    fetch_weather_to_csv(START_DATE, END_DATE, OUTPUT_FILE)