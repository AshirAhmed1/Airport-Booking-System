import pytest
import datetime
from flight import Trip, FlightSegment

# === Fixtures ===

@pytest.fixture
def sample_segments():
    """Returns a list of two FlightSegments with realistic timings."""
    seg1 = FlightSegment(
        fid="PA-100",
        dep=datetime.datetime(2024, 1, 1, 6, 0),
        arr=datetime.datetime(2024, 1, 1, 9, 0),
        base_cost=100.0,
        length=1500,
        dep_loc="YYZ",
        arr_loc="JFK",
        long_lat=((0.0, 0.0), (1.0, 1.0))
    )
    seg2 = FlightSegment(
        fid="PA-101",
        dep=datetime.datetime(2024, 1, 1, 10, 30),
        arr=datetime.datetime(2024, 1, 1, 15, 0),
        base_cost=150.0,
        length=3000,
        dep_loc="JFK",
        arr_loc="LHR",
        long_lat=((1.0, 1.0), (2.0, 2.0))
    )
    return [seg1, seg2]


@pytest.fixture
def sample_trip(sample_segments):
    return Trip(
        rid="R12345",
        cid=999999,
        trip_date=datetime.date(2024, 1, 1),
        flight_segments=sample_segments
    )


# === Tests ===

def test_trip_initialization(sample_trip):
    assert sample_trip.reservation_id == "R12345"
    assert sample_trip.customer_id == 999999
    assert sample_trip.trip_departure == datetime.date(2024, 1, 1)


def test_get_flight_segments(sample_trip, sample_segments):
    assert sample_trip.get_flight_segments() == sample_segments


def test_get_reservation_id(sample_trip):
    assert sample_trip.get_reservation_id() == "R12345"


def test_in_flight_time(sample_trip):
    # seg1: 3 hours, seg2: 4.5 hours => 270 + 90 = 360 + 90 = 450 mins
    assert sample_trip.get_in_flight_time() == 450  # 3h + 4.5h


def test_total_trip_time(sample_trip):
    # From 06:00 to 15:00 = 9 hours = 540 minutes
    assert sample_trip.get_total_trip_time() == 540


def test_single_flight_trip_time():
    """Edge case: 1 flight segment trip"""
    seg = FlightSegment(
        fid="PA-001",
        dep=datetime.datetime(2024, 6, 1, 12, 0),
        arr=datetime.datetime(2024, 6, 1, 14, 45),
        base_cost=200.0,
        length=1200,
        dep_loc="YYZ",
        arr_loc="ORD",
        long_lat=((0.0, 0.0), (1.0, 1.0))
    )
    trip = Trip("R0001", 123456, datetime.date(2024, 6, 1), [seg])
    assert trip.get_in_flight_time() == 165  # 2h 45min
    assert trip.get_total_trip_time() == 165


def test_disordered_segments_resolve_correctly():
    """Trip segments out of order still calculate total correctly"""
    seg1 = FlightSegment(
        fid="PA-A",
        dep=datetime.datetime(2024, 5, 1, 10),
        arr=datetime.datetime(2024, 5, 1, 13),
        base_cost=100,
        length=1000,
        dep_loc="A", arr_loc="B", long_lat=((0, 0), (1, 1))
    )
    seg2 = FlightSegment(
        fid="PA-B",
        dep=datetime.datetime(2024, 5, 1, 7),
        arr=datetime.datetime(2024, 5, 1, 9),
        base_cost=100,
        length=1000,
        dep_loc="B", arr_loc="C", long_lat=((1, 1), (2, 2))
    )
    trip = Trip("R9999", 1, datetime.date(2024, 5, 1), [seg1, seg2])
    assert trip.get_total_trip_time() == 360  # from 7:00 to 13:00
    assert trip.get_in_flight_time() == 5 * 60  # 2h + 3h = 300
