import os
import pytest
import pandas as pd
import json
from src.process_data import process_bronze_to_silver

@pytest.fixture
def sample_bronze_data():
    """Provides a sample raw earthquake data dictionary."""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "mag": 1.5,
                    "place": "10km NE of The Geysers, CA",
                    "time": 1672531200000, # 2023-01-01 00:00:00 UTC
                    "url": "http://example.com/1",
                    "tsunami": 0
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [-122.7, 38.8, 1.0]
                },
                "id": "test1"
            },
            {
                "type": "Feature",
                "properties": {
                    "mag": 5.2,
                    "place": "20km S of Pāhala, Hawaii",
                    "time": 1672534800000, # 2023-01-01 01:00:00 UTC
                    "url": "http://example.com/2",
                    "tsunami": 1
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [-155.5, 19.1, 32.8]
                },
                "id": "test2"
            }
        ]
    }

def test_process_bronze_to_silver(tmpdir, sample_bronze_data):
    """
    Tests the data processing from bronze to silver layer.
    
    Args:
        tmpdir: A pytest fixture that provides a temporary directory for this test run.
        sample_bronze_data: Our sample raw data defined above.
    """
    bronze_dir = tmpdir.mkdir("bronze")
    silver_dir = tmpdir.mkdir("silver")
    archive_dir = os.path.join(bronze_dir, "archive")

    raw_json_path = bronze_dir.join("earthquake_data_test.json")
    with open(raw_json_path, 'w') as f:
        json.dump(sample_bronze_data, f)

    process_bronze_to_silver(bronze_dir=str(bronze_dir), silver_dir=str(silver_dir))

    silver_files = os.listdir(str(silver_dir))
    assert len(silver_files) == 1, "Should create one silver file"
    assert silver_files[0] == "earthquake_data_test.parquet"

    archived_files = os.listdir(str(archive_dir))
    assert len(archived_files) == 1, "Should archive the bronze file"
    assert archived_files[0] == "earthquake_data_test.json"
    
    result_df = pd.read_parquet(os.path.join(silver_dir, silver_files[0]))
    
    assert len(result_df) == 2, "Silver DataFrame should have two records"
    assert 'id' in result_df.columns
    assert 'magnitude' in result_df.columns
    assert 'place' in result_df.columns
    assert 'time' in result_df.columns
    assert 'url' in result_df.columns
    assert 'tsunami' in result_df.columns
    assert 'longitude' in result_df.columns
    assert 'latitude' in result_df.columns
    assert 'depth' in result_df.columns
    
    assert result_df.iloc[1]['magnitude'] == 5.2
    assert result_df.iloc[1]['place'] == "20km S of Pāhala, Hawaii"

def test_process_empty_bronze_directory(tmpdir):
    """
    Tests that the script runs without error and does nothing
    when the bronze directory is empty.
    """
    bronze_dir = tmpdir.mkdir("bronze")
    silver_dir = tmpdir.mkdir("silver")
    archive_dir = os.path.join(bronze_dir, "archive")

    process_bronze_to_silver(bronze_dir=str(bronze_dir), silver_dir=str(silver_dir))

    assert len(os.listdir(str(silver_dir))) == 0
    assert len(os.listdir(str(archive_dir))) == 0

