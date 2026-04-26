import pytest
from airport import Airport

# --- Test Data ---
SAMPLE_ID = "YYZ"
SAMPLE_NAME = "Lester B. Pearson International Airport"
SAMPLE_LOCATION = (-79.63059998, 43.67720032)


def test_airport_creation():
    """Test that Airport object is initialized correctly."""
    airport = Airport(SAMPLE_ID, SAMPLE_NAME, SAMPLE_LOCATION)
    assert airport.get_airport_id() == SAMPLE_ID
    assert airport.get_name() == SAMPLE_NAME
    assert airport.get_location() == SAMPLE_LOCATION


def test_airport_id_format():
    """Test airport ID format (should be 3 characters)."""
    airport = Airport("LAX", "Los Angeles International Airport", (-118.4085, 33.9416))
    assert len(airport.get_airport_id()) == 3
    assert airport.get_airport_id().isalpha()


def test_airport_location_edge_values():
    """Test valid edge values for location coordinates."""
    airport = Airport("XYZ", "Extreme Airport", (-180.0, 90.0))
    lon, lat = airport.get_location()
    assert -180.0 <= lon <= 180.0
    assert -90.0 <= lat <= 90.0


def test_multiple_airports_dont_clash():
    """Test that multiple airports can coexist independently."""
    toronto = Airport("YYZ", "Toronto", (-79.63, 43.67))
    dubai = Airport("DXB", "Dubai", (55.3644, 25.2532))
    assert toronto.get_airport_id() != dubai.get_airport_id()
    assert toronto.get_location() != dubai.get_location()


def test_airport_repr_data():
    """Check airport stores correct types of data."""
    airport = Airport(SAMPLE_ID, SAMPLE_NAME, SAMPLE_LOCATION)
    assert isinstance(airport.get_airport_id(), str)
    assert isinstance(airport.get_name(), str)
    assert isinstance(airport.get_location(), tuple)
    assert isinstance(airport.get_location()[0], float)
    assert isinstance(airport.get_location()[1], float)


# === Additional Edge Case Tests ===

def test_airport_id_unusual_length():
    """Test behavior with unusual airport ID length."""
    airport = Airport("ABCDE", "Test Airport", (0.0, 0.0))
    assert airport.get_airport_id() == "ABCDE"


def test_airport_location_precision():
    """Test very high-precision coordinate values."""
    precise_location = (-123.1234567890123456, 49.9876543210987654)
    airport = Airport("YVR", "Vancouver", precise_location)
    assert airport.get_location() == precise_location


def test_airport_empty_name():
    """Test an airport with an empty string name."""
    airport = Airport("XXX", "", (0.0, 0.0))
    assert airport.get_name() == ""
