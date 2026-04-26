"""
UTM:CSC148, Summer 2025
Assignment 1

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2025 Bogdan Simion, Michael Liut, Paul Vrbik
"""
import csv
import datetime
from typing import Dict, List, Tuple, Optional

from airport import Airport
from customer import Customer
from flight import Trip, FlightSegment
from visualizer import Visualizer

#############################################
# DO NOT DECLARE ANY OTHER GLOBAL VARIABLES!
#############################################

# AIRPORT_LOCATIONS: global mapping of an airport's IATA with their respective
#                    longitude and latitude positions.
# NOTE: This is used for our testing purposes, so it has to be populated in
# create_airports(), but you are welcome to use it as you see fit.
AIRPORT_LOCATIONS = {}

# DEFAULT_BASE_COST: Default rate per km for the base cost of a flight segment.
DEFAULT_BASE_COST = 0.1225


# Helper Functions
def _parse_itinerary(string: str) -> List[Tuple[str, str]]:
    """Convert a string representation of an itinerary
    from the csv into a list of (IATA, seat_type) tuples."""

    rem_brackets = string[1:-1]
    seg = rem_brackets.split("),(")
    results = []
    for x in seg:
        x = x.strip("()")
        x = x.replace("'", "")
        z = x.split(",")
        if len(z) == 2:
            results.append((z[0].strip(), z[1].strip()))
    return results


def _matching_flights(dep_time: datetime.datetime,
                      flights_date: Dict[datetime.date, List[FlightSegment]],
                      matches: List[FlightSegment],
                      dep: str, arr: str) -> None:
    """Find all available flights departing from
    dep to arr on or after dep_time"""

    date_to_check = dep_time.date()

    while date_to_check in flights_date:
        for x in flights_date[date_to_check]:
            if (x.get_dep() == dep
                    and x.get_arr() == arr
                    and x.get_times()[0] >= dep_time):
                matches.append(x)
        date_to_check += datetime.timedelta(days=1)


def _build_segments(itinerary: List[Tuple[str, str]],
                    customer_id: int,
                    trip_date: datetime.date,
                    flight_segments: Dict[datetime.date, List[FlightSegment]])\
        -> Optional[List[Tuple[FlightSegment, str]]]:
    """Try to build the trip segment list by checking
    valid flights and booking them."""
    flight_segm = []
    curr = datetime.datetime.combine(trip_date, datetime.time.min)
    i = 0

    while i < len(itinerary) - 1:
        z = []
        dep_loc = itinerary[i][0]
        arr_loc = itinerary[i + 1][0]
        seat_type = itinerary[i][1]
        _matching_flights(curr, flight_segments, z,
                          dep_loc, arr_loc)
        if not z:
            return None
        earliest = z[0]
        for x in z[1:]:
            if x.get_times()[0] < earliest.get_times()[0]:
                earliest = x
        earliest.book_seat(customer_id, seat_type)
        flight_segm.append((earliest, seat_type))
        curr = earliest.get_times()[1]
        i += 1
    return flight_segm


def import_data(file_airports: str, file_customers: str, file_segments: str,
                file_trips: str) \
        -> Tuple[List[List[str]], List[List[str]],
                 List[List[str]], List[List[str]]]:
    """ Opens all the data files <data/filename.csv> which stores the CSV data,
        and returns a tuple of lists of lists of strings. This contains the
        read in data, line-by-line, (airports, customers, flights, trips).

        Precondition: the dataset file must be in CSV format.
    """

    airport_log, customer_log, flight_log, trip_log = [], [], [], []

    airport_data = csv.reader(open(file_airports))
    customer_data = csv.reader(open(file_customers))
    flight_data = csv.reader(open(file_segments))
    trip_data = csv.reader(open(file_trips))

    for row in airport_data:
        airport_log.append(row)

    for row in flight_data:
        flight_log.append(row)

    for row in customer_data:
        customer_log.append(row)

    for row in trip_data:
        trip_log.append(row)

    return airport_log, flight_log, customer_log, trip_log


def create_customers(log: List[List[str]]) -> Dict[int, Customer]:
    """ Returns a dictionary of Customer IDs and their Customer instances,
    based on the customers from the input dataset from the <log>.

    Precondition:
        - The <log> list contains the input data in the correct format.
    """

    new_dict = {}
    for x in log:
        customer_id = int(x[0])
        name = x[1]
        age = int(x[2])
        nationality = x[3]
        z = Customer(customer_id, name, age, nationality)
        new_dict[customer_id] = z
    return new_dict


def create_flight_segments(log: List[List[str]]) \
        -> Dict[datetime.date, List[FlightSegment]]:
    """ Returns a dictionary storing all FlightSegments, indexed by their
    departure date, based on the input dataset stored in the <log>.

    Precondition:
    - The <log> list contains the input data in the correct format.
    """
    new_dict = {}
    for x in log:
        fid = x[0]
        dep_time = datetime.datetime.strptime(x[4], "%H:%M").time()
        arr_time = datetime.datetime.strptime(x[5], "%H:%M").time()
        date_of_flight = datetime.datetime.strptime(x[3], "%Y:%m:%d").date()
        base_cost = DEFAULT_BASE_COST
        length = float(x[6])
        dep_loc = x[1]
        arr_loc = x[2]
        long_lat = (AIRPORT_LOCATIONS[dep_loc], AIRPORT_LOCATIONS[arr_loc])
        dep = datetime.datetime.combine(date_of_flight, dep_time)
        arr = datetime.datetime.combine(date_of_flight, arr_time)

        if arr < dep:
            arr += datetime.timedelta(days=1)

        z = FlightSegment(fid=fid, dep=dep, arr=arr,
                          base_cost=base_cost, length=length, dep_loc=dep_loc,
                          arr_loc=arr_loc, long_lat=long_lat)

        if date_of_flight not in new_dict:
            new_dict[date_of_flight] = [z]
        else:
            new_dict[date_of_flight].append(z)

    return new_dict


def create_airports(log: List[List[str]]) -> List[Airport]:
    """ Return a list of Airports with all applicable data, based
    on the input dataset stored in the <log>.

    Precondition:
    - The <log> list contains the input data in the correct format.
    """

    air_port_list = []
    for x in log:
        aid = x[0]
        name = x[1]
        location = (float(x[2]), float(x[3]))
        AIRPORT_LOCATIONS[aid] = location
        z = Airport(aid=aid, name=name, location=location)
        air_port_list.append(z)
    return air_port_list


def load_trips(log: List[List[str]], customer_dict: Dict[int, Customer],
               flight_segments: Dict[datetime.date, List[FlightSegment]]) \
        -> List[Trip]:
    """ Creates the Trip objects and makes the bookings.

    Preconditions:
    - The <log> list contains the input data in the correct format.
    - the customers are already correctly stored in the <customer_dict>,
    indexed by their customer ID.
    - the flight segments are already correctly stored in the
    <flight_segments>, indexed by their departure date
    """
    new_list = []
    for x in log:
        reservation_id = x[0]
        if reservation_id != "None":
            customer_id = int(x[1])
            trip_departure = datetime.datetime.strptime(x[2], "%Y-%m-%d").date()
            z = ','.join(x[3:]).strip()
            itinerary = _parse_itinerary(z)
            if customer_id in customer_dict:
                customer = customer_dict[customer_id]
                flight_segm = _build_segments(itinerary, customer_id,
                                              trip_departure, flight_segments)
                if flight_segm:
                    new_trip = customer.book_trip(reservation_id,
                                                  flight_segm, trip_departure)
                    new_list.append(new_trip)

    return new_list


if __name__ == '__main__':
    print("\n---------------------------------------------")
    print("Reading in all data! Processing...")
    print("---------------------------------------------\n")

    # input_data = import_data('data/airports.csv', 'data/customers.csv',
    #     'data/segments.csv', 'data/trips.csv')
    input_data = import_data('data/airports.csv', 'data/customers.csv',
                             'data/segments_small.csv', 'data/trips_small.csv')

    airports = create_airports(input_data[0])
    print("Airports Created! Still Processing...")
    flights = create_flight_segments(input_data[1])
    print("Flight Segments Created! Still Processing...")
    customers = create_customers(input_data[2])
    print("Customers Created! Still Processing...")
    print("Loading trips can take a while...")
    trips = load_trips(input_data[3], customers, flights)
    print("Trips Created! Opening Visualizer...\n")

    flights_len = 0
    for ky in flights:
        flights_len += len(flights[ky])

    print("---------------------------------------------")
    print("Some Statistics:")
    print("---------------------------------------------")
    print("Total airports in the dataset:", len(airports))
    print("Total flight segments in the dataset:", flights_len)
    print("Total customers in the dataset:", len(customers))
    print("Total trips in the dataset:", len(trips))
    print("---------------------------------------------\n")

    all_flights = [seg for tp in trips for seg in tp.get_flight_segments()]
    all_customers = [customers[cid] for cid in customers]

    V = Visualizer()
    V.draw(all_flights)

    while not V.has_quit():

        flights = V.handle_window_events(all_customers, all_flights)

        all_flights = []

        for flt in flights:
            all_flights.append(flt)

        V.draw(all_flights)

    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'csv', 'datetime', 'doctest',
            'visualizer', 'customer', 'flight', 'airport'
        ],
        'max-nested-blocks': 6,
        'allowed-io': [
            'create_customers', 'create_airports', 'import_data',
            'create_flight_segments', 'load_trips'
        ],
        'generated-members': 'pygame.*'
    })
