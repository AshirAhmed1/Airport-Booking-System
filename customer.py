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
from __future__ import annotations

from datetime import datetime
from typing import List, Tuple, Dict, Optional

from flight import Trip, FlightSegment

"""
    FF_Status: Dict[str, Tuple(int, int)] where the Tuple(status miles to 
               reach discount for fares from the next trip (NOT flight segment)
               after the status is achieved).
               The units are (Kilometers, Percent).
"""
FREQUENT_FLYER_STATUS = {"Prestige": (15000, -10), "Elite-Light": (30000, -15),
                         "Elite-Regular": (50000, -20),
                         "Super-Elite": (100000, -25)}

"""
    FREQUENT_FLYER_MULTIPLIER: the key is the type of cabin class (seat type), 
                               the value is the miles multiplier (status miles 
                               are calculated by multiplying the flight length 
                               by this miles multiplier).
"""
FREQUENT_FLYER_MULTIPLIER = {"Economy": 1, "Business": 5}

"""
    CLASS_MULTIPLIER: used to determine the real-cost of the segment based on 
                      the class of flight: Dict(str, float) taken by the 
                      customer, where the Dict(class, multiplier).
"""
CLASS_MULTIPLIER = {"Economy": 1.0, "Business": 2.5}


# Helper Functions
def _update_ff_status(miles: float) -> str:
    """Return the customer's frequent flyer status"""
    if miles >= 100000:
        return "Super-Elite"
    elif miles >= 50000:
        return "Elite-Regular"
    elif miles >= 30000:
        return "Elite-Light"
    elif miles >= 15000:
        return "Prestige"
    else:
        return ""


class Customer:
    """ A Customer of Python Air.

    === Public Attributes ===
    name:
        the customer's name (may include one or all:
        first, middle, and last).
    age:
        the customer's age.
    nationality:
        the customer's nationality (there are no dual citizens).
    all_flight_costs:
        the sum of all flight costs this customer has taken over
        the course of their existence.

    Representation Invariants:
        - trips are stored per customer forever.
        - miles/status are accumulated and never lost.
    """

    # === Private Attributes ===
    # _customer_id:
    #     this is a unique 6-digit customer identifier.
    # _ff_status:
    #     this is the customer's frequent flyer status.
    # _miles:
    #     this is the running tally of the customer's
    #     total qualifying miles for their status.
    # _trips:
    #     this stores the dictionary of Trips and their
    #     corresponding costs.

    name: str
    age: int
    nationality: str
    all_flight_costs: float
    _customer_id: int
    _trips: Dict[Trip, float]
    _ff_status: str
    _miles: int

    def __init__(self, cus_id: int, name: str, age: int, nat: str) -> None:
        """ A Customer of Python Air. """

        self.name = name
        self.age = age
        self.nationality = nat
        self.all_flight_costs = 0.0
        self._customer_id = cus_id
        self._trips = {}
        self._ff_status = ""
        self._miles = 0

    def get_id(self) -> int:
        """ Returns this customer's identification (ID). """

        return self._customer_id

    def get_trips(self) -> List[Trip]:
        """ Returns a list of Trips booked for this customer. """

        new_list = []
        for x in self._trips:
            new_list.append(x)
        return new_list

    def get_total_flight_costs(self) -> float:
        """ Returns this customer's total flight costs. """

        return self.all_flight_costs

    def get_cost_of_trip(self, trip_lookup: Trip) -> Optional[float]:
        """ Returns the cost of that Trip, otherwise None. """

        if trip_lookup in self._trips:
            return self._trips[trip_lookup]
        else:
            return None

    def get_ff_status(self) -> str:
        """ Returns this customer's frequent flyer status. """

        return self._ff_status

    def get_miles(self) -> int:
        """ Returns this customer's qualifying miles. """

        return self._miles

    def book_trip(self, reservation_id: str,
                  segments: List[Tuple[FlightSegment, str]],
                  trip_date: datetime.date) -> Trip:
        """ Books the customer's trip and returns a Trip.

            <segments> are a List of Tuples, containing a (FlightSegment,
            seat_type) pair.

            Precondition: the customer is guaranteed to have a seat on each of
                          the <segments>.
        """

        f_segments = []
        total_cost = 0.0
        qualifying_miles = 0
        curr_status = self._ff_status
        discount_percent = 0
        for x in segments:
            f_segments.append(x[0])

        trip = Trip(reservation_id, self._customer_id, trip_date, f_segments)

        if curr_status in FREQUENT_FLYER_STATUS:
            discount_percent = FREQUENT_FLYER_STATUS[curr_status][1]

        for x in segments:
            flight_seg = x[0]
            seat_type = x[1]
            total_cost += (flight_seg.get_base_fare_cost()
                           * flight_seg.get_length()
                           * CLASS_MULTIPLIER[seat_type])
            qualifying_miles += (flight_seg.get_length()
                                 * FREQUENT_FLYER_MULTIPLIER[seat_type])

        discounted_cost = total_cost * (1 - abs(discount_percent) / 100)
        self.all_flight_costs += discounted_cost
        self._miles += qualifying_miles
        self._ff_status = _update_ff_status(self._miles)
        self._trips[trip] = discounted_cost
        return trip

    def cancel_trip(self, canceled_trip: Trip,
                    segments: List[Tuple[FlightSegment, str]]) -> None:
        """ Cancels this customer's Trip.

            <segments> are a List of Tuples, containing the (FlightSegment,
            seat_type) pair.

            Precondition: the <canceled_trip> must be a valid Trip that this
                          customer has booked.
        """
        for x in segments:
            flight_seg = x[0]
            flight_seg.cancel_seat(self._customer_id)
        if canceled_trip in self._trips:
            self.all_flight_costs -= self._trips[canceled_trip]
            self.all_flight_costs -= 100
            del self._trips[canceled_trip]


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta',
            'typing',
            'doctest',
            'flight',
            '__future__',
            'datetime'
        ],
        'max-attributes': 8,
    })
