import pytest
import sqlite3
import os
from unittest.mock import MagicMock, patch
from src.subscription_manager import add_subscriber, get_all_subscribers, init_db, TABLE_NAME, DB_PATH # Import DB_PATH

@pytest.fixture(autouse=True)
def use_test_db(monkeypatch, tmp_path):
    """
    Fixture to ensure all tests use an isolated, file-based SQLite database.
    """
    # Create a unique temporary database file for this test
    test_db_file = tmp_path / "test_subscriptions.db"
    
    # Patch the DB_PATH in the subscription_manager to point to our test database
    monkeypatch.setattr('src.subscription_manager.DB_PATH', test_db_file)
    
    # Directly patch sqlite3.connect to ensure all connections go to our test_db_file
    # This is more robust as it catches all calls to sqlite3.connect, not just those from a specific module.
    original_sqlite_connect = sqlite3.connect
    def mock_connect(db_path_arg, *args, **kwargs):
        # Always return a connection to our temporary test database for this test's duration
        return original_sqlite_connect(test_db_file, *args, **kwargs)
    
    monkeypatch.setattr(sqlite3, 'connect', mock_connect)

    # Initialize the database and create the table for the test
    init_db()
    
    # Yield control to the test function
    yield
    
    # Clean up the test database file after the test
    if os.path.exists(test_db_file):
        os.remove(test_db_file)

@pytest.fixture
def mock_geolocator(monkeypatch):
    """Fixture to mock the Nominatim geolocator."""
    mock_location = MagicMock()
    mock_location.latitude = 37.7749
    mock_location.longitude = -122.4194
    
    mock_geolocator_instance = MagicMock()
    mock_geolocator_instance.geocode.return_value = mock_location
    
    mock_nominatim = MagicMock(return_value=mock_geolocator_instance)
    monkeypatch.setattr('src.subscription_manager.Nominatim', mock_nominatim)
    
    return mock_nominatim

def test_add_subscriber(mock_geolocator):
    """Test adding a new subscriber."""
    email = "test@example.com"
    location = "San Francisco"
    
    add_subscriber(email, location)
    
    conn = sqlite3.connect(DB_PATH) # Use DB_PATH from src.subscription_manager
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE email = ?", (email,))
    subscriber = cursor.fetchone()
    conn.close()
    
    assert subscriber is not None
    assert subscriber['email'] == email
    assert subscriber['location_name'] == location
    assert subscriber['latitude'] == 37.7749
    assert subscriber['longitude'] == -122.4194

def test_get_all_subscribers(mock_geolocator):
    """Test retrieving all subscribers."""
    # Add some subscribers
    add_subscriber("test1@example.com", "Location 1")
    add_subscriber("test2@example.com", "Location 2")
    
    subscribers = get_all_subscribers()
    
    assert len(subscribers) == 2
    emails = {s['email'] for s in subscribers}
    assert "test1@example.com" in emails
    assert "test2@example.com" in emails

def test_add_subscriber_updates_existing(mock_geolocator):
    """Test that adding a subscriber with an existing email updates the record."""
    email = "update@example.com"
    
    # First subscription
    add_subscriber(email, "Location A")
    
    # Mock a new location for the update
    mock_location_b = MagicMock()
    mock_location_b.latitude = 40.7128
    mock_location_b.longitude = -74.0060
    mock_geolocator().geocode.return_value = mock_location_b
    
    # Second subscription with the same email
    add_subscriber(email, "Location B")
    
    conn = sqlite3.connect(DB_PATH) # Use DB_PATH from src.subscription_manager
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE email = ?", (email,))
    results = cursor.fetchall()
    conn.close()

    # Ensure there is only one record for this email
    assert len(results) == 1
    
    # Check that the details have been updated
    updated_subscriber = dict(zip([c[0] for c in cursor.description], results[0]))
    assert updated_subscriber['location_name'] == "Location B"
    assert updated_subscriber['latitude'] == 40.7128
    assert updated_subscriber['longitude'] == -74.0060
