import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock # MagicMock is needed for smtplib mocking
from src.analyze_and_alert import analyze_and_alert

@pytest.fixture
def sample_silver_data():
    """Provides a sample processed data dictionary for the 'silver' layer."""
    return pd.DataFrame({
        'id': ['test1', 'test2', 'test3'],
        'magnitude': [4.5, 5.5, 6.0],
        'place': ['Location A', 'Location B (Significant)', 'Location C (Significant)'],
        'time': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03']),
        'url': ['http://example.com/1', 'http://example.com/2', 'http://example.com/3'],
        'tsunami': [0, 1, 0]
    })

@pytest.fixture
def mock_email_config():
    """Provides a mock email configuration for SMTP."""
    return {
        'smtp_host': 'smtp.test.com',
        'smtp_port': 587,
        'smtp_username': 'test_user',
        'smtp_password': 'test_password',
        'sender_email': 'test@example.com',
        'recipient_emails': ['recipient@example.com']
    }

@patch('src.analyze_and_alert.smtplib.SMTP')
def test_new_significant_earthquake_sends_alert(mock_smtp, tmpdir, monkeypatch, sample_silver_data, mock_email_config):
    """
    Tests that an email alert is sent for a new significant earthquake (mag >= 5.0).
    """
    silver_dir = tmpdir.mkdir("silver")
    gold_dir = tmpdir.mkdir("gold")
    
    monkeypatch.setattr('src.analyze_and_alert.get_email_config', lambda: mock_email_config)
    
    silver_file_path = silver_dir.join("silver_data.parquet")
    sample_silver_data.to_parquet(silver_file_path, index=False)
    
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    analyze_and_alert(silver_dir=str(silver_dir), gold_dir=str(gold_dir))

    gold_file = os.path.join(gold_dir, "silver_data.parquet")
    assert os.path.exists(gold_file)
    gold_df = pd.read_parquet(gold_file)
    assert len(gold_df) == 2
    assert all(gold_df['magnitude'] >= 5.0)

    log_file = os.path.join(gold_dir, "alerted_earthquakes.log")
    assert os.path.exists(log_file)
    with open(log_file, 'r') as f:
        alerted_ids = f.read().splitlines()
    assert len(alerted_ids) == 2

    assert mock_smtp.called, "Should have tried to connect to an SMTP server"
    assert mock_server.starttls.call_count == 2
    assert mock_server.login.call_count == 2
    assert mock_server.sendmail.call_count == 2

@patch('src.analyze_and_alert.smtplib.SMTP')
def test_old_significant_earthquake_does_not_send_alert(mock_smtp, tmpdir, monkeypatch, sample_silver_data, mock_email_config):
    """
    Tests that an email alert is NOT sent for a significant earthquake
    that has already been logged.
    """
    silver_dir = tmpdir.mkdir("silver")
    gold_dir = tmpdir.mkdir("gold")

    monkeypatch.setattr('src.analyze_and_alert.get_email_config', lambda: mock_email_config)

    silver_file_path = silver_dir.join("silver_data.parquet")
    sample_silver_data.to_parquet(silver_file_path, index=False)
    
    log_file = os.path.join(gold_dir, "alerted_earthquakes.log")
    with open(log_file, 'w') as f:
        f.write("test2\n")

    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server
    
    analyze_and_alert(silver_dir=str(silver_dir), gold_dir=str(gold_dir))

    with open(log_file, 'r') as f:
        alerted_ids = f.read().splitlines()
    assert len(alerted_ids) == 2
    
    mock_server.login.assert_called_once()
    mock_server.sendmail.assert_called_once()

@patch('src.analyze_and_alert.smtplib.SMTP')
def test_no_significant_earthquakes_to_report(mock_smtp, tmpdir, monkeypatch, mock_email_config):
    """
    Tests that no alerts are sent and no gold file is created when there
    are no significant earthquakes.
    """
    silver_dir = tmpdir.mkdir("silver")
    gold_dir = tmpdir.mkdir("gold")

    monkeypatch.setattr('src.analyze_and_alert.get_email_config', lambda: mock_email_config)

    non_significant_data = pd.DataFrame({
        'id': ['test1', 'test4'],
        'magnitude': [4.5, 3.2],
        'place': ['Location A', 'Location D'],
        'time': pd.to_datetime(['2023-01-01', '2023-01-04']),
        'url': ['http://example.com/1', 'http://example.com/4'],
        'tsunami': [0, 0]
    })
    silver_file_path = silver_dir.join("silver_data.parquet")
    non_significant_data.to_parquet(silver_file_path, index=False)

    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    analyze_and_alert(silver_dir=str(silver_dir), gold_dir=str(gold_dir))

    gold_files = os.listdir(str(gold_dir))
    assert len(gold_files) == 0

    mock_server.sendmail.assert_not_called()

