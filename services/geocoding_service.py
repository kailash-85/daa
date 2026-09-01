"""
Geocoding service for location lookup and reverse geocoding.
Uses Nominatim (OpenStreetMap) as primary, with fallback support for Google Maps.
"""

import requests
from geopy.geocoders import Nominatim, GoogleV3
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import os
from functools import lru_cache

class GeocodingService:
    """Handle location geocoding and reverse geocoding"""
    
    def __init__(self):
        self.nominatim_user_agent = os.environ.get('NOMINATIM_USER_AGENT', 'delivery-calculator')
        self.google_api_key = os.environ.get('GOOGLE_MAPS_API_KEY', '')
        self.geocoder = Nominatim(user_agent=self.nominatim_user_agent)
    
    def geocode_location(self, query):
        """
        Geocode location name to coordinates.
        
        Args:
            query: Location name or address
        
        Returns:
            dict: {
                'name': str,
                'address': str,
                'latitude': float,
                'longitude': float,
                'success': bool,
                'error': str or None
            }
        """
        try:
            location = self.geocoder.geocode(query, timeout=10)
            
            if location:
                return {
                    'name': query,
                    'address': location.address,
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'success': True,
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'error': f'Location "{query}" not found'
                }
        
        except GeocoderTimedOut:
            return {
                'success': False,
                'error': 'Geocoding service timed out. Please try again.'
            }
        except GeocoderServiceError as e:
            return {
                'success': False,
                'error': f'Geocoding service error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Geocoding failed: {str(e)}'
            }
    
    def reverse_geocode(self, latitude, longitude):
        """
        Reverse geocode coordinates to address.
        
        Args:
            latitude: Latitude
            longitude: Longitude
        
        Returns:
            dict: {
                'address': str,
                'latitude': float,
                'longitude': float,
                'success': bool,
                'error': str or None
            }
        """
        try:
            location = self.geocoder.reverse(f"{latitude}, {longitude}", timeout=10)
            
            if location:
                return {
                    'address': location.address,
                    'latitude': latitude,
                    'longitude': longitude,
                    'success': True,
                    'error': None
                }
            else:
                return {
                    'address': f'({latitude}, {longitude})',
                    'latitude': latitude,
                    'longitude': longitude,
                    'success': True,
                    'error': None
                }
        
        except GeocoderTimedOut:
            return {
                'success': False,
                'error': 'Reverse geocoding timed out'
            }
        except Exception as e:
            # Return coordinates as fallback
            return {
                'address': f'({latitude}, {longitude})',
                'latitude': latitude,
                'longitude': longitude,
                'success': True,
                'error': None
            }
    
    def search_locations(self, query, limit=5):
        """
        Search for multiple location matches.
        
        Args:
            query: Search query
            limit: Maximum results
        
        Returns:
            list: List of matching locations
        """
        try:
            locations = self.geocoder.geocode(query, timeout=10, exactly_one=False)
            
            if not locations:
                return []
            
            results = []
            for loc in locations[:limit]:
                results.append({
                    'name': query,
                    'address': loc.address,
                    'latitude': loc.latitude,
                    'longitude': loc.longitude
                })
            
            return results
        
        except Exception as e:
            return []


class RoutingService:
    """Handle route finding and distance/time calculation"""
    
    def __init__(self):
        self.base_url = "http://router.project-osrm.org/route/v1/driving"
    
    def get_route(self, source_lat, source_lon, dest_lat, dest_lon):
        """
        Get route information between two points using OSRM.
        
        Args:
            source_lat, source_lon: Starting point coordinates
            dest_lat, dest_lon: Destination coordinates
        
        Returns:
            dict: {
                'distance': float (km),
                'duration': int (minutes),
                'geometry': encoded polyline or geojson,
                'success': bool,
                'error': str or None
            }
        """
        try:
            url = f"{self.base_url}/{source_lon},{source_lat};{dest_lon},{dest_lat}"
            params = {
                'overview': 'full',
                'geometries': 'polyline',
                'steps': 'false',
                'continue_straight': 'default'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('code') == 'Ok' and data.get('routes'):
                    route = data['routes'][0]
                    
                    return {
                        'distance': round(route['distance'] / 1000, 2),  # Convert to km
                        'duration': round(route['duration'] / 60),  # Convert to minutes
                        'geometry': route.get('geometry', ''),
                        'success': True,
                        'error': None
                    }
                else:
                    return {
                        'success': False,
                        'error': 'No route found between locations'
                    }
            else:
                return {
                    'success': False,
                    'error': f'Routing service returned status {response.status_code}'
                }
        
        except requests.Timeout:
            return {
                'success': False,
                'error': 'Routing service timed out'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Routing failed: {str(e)}'
            }
    
    def get_distance(self, source_lat, source_lon, dest_lat, dest_lon):
        """Get distance between two points"""
        result = self.get_route(source_lat, source_lon, dest_lat, dest_lon)
        
        if result['success']:
            return result['distance']
        else:
            # Fallback: straight-line distance approximation
            return self._haversine_distance(source_lat, source_lon, dest_lat, dest_lon)
    
    @staticmethod
    def _haversine_distance(lat1, lon1, lat2, lon2):
        """Calculate approximate distance using Haversine formula (in km)"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in km
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return round(R * c, 2)


# Create singleton instances
geocoding_service = GeocodingService()
routing_service = RoutingService()
