import random

# Street names and types for address generation
STREET_NAMES = ["Oak", "Pine", "Elm", "Maple", "Cedar", "Hill", "Lake", "River", "Park", "Main"]
STREET_TYPES = ["St", "Ave", "Blvd", "Ln", "Ct", "Rd", "Dr", "Way"]

class Property:
    def __init__(self, property_type, address, units, price_per_unit, 
                 management_fee_percent, rent_per_unit, maintenance_per_unit):
        self.property_type = property_type
        self.address = address
        self.units = units
        self.price_per_unit = price_per_unit
        self.management_fee_percent = management_fee_percent
        self.rent_per_unit = rent_per_unit
        self.maintenance_per_unit = maintenance_per_unit
        
        # Consistent expense calculation
        base_ratio = 0.35  # Base 35% expense ratio
        variation = random.uniform(-0.05, 0.05)  # ±5% variation
        self._expense_ratio = base_ratio + variation  # Final ratio between 30-40%

    def to_dict(self):
        """Convert property to dictionary for saving"""
        return {
            "property_type": self.property_type,
            "address": self.address,
            "units": self.units,
            "price_per_unit": self.price_per_unit,
            "management_fee_percent": self.management_fee_percent,
            "rent_per_unit": self.rent_per_unit,
            "maintenance_per_unit": self.maintenance_per_unit,
            "expense_ratio": self._expense_ratio
        }
    
    @property
    def total_price(self):
        return self.units * self.price_per_unit
    
    @property
    def gross_income(self):
        return (self.units * self.rent_per_unit) * 12
    
    @property
    def management_fee(self):
        return self.gross_income * (self.management_fee_percent / 100)
    
    @property
    def total_expenses(self):
        return self.gross_income * self._expense_ratio
    
    @property
    def net_income(self):
        return self.gross_income - self.total_expenses
    
    @property
    def cap_rate(self):
        if self.total_price == 0:
            return 0
        return (self.net_income / self.total_price) * 100
    
    def __str__(self):
        """String representation of property"""
        valuation = "\n🔥🔥 Premium Investment!" if self.cap_rate >= 7 else \
                   "\n🔥 Solid Deal" if self.cap_rate >= 5.5 else \
                   "\n⚠️⚠️ Money Pit" if self.cap_rate <= 3 else \
                   "\n⚠️ Below Average" if self.cap_rate <= 4 else "\n➖ Average"
        
        return f"""Type: {self.property_type}
Address: {self.address}
Units: {self.units}
Price per unit: ${self.price_per_unit:,.2f}
Total Price: ${self.total_price:,.2f}
Rent per unit: ${self.rent_per_unit:,.2f}
Gross Income: ${self.gross_income:,.2f}
Management Fee: ${self.management_fee:,.2f}
Expenses: ${self.total_expenses:,.2f}
Net Income: ${self.net_income:,.2f}
CAP Rate: {self.cap_rate:.2f}%{valuation}"""

# Property generation functions
def generate_address():
    """Generate a random street address"""
    street_number = random.randint(1, 9999)
    street_name = random.choice(STREET_NAMES)
    street_type = random.choice(STREET_TYPES)
    return f"{street_number:04d} {street_name} {street_type}"

def generate_units(property_type):
    """Generate appropriate units based on property type"""
    return {
        "Duplex": 2,
        "Triplex": 3,
        "Fourplex": 4,
        "Apartment": random.randint(5, 15),
        "Apartment Complex": random.randint(16, 150)
    }.get(property_type, 1)

def generate_price_per_unit():
    """Generate random price per unit"""
    return random.randint(150_000, 250_000)

def generate_management_fee_percent():
    """Generate random management fee percentage"""
    return random.uniform(5.0, 8.0)

def generate_rent_per_unit():
    """Generate random rent amount per unit"""
    return random.randint(1200, 2200)

def generate_maintenance_per_unit():
    """Generate random maintenance cost per unit"""
    return random.randint(200, 800)

def generate_property(property_type):
    """Generate a property with natural CAP rate variation"""
    prop = Property(
        property_type=property_type,
        address=generate_address(),
        units=generate_units(property_type),
        price_per_unit=generate_price_per_unit(),
        management_fee_percent=generate_management_fee_percent(),
        rent_per_unit=generate_rent_per_unit(),
        maintenance_per_unit=generate_maintenance_per_unit()
    )
    
    # Ensure some variety in quality
    if random.random() < 0.3:  # 30% chance of underperforming property
        prop.rent_per_unit *= random.uniform(0.7, 0.9)  # Reduce rent
        prop.price_per_unit *= random.uniform(1.1, 1.3)  # Increase price
    
    return prop

def generate_properties_for_type(property_type, count=5):
    """Generate multiple properties of a specific type"""
    return [generate_property(property_type) for _ in range(count)]

def generate_properties_for_month():
    """Generate properties for all types for the current month"""
    property_types = ["Duplex", "Triplex", "Fourplex", "Apartment", "Apartment Complex"]
    return [prop for prop_type in property_types 
            for prop in generate_properties_for_type(prop_type, count=5)]