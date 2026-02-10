import pytest
import pandas as pd
import os
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from src.analyze_and_alert import analyze_and_alert
from src.subscription_manager import add_subscriber, init_db

ALERT_RADIUS_KM = 300

@pytest.fixture
def mock_db_and_fs(tmp_path, monkeypatch):
    """Fixture to create a temporary filesystem and a test database."""
    # Mock filesystem
    silver_dir = tmp_path / "silver"
    gold_dir = tmp_path / "gold"
    silver_dir.mkdir()
    gold_dir.mkdir()

    # Mock database
    test_db_path = tmp_path / "test_subscriptions.db"
    monkeypatch.setattr('src.subscription_manager.DB_PATH', test_db_path)
    init_db()

    return silver_dir, gold_dir, test_db_path

@pytest.fixture
def mock_geolocator(monkeypatch):
    """Fixture to mock geopy without making network calls."""
    # This mock will return different coordinates based on the input location string
    def mock_geocode(location_str):
        mock_loc = MagicMock()
        if location_str == "San Francisco":
            mock_loc.latitude, mock_loc.longitude = 37.77, -122.41 # Near the earthquake
        elif location_str == "London":
            mock_loc.latitude, mock_loc.longitude = 51.50, -0.12 # Far from the earthquake
        else: # Default
            mock_loc.latitude, mock_loc.longitude = 0, 0
        return mock_loc

    mock_geo_instance = MagicMock()
    mock_geo_instance.geocode.side_effect = mock_geocode
    mock_nominatim = MagicMock(return_value=mock_geo_instance)
    monkeypatch.setattr('src.subscription_manager.Nominatim', mock_nominatim)


# Use pytest-asyncio to handle async test functions
@pytest.mark.asyncio
async def test_analyze_and_alert_integration(mock_db_and_fs, mock_geolocator):
    """
    Integration test for the analyze_and_alert workflow.
    - Creates a mock earthquake.
    - Creates two subscribers: one near, one far.
    - Runs the alerting function.
    - Asserts that only the nearby subscriber receives an alert.
    """
    silver_dir, gold_dir, _ = mock_db_and_fs

    # 1. Add subscribers
    add_subscriber("user_near@example.com", "San Francisco")
    add_subscriber("user_far@example.com", "London")

    # 2. Create a mock earthquake data file in the silver directory
    # Earthquake is in Northern California, near San Francisco
    earthquake_data = {
        'id': ['test_eq_001'],
        'time': [pd.to_datetime('2026-02-08T12:00:00Z')],
        'latitude': [38.0],
        'longitude': [-122.0],
        'depth': [10.0],
        'magnitude': [5.5],
        'place': ['Northern California'],
        'tsunami': [0],
        'url': ['http://example.com/test_eq_001']
    }
    df = pd.DataFrame(earthquake_data)
    df.to_parquet(silver_dir / "test_data.parquet")
    
    # 3. Mock the messaging service to capture calls
    with patch('src.analyze_and_alert.send_bulk_alerts') as mock_send_alerts:
        # Make the mock awaitable
        mock_send_alerts.return_value = asyncio.Future()
        mock_send_alerts.return_value.set_result(None)

        # 4. Run the main function
        await analyze_and_alert(silver_dir=str(silver_dir), gold_dir=str(gold_dir))

        # 5. Assertions
        # Check that the messaging service was called
        mock_send_alerts.assert_called_once()
        
        # Get the arguments passed to the mock
        call_args = mock_send_alerts.call_args[0][0]
        
        # There should be exactly one notification
        assert len(call_args) == 1
        
        # The notification should be for the 'nearby' user
        alerted_email, _ = call_args[0]
        assert alerted_email == "user_near@example.com"

        # Check that the gold layer file was created
        assert (gold_dir / "test_data.parquet").exists()

        # Check that the alert log was updated
        log_file = gold_dir / "alerted_earthquakes.log"
        assert log_file.exists()
        with open(log_file, 'r') as f:
            content = f.read()
            assert "test_eq_001" in content