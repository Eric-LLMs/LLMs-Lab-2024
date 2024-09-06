import requests


class POI:

    def __init__(self, client, amap_key="22b34521f11ce01f5744ffa28893cmef"):
        # Initialize the POI class with a client and an optional amap_key.
        self.client = client
        self.amap_key = amap_key

    def get_completion(self, messages, model="gpt-3.5-turbo"):
        # This method calls the OpenAI API with a set of messages and optional parameters.
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,  # Setting the temperature to 0 for deterministic results.
            seed=1024,  # The random seed ensures consistent outputs given the same temperature and prompt.
            tool_choice="auto",  # The default value lets GPT decide whether to use function calls or text responses.
            # You can also enforce a specific Function-Calling as per the official documentation.
            tools=[{
                "type": "function",
                "function": {
                    "name": "get_location_coordinate",
                    "description": "Retrieve the coordinates (latitude and longitude) of a POI based on its name.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The name of the POI, which must be in Chinese.",
                            },
                            "city": {
                                "type": "string",
                                "description": "The name of the city where the POI is located, which must be in Chinese.",
                            }
                        },
                        "required": ["location", "city"],
                    }
                }
            },
                {
                    "type": "function",
                    "function": {
                        "name": "search_nearby_pois",
                        "description": "Search for POIs near a given set of coordinates.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "longitude": {
                                    "type": "string",
                                    "description": "The longitude of the center point.",
                                },
                                "latitude": {
                                    "type": "string",
                                    "description": "The latitude of the center point.",
                                },
                                "keyword": {
                                    "type": "string",
                                    "description": "Keyword to search for the target POI.",
                                }
                            },
                            "required": ["longitude", "latitude", "keyword"],
                        }
                    }
                }],
        )
        return response.choices[0].message

    def get_location_coordinate(self, location, city):
        # Fetches the coordinates of a POI from the Amap API using the location name and city.
        url = f"https://restapi.amap.com/v5/place/text?key={self.amap_key}&keywords={location}&region={city}"
        print(url)
        r = requests.get(url)
        result = r.json()
        if "pois" in result and result["pois"]:
            return result["pois"][0]  # Return the first POI result if available.
        return None  # Return None if no POI found.

    def search_nearby_pois(self, longitude, latitude, keyword):
        # Searches for nearby POIs using the Amap API given coordinates and a keyword.
        url = f"https://restapi.amap.com/v5/place/around?key={self.amap_key}&keywords={keyword}&location={longitude},{latitude}"
        print(url)
        r = requests.get(url)
        result = r.json()
        ans = ""
        if "pois" in result and result["pois"]:
            # Format the top 3 results with their name, address, and distance.
            for i in range(min(3, len(result["pois"]))):
                name = result["pois"][i]["name"]
                address = result["pois"][i]["address"]
                distance = result["pois"][i]["distance"]
                ans += f"{name}\n{address}\nDistance: {distance} meters\n\n"
        return ans
