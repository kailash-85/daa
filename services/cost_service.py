"""
Cost calculation service for delivery expenses.
"""


class CostService:
    """Calculate delivery costs based on various factors"""
    
    @staticmethod
    def calculate_delivery_cost(distance, time, base_charge=50, cost_per_km=10, cost_per_minute=2):
        """
        Calculate delivery cost dynamically.
        
        Formula:
        Cost = Base Charge + (Distance × Cost Per KM) + (Time × Cost Per Minute)
        
        Args:
            distance: Distance in km
            time: Estimated time in minutes
            base_charge: Base delivery charge in rupees
            cost_per_km: Cost per kilometer
            cost_per_minute: Cost per minute
        
        Returns:
            dict: {
                'base_charge': float,
                'distance_cost': float,
                'time_cost': float,
                'total': float,
                'breakdown': str (for display)
            }
        """
        if distance is None or time is None:
            return None
        
        distance_cost = distance * cost_per_km
        time_cost = time * cost_per_minute
        total_cost = base_charge + distance_cost + time_cost
        
        return {
            'base_charge': base_charge,
            'distance_cost': round(distance_cost, 2),
            'time_cost': round(time_cost, 2),
            'total': round(total_cost, 2),
            'breakdown': f"₹{base_charge} + (₹{cost_per_km}/km × {distance}km) + (₹{cost_per_minute}/min × {time}min) = ₹{round(total_cost, 2)}"
        }
    
    @staticmethod
    def calculate_multiple_routes(routes, base_charge=50, cost_per_km=10, cost_per_minute=2):
        """
        Calculate costs for multiple routes.
        
        Args:
            routes: List of route dicts with 'distance' and 'delivery_time' keys
            base_charge, cost_per_km, cost_per_minute: Cost factors
        
        Returns:
            list: Route dicts with calculated costs added
        """
        results = []
        
        for route in routes:
            cost_data = CostService.calculate_delivery_cost(
                route.get('distance'),
                route.get('delivery_time'),
                base_charge,
                cost_per_km,
                cost_per_minute
            )
            
            route['calculated_cost'] = cost_data
            results.append(route)
        
        return results


# Convenience function
def calculate_cost(distance, time, base_charge=50, cost_per_km=10, cost_per_minute=2):
    """Convenience function for cost calculation"""
    return CostService.calculate_delivery_cost(distance, time, base_charge, cost_per_km, cost_per_minute)
