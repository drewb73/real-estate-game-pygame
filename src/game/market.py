import random
from dataclasses import dataclass
from typing import Dict, List
import numpy as np
from .property import Property, generate_units, generate_address, generate_price_per_unit, \
                     generate_management_fee_percent, generate_rent_per_unit, generate_maintenance_per_unit

@dataclass
class MarketSnapshot:
    """Stores average metrics for one property type in a given month"""
    property_type: str
    avg_price_per_unit: float
    avg_rent_per_unit: float
    avg_cap_rate: float
    inventory: int  # Number of available properties
    days_on_market: float  # Average days on market

class MarketAnalytics:
    def __init__(self):
        self.history: Dict[int, List[MarketSnapshot]] = {}  # {month: [MarketSnapshots]}
        self.market_conditions = {
            'trend': random.choice(['bull', 'bear', 'stable']),
            'interest_rates': random.uniform(2.5, 7.5),
            'unemployment': random.uniform(3.0, 10.0)
        }
        self.seasonal_factors = self._calculate_seasonal_factors()
    
    def _calculate_seasonal_factors(self) -> Dict[int, float]:
        """Return monthly multipliers for seasonal effects"""
        return {
            1: 0.95,  # January - slow
            2: 0.97,
            3: 1.03,   # Spring pickup
            4: 1.05,
            5: 1.07,
            6: 1.06,   # Summer
            7: 1.04,
            8: 1.02,
            9: 1.01,   # Fall
            10: 1.00,
            11: 0.98,  # Holiday slowdown
            12: 0.96
        }
    
    def _get_economic_multipliers(self, month: int) -> Dict[str, float]:
        """Calculate economic impact on property values"""
        seasonal = self.seasonal_factors.get(month % 12 or 12, 1.0)
        
        # Interest rate impact (inverse relationship with prices)
        rate_impact = 1.0 - (self.market_conditions['interest_rates'] - 4.0) / 100
        
        # Unemployment impact
        employment_impact = 1.0 - (self.market_conditions['unemployment'] - 5.0) / 200
        
        # Market trend momentum
        trend_map = {'bull': 1.02, 'bear': 0.98, 'stable': 1.0}
        trend = trend_map[self.market_conditions['trend']]
        
        # Random fluctuation
        fluctuation = random.uniform(0.98, 1.02)
        
        return {
            'price': seasonal * rate_impact * trend * fluctuation,
            'rent': seasonal * employment_impact * fluctuation,
            'inventory': 1.0 / (seasonal * trend)
        }
    
    def generate_monthly_samples(self, current_month: int) -> List[MarketSnapshot]:
        """Generate market data with realistic economic simulation"""
        property_types = ["Duplex", "Triplex", "Fourplex", "Apartment", "Apartment Complex"]
        monthly_data = []
        economic_factors = self._get_economic_multipliers(current_month)
        
        # Update market conditions (10% chance of change each month)
        if random.random() < 0.1:
            self._update_market_conditions()
        
        for prop_type in property_types:
            prices = []
            rents = []
            cap_rates = []
            inventories = []
            doms = []  # Days on market
            
            # Generate between 80-120 sample properties per type
            sample_size = random.randint(80, 120)
            for _ in range(sample_size):
                # Base property with economic adjustments
                prop = self._generate_property_with_economics(prop_type, economic_factors)
                
                prices.append(prop.price_per_unit)
                rents.append(prop.rent_per_unit)
                cap_rates.append(prop.cap_rate)
                inventories.append(1 if random.random() < 0.3 else 0)  # 30% chance of being available
                doms.append(random.randint(0, 90))  # 0-90 days on market
            
            monthly_data.append(MarketSnapshot(
                property_type=prop_type,
                avg_price_per_unit=np.mean(prices),
                avg_rent_per_unit=np.mean(rents),
                avg_cap_rate=np.mean(cap_rates),
                inventory=int(np.sum(inventories)),
                days_on_market=np.mean(doms)
            ))
        
        self.history[current_month] = monthly_data
        return monthly_data
    
    def _generate_property_with_economics(self, prop_type: str, factors: Dict[str, float]) -> Property:
        """Generate a property with economic influences"""
        # Apply economic multipliers with some randomness
        price_mult = factors['price'] * random.uniform(0.95, 1.05)
        rent_mult = factors['rent'] * random.uniform(0.9, 1.1)
        
        prop = Property(
            property_type=prop_type,
            address="MARKET_SAMPLE",
            units=generate_units(prop_type),
            price_per_unit=int(generate_price_per_unit() * price_mult),
            management_fee_percent=generate_management_fee_percent(),
            rent_per_unit=int(generate_rent_per_unit() * rent_mult),
            maintenance_per_unit=generate_maintenance_per_unit()
        )
        
        # 15% chance of being a distressed property
        if random.random() < 0.15:
            prop.price_per_unit *= random.uniform(0.7, 0.9)
            prop.rent_per_unit *= random.uniform(0.8, 1.2)
        
        return prop
    
    def _update_market_conditions(self):
        """Gradually shift market conditions"""
        # Interest rate drift (up or down 0-25 basis points)
        self.market_conditions['interest_rates'] += random.uniform(-0.25, 0.25)
        self.market_conditions['interest_rates'] = max(2.5, min(10.0, 
            self.market_conditions['interest_rates']))
        
        # Unemployment changes
        self.market_conditions['unemployment'] += random.uniform(-0.5, 0.5)
        self.market_conditions['unemployment'] = max(3.0, min(15.0,
            self.market_conditions['unemployment']))
        
        # Market trend transitions
        if random.random() < 0.2:  # 20% chance to change trend
            trends = ['bull', 'bear', 'stable']
            current = self.market_conditions['trend']
            trends.remove(current)
            self.market_conditions['trend'] = random.choice(trends)
    
    def get_latest_market_data(self) -> List[MarketSnapshot]:
        """Get the most recent market data with additional analysis"""
        if not self.history:
            return []
            
        latest_month = max(self.history.keys())
        data = self.history[latest_month]
        
        # Add market temperature indicators
        for snapshot in data:
            snapshot.temperature = self._calculate_market_temperature(snapshot)
        
        return data
    
    def _calculate_market_temperature(self, snapshot: MarketSnapshot) -> str:
        """Determine if market is hot, normal, or cold for this property type"""
        dom = snapshot.days_on_market
        inventory = snapshot.inventory
        
        if dom < 30 and inventory < 10:
            return "🔥 Hot Market"
        elif dom > 60 and inventory > 25:
            return "❄️ Cold Market"
        return "➖ Balanced Market"
    
    def get_market_trend(self, property_type: str) -> float:
        """Get percentage change in price from previous month with momentum"""
        if len(self.history) < 2:
            return 0.0
            
        months = sorted(self.history.keys())
        current_month = months[-1]
        previous_month = months[-2]
        
        current = next((x for x in self.history[current_month] 
                       if x.property_type == property_type), None)
        previous = next((x for x in self.history[previous_month] 
                        if x.property_type == property_type), None)
        
        if not current or not previous:
            return 0.0
        
        price_change = ((current.avg_price_per_unit - previous.avg_price_per_unit) / 
                       previous.avg_price_per_unit) * 100
        
        # Add momentum if we have more history
        if len(self.history) > 2:
            two_months_ago = months[-3]
            older = next((x for x in self.history[two_months_ago]
                         if x.property_type == property_type), None)
            if older:
                prev_change = ((previous.avg_price_per_unit - older.avg_price_per_unit) / 
                               older.avg_price_per_unit) * 100
                # Apply 30% momentum effect
                price_change = price_change * 0.7 + prev_change * 0.3
        
        return price_change
    
    def get_best_investment(self) -> MarketSnapshot:
        """Return the property type with highest current cap rate"""
        if not self.history:
            return None
            
        latest = self.get_latest_market_data()
        return max(latest, key=lambda x: x.avg_cap_rate)