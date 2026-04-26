import pytest
import datetime
from application import (
    import_data,
    create_airports,
    create_customers,
    create_flight_segments,
    load_trips,
    _parse_itinerary,
    AIRPORT_LOCATIONS
)


@pytest.fixture
def raw_data():
    return import_data(
        "data/airports.csv",
        "data/customers.csv",
        "data/segments_small.csv",
        "data/trips_small.csv"
    )


def test_airports_created(raw_data):
    airports_data = raw_data[0]
    airports = create_airports(airports_data)
    assert isinstance(airports, list)
    assert all(a.get_airport_id() in AIRPORT_LOCATIONS for a in airports)
    assert all(isinstance(a.get_location(), tuple) for a in airports)
    assert all(len(a.get_airport_id()) == 3 for a in airports)


def test_customers_created(raw_data):
    customer_data = raw_data[2]
    customers = create_customers(customer_data)
    assert isinstance(customers, dict)
    assert all(isinstance(cid, int) for cid in customers)
    assert all(customers[cid].get_id() == cid for cid in customers)


def test_flight_segments_created(raw_data):
    create_airports(raw_data[0])  # Needed for AIRPORT_LOCATIONS
    seg_data = raw_data[1]
    segs = create_flight_segments(seg_data)
    assert isinstance(segs, dict)
    assert all(isinstance(k, datetime.date) for k in segs)
    total_segs = sum(len(lst) for lst in segs.values())
    assert total_segs > 0


def test_flight_segments_multiple_same_day(raw_data):
    create_airports(raw_data[0])
    segs = create_flight_segments(raw_data[1])
    for date, flights in segs.items():
        if len(flights) > 1:
            assert isinstance(flights[0], type(flights[1]))


def test_trips_loaded(raw_data):
    create_airports(raw_data[0])
    segs = create_flight_segments(raw_data[1])
    customers = create_customers(raw_data[2])
    trips = load_trips(raw_data[3], customers, segs)
    assert isinstance(trips, list)
    assert all(trip.get_reservation_id() for trip in trips)
    assert all(len(trip.get_flight_segments()) >= 1 for trip in trips)


def test_itinerary_parser():
    parsed = _parse_itinerary("[('YYZ','Economy'),('CDG','Business')]")
    assert parsed == [('YYZ', 'Economy'), ('CDG', 'Business')]


def test_itinerary_parser_empty():
    assert _parse_itinerary("[]") == []


def test_itinerary_parser_malformed():
    # Should not crash on bad input; just return partial or empty
    result = _parse_itinerary("[('YYZ''Economy'),('CDG')]")
    assert isinstance(result, list)
    assert all(isinstance(t, tuple) for t in result or [])


def test_trips_skip_invalid_customer(raw_data):
    create_airports(raw_data[0])
    segs = create_flight_segments(raw_data[1])
    customers = create_customers(raw_data[2])
    # Inject a fake row with non-existent customer
    bad_trip = [["XYZ12", "999999", "2019-01-01", "[('YYZ','Economy'),('CDG','Economy')]"]]
    trips = load_trips(bad_trip, customers, segs)
    assert trips == []


def test_trips_skip_if_no_flight_match(raw_data):
    create_airports(raw_data[0])
    segs = create_flight_segments(raw_data[1])
    customers = create_customers(raw_data[2])
    # Destination that doesn't exist
    bad_trip = [["XYZ13", list(customers.keys())[0], "2019-01-01", "[('XXX','Economy'),('YYY','Economy')]"]]
    trips = load_trips(bad_trip, customers, segs)
    assert trips == []


def test_airport_location_map_not_empty(raw_data):
    create_airports(raw_data[0])
    assert isinstance(AIRPORT_LOCATIONS, dict)
    assert all(len(k) == 3 and isinstance(v, tuple) for k, v in AIRPORT_LOCATIONS.items())
