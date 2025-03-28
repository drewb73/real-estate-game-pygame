import json
import os
from .property import Property, generate_properties_for_month
from .market import MarketAnalytics, MarketSnapshot

PLAYER_DATA_FILE = "player_data.json"

class Player:
    def __init__(self, name, difficulty, capital, properties=None, year=1, month=1, available_properties=None):
        self.name = name
        self.difficulty = difficulty
        self.capital = capital
        self.properties = properties if properties is not None else []
        self.year = year
        self.month = month
        self.available_properties = available_properties if available_properties is not None else []
        self.market = MarketAnalytics()

    def save(self):
        """Save player data to a file."""
        data = {
            "name": self.name,
            "difficulty": self.difficulty,
            "capital": self.capital,
            "properties": [prop.to_dict() for prop in self.properties],
            "year": self.year,
            "month": self.month,
            "available_properties": [prop.to_dict() for prop in self.available_properties],
            "market_history": {
                str(month): [snapshot.__dict__ for snapshot in snapshots]
                for month, snapshots in self.market.history.items()
            }
        }
        with open(PLAYER_DATA_FILE, "w") as file:
            json.dump(data, file, indent=4)
        print(f"Progress saved for {self.name}!")

    @staticmethod
    def load():
        """Load player data from a file."""
        if not os.path.exists(PLAYER_DATA_FILE):
            return None

        try:
            with open(PLAYER_DATA_FILE, "r") as file:
                data = json.load(file)

            # Validate required fields
            required_fields = ["name", "difficulty", "capital", "properties", 
                              "year", "month", "available_properties"]
            if not all(key in data for key in required_fields):
                raise ValueError("Missing required fields in save file")

            # Load properties
            def load_properties(prop_list):
                return [
                    Property(
                        property_type=prop["property_type"],
                        address=prop["address"],
                        units=prop["units"],
                        price_per_unit=prop["price_per_unit"],
                        management_fee_percent=prop["management_fee_percent"],
                        rent_per_unit=prop["rent_per_unit"],
                        maintenance_per_unit=prop["maintenance_per_unit"]
                    ) for prop in prop_list
                ]

            player = Player(
                name=data["name"],
                difficulty=data["difficulty"],
                capital=data["capital"],
                properties=load_properties(data.get("properties", [])),
                year=data["year"],
                month=data["month"],
                available_properties=load_properties(data.get("available_properties", []))
            )

            # Load market history
            if "market_history" in data:
                for month_str, snapshots in data["market_history"].items():
                    player.market.history[int(month_str)] = [
                        MarketSnapshot(
                            property_type=s["property_type"],
                            avg_price_per_unit=s["avg_price_per_unit"],
                            avg_rent_per_unit=s["avg_rent_per_unit"],
                            avg_cap_rate=s["avg_cap_rate"]
                        ) for s in snapshots
                    ]

            return player

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"Error loading save file: {e}. Starting a new game.")
            try:
                os.remove(PLAYER_DATA_FILE)
            except:
                pass
            return None

def create_player():
    """Create a new player with initial setup."""
    name = input("Enter your name: ").strip()
    while not name:
        print("Name cannot be empty!")
        name = input("Enter your name: ").strip()

    print("\nChoose your difficulty level:")
    print("1. Easy ($5,000,000)")
    print("2. Medium ($2,500,000)")
    print("3. Hard ($1,000,000)")
    
    difficulty_map = {
        "1": ("Easy", 5_000_000),
        "2": ("Medium", 2_500_000),
        "3": ("Hard", 1_000_000)
    }
    
    while True:
        choice = input("Enter your choice (1, 2, or 3): ")
        if choice in difficulty_map:
            difficulty, capital = difficulty_map[choice]
            break
        print("Invalid choice. Please enter 1, 2, or 3.")

    available_properties = generate_properties_for_month()
    return Player(name, difficulty, capital, year=1, month=1, available_properties=available_properties)

def initialize_player():
    """Initialize or load player data."""
    if os.path.exists(PLAYER_DATA_FILE):
        try:
            with open(PLAYER_DATA_FILE, "r") as file:
                data = json.load(file)
            saved_name = data.get("name", "Unknown")

            print(f"\nWelcome back, {saved_name}!")
            print("1. Continue your saved game")
            print("2. Delete save and restart")
            
            while True:
                choice = input("Enter your choice (1 or 2): ")
                if choice == "1":
                    player = Player.load()
                    if player:
                        return player
                    break
                elif choice == "2":
                    os.remove(PLAYER_DATA_FILE)
                    print("Save file deleted. Starting new game...")
                    break
                else:
                    print("Invalid choice. Please enter 1 or 2.")
        except:
            print("Corrupted save file. Starting new game...")
            os.remove(PLAYER_DATA_FILE)

    print("\nWelcome to the Real Estate Game!")
    return create_player()