import pytest
from datetime import datetime, date
from customer import Customer
from flight import FlightSegment, Trip
from filter import (
    CustomerFilter, DurationFilter, LocationFilter, DateFilter,
    TripFilter, ResetFilter
)

# === Helpers ===
def create_segment(fid, dep, arr, dep_time, arr_time):
    return FlightSegment(fid, dep_time, arr_time, 0.1, 1000, dep, arr,
                         ((0.0, 0.0), (1.0, 1.0)))


def create_customer(cid, name, trip_id, segments, trip_date):
    customer = Customer(cid, name, 35, "Canada")
    for seg in segments:
        seg.book_seat(cid, "Economy")
    customer.book_trip(trip_id, [(seg, "Economy") for seg in segments], trip_date)
    return customer


@pytest.fixture
def setup_data():
    dep1 = datetime(2025, 6, 1, 8, 0)
    arr1 = datetime(2025, 6, 1, 10, 0)

    dep2 = datetime(2025, 6, 1, 12, 0)
    arr2 = datetime(2025, 6, 1, 20, 0)

    dep3 = datetime(2025, 6, 2, 9, 0)
    arr3 = datetime(2025, 6, 2, 9, 0)  # Zero duration

    seg1 = create_segment("F1", "YYZ", "JFK", dep1, arr1)
    seg2 = create_segment("F2", "JFK", "LAX", dep2, arr2)
    seg3 = create_segment("F3", "LAX", "SEA", dep3, arr3)

    cust1 = create_customer(111111, "Alice", "R1111", [seg1], date(2025, 6, 1))
    cust2 = create_customer(222222, "Bob", "R2222", [seg2, seg3], date(2025, 6, 2))

    return {
        'customers': [cust1, cust2],
        'segments': [seg1, seg2, seg3],
        'seg1': seg1,
        'seg2': seg2,
        'seg3': seg3
    }

# === CustomerFilter ===
def test_customer_filter_valid(setup_data):
    filt = CustomerFilter()
    res = filt.apply(setup_data['customers'], setup_data['segments'], "111111")
    assert setup_data['seg1'] in res
    assert setup_data['seg2'] not in res

def test_customer_filter_invalid_id(setup_data):
    filt = CustomerFilter()
    res = filt.apply(setup_data['customers'], setup_data['segments'], "000000")
    assert res == setup_data['segments']

def test_customer_filter_non_numeric(setup_data):
    filt = CustomerFilter()
    res = filt.apply(setup_data['customers'], setup_data['segments'], "abc123")
    assert res == setup_data['segments']

# === DurationFilter ===
def test_duration_filter_greater_than(setup_data):
    filt = DurationFilter()
    res = filt.apply(setup_data['customers'], setup_data['segments'], "G0150")
    assert setup_data['seg2'] in res
    assert setup_data['seg1'] not in res

def test_duration_filter_less_than(setup_data):
    filt = DurationFilter()
    res = filt.apply(setup_data['customers'], setup_data['segments'], "L0030")
    assert setup_data['seg3'] in res

def test_duration_filter_invalid_format(setup_data):
    filt = DurationFilter()
    res = filt.apply(setup_data['customers'], setup_data['segments'], "D9999")
    assert res == setup_data['segments']

# === LocationFilter ===
def test_location_filter_departure_valid(setup_data):
    filt = LocationFilter()
    res = filt.apply(setup_data['customers'], setup_data['segments'], "DYYZ")
    assert setup_data['seg1'] in res

def test_location_filter_arrival_valid(setup_data):
    filt = LocationFilter()
    res = filt.apply(setup_data['customers'], setup_data['segments'], "ALAX")
    assert setup_data['seg2'] in res

def test_location_filter_invalid_code(setup_data):
    filt = LocationFilter()
    res = filt.apply(setup_data['customers'], setup_data['segments'], "XYZ")
    assert res == setup_data['segments']

# === DateFilter ===
def test_date_filter_exact_match(setup_data):
    filt = DateFilter()
    res = filt.apply(setup_data['customers'], setup_data['segments'], "2025-06-01/2025-06-02")
    assert setup_data['seg1'] in res

def test_date_filter_range(setup_data):
    filt = DateFilter()
    res = filt.apply(setup_data['customers'], setup_data['segments'], "2025-06-01,2025-06-02")
    assert setup_data['seg1'] in res
    assert setup_data['seg2'] in res

def test_date_filter_invalid_format(setup_data):
    filt = DateFilter()
    res = filt.apply(setup_data['customers'], setup_data['segments'], "01-06-2025/02-06-2025")
    assert res == setup_data['segments']

def test_date_filter_reversed_dates(setup_data):
    filt = DateFilter()
    res = filt.apply(setup_data['customers'], setup_data['segments'], "2025-06-03/2025-06-01")
    assert res == setup_data['segments']

# === TripFilter ===
def test_trip_filter_valid(setup_data):
    filt = TripFilter()
    res = filt.apply(setup_data['customers'], setup_data['segments'], "R1111")
    assert setup_data['seg1'] in res
    assert setup_data['seg2'] not in res

def test_trip_filter_invalid_res_id(setup_data):
    filt = TripFilter()
    res = filt.apply(setup_data['customers'], setup_data['segments'], "RXXXX")
    assert res == []

def test_trip_filter_malformed_input(setup_data):
    filt = TripFilter()
    res = filt.apply(setup_data['customers'], setup_data['segments'], "123")
    assert res == setup_data['segments']

# === ResetFilter ===
def test_reset_filter_returns_all(setup_data):
    filt = ResetFilter()
    res = filt.apply(setup_data['customers'], [], "")
    assert set(res) == set(setup_data['segments'])
