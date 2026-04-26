import pytest
from datetime import datetime, date, timedelta
from customer import Customer
from flight import FlightSegment, Trip

# ---------------------- HELPER FUNCTION -------------------------
def create_segment(length=1000, base_cost=0.1) -> FlightSegment:
    dep_time = datetime(2025, 1, 1, 9, 0)
    arr_time = dep_time + timedelta(hours=2)
    return FlightSegment(
        "FL001",
        dep_time,
        arr_time,
        base_cost,
        length,
        "YYZ",
        "JFK",
        ((-79.6306, 43.6777), (-73.7781, 40.6413))
    )

# ------------------------ UNIT TESTS ----------------------------

def test_initial_customer_state():
    c = Customer(123456, "Jane Doe", 25, "Canada")
    assert c.get_id() == 123456
    assert c.get_ff_status() == ""
    assert c.get_miles() == 0
    assert c.get_trips() == []
    assert c.get_total_flight_costs() == 0.0

def test_single_trip_economy():
    c = Customer(100001, "Alice", 30, "Canada")
    seg = create_segment(length=1000)
    seg.book_seat(100001, "Economy")
    c.book_trip("R001", [(seg, "Economy")], date(2025, 6, 1))
    assert c.get_miles() == 1000
    assert c.get_ff_status() == ""
    assert len(c.get_trips()) == 1

def test_frequent_flyer_threshold_prestige():
    c = Customer(100002, "Bob", 30, "Canada")
    seg = create_segment(length=15000)
    seg.book_seat(100002, "Economy")
    c.book_trip("R002", [(seg, "Economy")], date(2025, 6, 2))
    assert c.get_ff_status() == "Prestige"
    assert c.get_miles() == 15000

def test_discount_applies_only_after_status():
    c = Customer(100003, "Charlie", 40, "Canada")
    seg1 = create_segment(length=15000)
    seg2 = create_segment(length=1000)
    seg1.book_seat(100003, "Economy")
    seg2.book_seat(100003, "Economy")
    c.book_trip("R003", [(seg1, "Economy")], date(2025, 6, 3))
    trip2 = c.book_trip("R004", [(seg2, "Economy")], date(2025, 6, 4))
    base = 0.1 * 1000
    expected_discounted = base * 0.9
    assert pytest.approx(c.get_cost_of_trip(trip2)) == expected_discounted

def test_mixed_class_trip():
    c = Customer(100004, "Dana", 35, "Canada")
    seg1 = create_segment(length=2000)
    seg2 = create_segment(length=1000)
    seg1.book_seat(100004, "Economy")
    seg2.book_seat(100004, "Business")
    c.book_trip("R005", [(seg1, "Economy"), (seg2, "Business")], date(2025, 6, 5))
    assert c.get_miles() == 2000 + 1000 * 5
    assert len(c.get_trips()) == 1

def test_cancel_trip_updates_cost():
    c = Customer(100005, "Eve", 45, "Canada")
    seg = create_segment(length=1000)
    seg.book_seat(100005, "Economy")
    trip = c.book_trip("R006", [(seg, "Economy")], date(2025, 6, 6))
    cost_before = c.get_total_flight_costs()
    trip_cost = c.get_cost_of_trip(trip)
    c.cancel_trip(trip, [(seg, "Economy")])
    expected = cost_before - 100 - trip_cost
    assert c.get_total_flight_costs() == pytest.approx(expected)

def test_cancel_trip_not_found():
    c = Customer(100006, "Frank", 50, "Canada")
    seg = create_segment()
    dummy_trip = Trip("R999", 100006, date(2025, 6, 7), [seg])
    # Should do nothing and not crash
    c.cancel_trip(dummy_trip, [(seg, "Economy")])
    assert c.get_total_flight_costs() == 0.0

def test_get_cost_of_trip_returns_none():
    c = Customer(100007, "Grace", 29, "Canada")
    seg = create_segment()
    dummy_trip = Trip("R888", 100007, date(2025, 6, 8), [seg])
    assert c.get_cost_of_trip(dummy_trip) is None

def test_get_trips_after_multiple_bookings():
    c = Customer(100008, "Henry", 60, "Canada")
    seg1 = create_segment(length=1000)
    seg2 = create_segment(length=2000)
    seg1.book_seat(100008, "Economy")
    seg2.book_seat(100008, "Economy")
    t1 = c.book_trip("R010", [(seg1, "Economy")], date(2025, 6, 10))
    t2 = c.book_trip("R011", [(seg2, "Economy")], date(2025, 6, 11))
    assert set(c.get_trips()) == {t1, t2}

def test_negative_cost_after_cancel():
    c = Customer(100009, "Ivy", 27, "Canada")
    seg = create_segment()
    seg.book_seat(100009, "Economy")
    trip = c.book_trip("R012", [(seg, "Economy")], date(2025, 6, 12))
    c.cancel_trip(trip, [(seg, "Economy")])
    assert c.get_total_flight_costs() < 0
