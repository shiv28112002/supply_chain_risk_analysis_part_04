
import os
import pandas as pd
import requests
from langchain_core.tools import tool

# Project directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Creating Tool 1

# Risk Events dataset
risk_file = os.path.join(BASE_DIR, "data", "risk_events.csv")

# Loading risk events
risk_df = pd.read_csv(risk_file)

# Tool 1: Risk Analysis

@tool
def analyze_risk_events(analysis_type: str) -> str:
    """
    Analyze historical supply-chain risk events.

    Use this tool to investigate risk categories, risk types,
    severity, estimated loss, impact areas, root causes,
    and risk status.

    analysis_type can be:
    category, type, severity, loss, impact_area,
    root_cause, or status.

    This is a read-only tool and does not modify the dataset.
    """
    try:

        if not analysis_type:
            return "Error: analysis_type is required."

        analysis_type = analysis_type.lower().strip()

        if analysis_type == "category":
            result = (risk_df["risk_category"].value_counts().head(10))
            return "Risk events by category:\n" + result.to_string()

        elif analysis_type == "type":
            result = (risk_df["risk_type"].value_counts().head(10))
            return "Most common risk types:\n" + result.to_string()

        elif analysis_type == "severity":
            result = risk_df["severity"].value_counts()
            return "Risk events by severity:\n" + result.to_string()

        elif analysis_type == "loss":
            result = (risk_df.groupby("risk_category")["estimated_loss"]
                      .agg(event_count="count",total_loss="sum",average_loss="mean")
                      .sort_values("total_loss",ascending=False).head(10)
                      )
            return ("Risk categories ranked by estimated loss:\n"+ result.to_string())

        elif analysis_type == "impact_area":
            result = (risk_df["impact_area"].value_counts().head(10))
            return "Risk events by impact area:\n" + result.to_string()

        elif analysis_type == "root_cause":
            result = (risk_df["root_cause"].value_counts().head(10))
            return "Most common root causes:\n" + result.to_string()

        elif analysis_type == "status":
            result = risk_df["status"].value_counts()
            return "Risk events by status:\n" + result.to_string()

        else:
             return ("Error: unsupported analysis_type. "
                    "Use category, type, severity, loss, "
                    "impact_area, root_cause, or status."
                    )

    except Exception as e:
        return f"Error while analyzing risk events: {str(e)}"

# Creating Tool 2

# Shippment dataset
shipment_file = os.path.join( BASE_DIR,"data","shipment.csv")

# Loading shippment
shipment_df = pd.read_csv(shipment_file)

# Tool 2: Shipment Analysis

@tool
def analyze_shipments(analysis_type: str) -> str:
    """
    Analyze shipment and delivery performance.

    Use this tool to investigate shipment status, delay reasons,
    shipping partner performance, on-time delivery, delivery days,
    and delivery ratings.

    analysis_type can be:
    status, delay_reason, partner, on_time, delivery_days,
    or rating.

    This is a read-only tool and does not modify the dataset.
    """

    try:

        if not analysis_type:
            return "Error: analysis_type is required."

        analysis_type = analysis_type.lower().strip()

        if analysis_type == "status":
            result = (shipment_df["shipment_status"].value_counts())
            return ("Shipments by status:\n"+ result.to_string())

        elif analysis_type == "delay_reason":
            result = (shipment_df["delay_reason"].dropna().value_counts().head(10))
            return ("Most common shipment delay reasons:\n"+ result.to_string())

        elif analysis_type == "partner":
            result = (shipment_df["shipping_partner"].value_counts().head(10))
            return ("Shipments by shipping partner:\n"+ result.to_string())

        elif analysis_type == "on_time":
            result = (shipment_df["is_on_time"].value_counts())
            total = len(shipment_df)
            on_time = (shipment_df["is_on_time"].eq("Yes").sum())
            on_time_rate = ((on_time / total) * 100
                            if total > 0
                            else 0
                            )
            return ("Shipment on-time performance:\n"+ result.to_string()
                + f"\n\nOverall on-time rate: "
                f"{on_time_rate:.2f}%")

        elif analysis_type == "delivery_days":
            result = (shipment_df["delivery_days"].describe())
            return ("Shipment delivery-day statistics:\n"+ result.to_string())

        elif analysis_type == "rating":
            result = (shipment_df.groupby("shipping_partner")["delivery_rating"].mean().sort_values())
            return ("Average delivery rating by shipping partner:\n"+ result.to_string())

        else:
            return ("Error: unsupported analysis_type. "
                    "Use status, delay_reason, partner, "
                    "on_time, delivery_days, or rating."
                    )

    except Exception as e:
        return (f"Error while analyzing shipments: {str(e)}")
    
    
# Creating Tool 3

# Tool 3: Live Weather API

@tool
def get_weather(shipment_id: str) -> str:
    """
    Get the current weather for the shipping city of a shipment.

    The tool reads the shipping city from the shipment dataset
    using the shipment_id, then calls the live Open-Meteo API.

    Returns only the city, weather condition, and temperature.

    This is a read-only tool and does not modify the dataset.
    """

    try:

        # Find the shipment
        shipment = shipment_df[ shipment_df["shipment_id"].astype(str) == str(shipment_id)]

        if shipment.empty:
            return f"Error: Shipment '{shipment_id}' was not found."

        # Get shipping city from the dataset
        city = shipment.iloc[0]["shipping_city"]

        if pd.isna(city) or not str(city).strip():
            return (f"Error: No shipping city found "
                    f"for shipment '{shipment_id}'."
                    )

        city = str(city).strip()

        # Find city coordinates using Open-Meteo geocoding
        geo_response = requests.get("https://geocoding-api.open-meteo.com/v1/search",
                                    params={"name": city,
                                            "count": 1,
                                            "language": "en",
                                            "format": "json"},
                                    timeout=10
                                    )

        if geo_response.status_code != 200:
            return "Error: Could not find the shipping city."

        geo_data = geo_response.json()
        results = geo_data.get("results")

        if not results:
            return f"Error: City '{city}' was not found."

        latitude = results[0]["latitude"]
        longitude = results[0]["longitude"]

        # Get live weather
        weather_response = requests.get("https://api.open-meteo.com/v1/forecast",
                                        params={"latitude": latitude,
                                                "longitude": longitude,
                                                "current": "temperature_2m,weather_code"},
                                        timeout=10
                                        )

        if weather_response.status_code != 200:
            return "Error: Could not retrieve weather data."

        weather_data = weather_response.json()
        current = weather_data.get("current")

        if not current:
            return "Error: No current weather data was returned."

        temperature = current.get("temperature_2m")
        weather_code = current.get("weather_code")

        # Convert weather code to simple condition
        if weather_code == 0:
            condition = "Clear"

        elif weather_code in [1, 2]:
            condition = "Mainly clear"

        elif weather_code == 3:
            condition = "Cloudy"

        elif weather_code in [45, 48]:
            condition = "Foggy"

        elif weather_code in [95, 96, 99]:
            condition = "Thunderstorm"

        elif weather_code in [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82]:
            condition = "Rainy"

        else:
            condition = "Cloudy"

        return (f"{city}\n"
                f"{condition}\n"
                f"Temperature: {temperature}°C"
                )

    except requests.exceptions.Timeout:
        return (f"Error: Weather API request timed out.")

    except requests.exceptions.RequestException as e:
        return (f"Error: Could not connect to Weather API: {str(e)}")

    except Exception as e:
        return (f"Error while processing weather data: {str(e)}")
    