import datetime
import pytest
from flight import FlightSegment


# === Shared Fixture ===
@pytest.fixture
def sample_flight():
    dep = datetime.datetime(2019, 1, 1, 12, 59)
    arr = datetime.datetime(2019, 1, 1, 22, 54)
    long_lat = ((-79.6306, 43.6772), (2.55, 49.0083))
    return FlightSegment("PA-001", dep, arr, 0.1225 * 9143, 9143.0, "YYZ", "CDG", long_lat)


# === Basic Getters ===

def test_get_fid(sample_flight):
    assert sample_flight.get_fid() == "PA-001"

def test_get_length(sample_flight):
    assert sample_flight.get_length() == 9143.0

def test_get_base_fare_cost(sample_flight):
    assert round(sample_flight.get_base_fare_cost(), 2) == round(0.1225 * 9143, 2)

def test_get_dep_and_arr(sample_flight):
    assert sample_flight.get_dep() == "YYZ"
    assert sample_flight.get_arr() == "CDG"

def test_get_times(sample_flight):
    dep, arr = sample_flight.get_times()
    assert dep == datetime.datetime(2019, 1, 1, 12, 59)
    assert arr == datetime.datetime(2019, 1, 1, 22, 54)

def test_get_duration(sample_flight):
    duration = sample_flight.get_duration()
    assert isinstance(duration, datetime.time)
    assert duration.hour == 9
    assert duration.minute == 55

def test_get_long_lat(sample_flight):
    assert sample_flight.get_long_lat() == ((-79.6306, 43.6772), (2.55, 49.0083))


# === Manifest & Seat Booking ===

def test_initial_seat_availability(sample_flight):
    assert sample_flight.seat_capacity == {"Economy": 150, "Business": 22}
    assert sample_flight.seat_availability["Economy"] == 150

def test_book_seat_first_time(sample_flight):
    sample_flight.book_seat(123456, "Economy")
    assert sample_flight.check_manifest(123456)
    assert sample_flight.check_seat_class(123456) == "Economy"
    assert sample_flight.seat_availability["Economy"] == 149

def test_book_same_customer_twice_same_class(sample_flight):
    sample_flight.book_seat(999, "Economy")
    before = sample_flight.seat_availability["Economy"]
    sample_flight.book_seat(999, "Economy")
    after = sample_flight.seat_availability["Economy"]
    assert before == after

def test_change_class_if_available(sample_flight):
    sample_flight.book_seat(1, "Economy")
    sample_flight.book_seat(1, "Business")
    assert sample_flight.check_seat_class(1) == "Business"
    assert sample_flight.seat_availability["Economy"] == 150  # released
    assert sample_flight.seat_availability["Business"] == 21  # reduced

def test_cannot_change_to_full_class():
    f = FlightSegment("PA-002", datetime.datetime(2024, 1, 1, 10),
                      datetime.datetime(2024, 1, 1, 12), 100.0,
                      1000.0, "JFK", "LHR", ((-73.7781, 40.6413), (0.4543, 51.4700)))
    # Fill business
    for cid in range(1001, 1023):
        f.book_seat(cid, "Business")
    f.book_seat(1000, "Economy")
    f.book_seat(1000, "Business")  # Should NOT change
    assert f.check_seat_class(1000) == "Economy"

def test_cancel_seat(sample_flight):
    sample_flight.book_seat(777, "Business")
    assert sample_flight.check_manifest(777)
    sample_flight.cancel_seat(777)
    assert not sample_flight.check_manifest(777)
    assert sample_flight.seat_availability["Business"] == 22


def test_cancel_nonexistent_seat_does_nothing(sample_flight):
    before = sample_flight.seat_availability["Business"]
    sample_flight.cancel_seat(404)
    after = sample_flight.seat_availability["Business"]
    assert before == after
