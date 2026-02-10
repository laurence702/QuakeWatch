import pytest
from src.utils.geo import haversine_distance

def test_haversine_distance():
    """
    Test the haversine_distance function with known locations.
    Distance between Paris, France and New York, USA.
    """
    # Coordinates for Paris, France
    lat1, lon1 = 48.8566, 2.3522
    
    # Coordinates for New York, USA
    lat2, lon2 = 40.7128, -74.0060
    
    # Expected distance is approximately 5837 km.
    # We will check if the result is within a certain tolerance.
    expected_distance_km = 5837
    tolerance_km = 10 # Allow for small variations in Earth radius assumptions

    calculated_distance = haversine_distance(lat1, lon1, lat2, lon2)
    
    assert abs(calculated_distance - expected_distance_km) < tolerance_km

def test_haversine_distance_zero():
    """Test that the distance between a point and itself is zero."""
    lat, lon = 48.8566, 2.3522
    assert haversine_distance(lat, lon, lat, lon) == 0
