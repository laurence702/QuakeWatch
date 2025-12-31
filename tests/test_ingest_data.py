import os
import pytest
import json
import requests
from unittest.mock import patch
from src.ingest_data import ingest_from_usgs


@patch('src.ingest_data.requests.get')
def test_ingestion_creates_bronze_file(mock_requests_get, tmpdir):
    fake_api_response = {"message": "This is fake data"}

    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.return_value = fake_api_response

    tmp_bronze_dir = tmpdir.mkdir("bronze")

    ingest_from_usgs(bronze_dir=str(tmp_bronze_dir))

    mock_requests_get.assert_called_once()

    created_files = os.listdir(str(tmp_bronze_dir))
    assert len(created_files) > 0, "No files created in the bronze layer"

    with open(os.path.join(str(tmp_bronze_dir), created_files[0]), 'r') as f:
        content = json.load(f)
    assert content == fake_api_response

@patch('src.ingest_data.requests.get')
def test_ingest_api_failure_handles_gracefully(mock_requests_get, tmpdir):
    """
    Tests that the ingest function handles an API failure gracefully.
    """
    mock_requests_get.side_effect = requests.exceptions.RequestException("API is down")

    tmp_bronze_dir = tmpdir.mkdir("bronze")

    ingest_from_usgs(bronze_dir=str(tmp_bronze_dir))

    created_files = os.listdir(str(tmp_bronze_dir))
    assert len(created_files) == 0, "Should not create any files on API failure"
