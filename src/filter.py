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
import datetime
from typing import List

from customer import Customer
from flight import FlightSegment


# Helper Functions
def _remove_duplicates(flight_segments: List[FlightSegment])\
        -> List[FlightSegment]:
    """Return a new list with duplicates removed from flight_segments."""
    no_dup_flight = []
    for i in flight_segments:
        if i not in no_dup_flight:
            no_dup_flight.append(i)
    return no_dup_flight


class Filter:
    """ A class for filtering flight segments based on some criterion.

        This is an abstract class. Only subclasses should be instantiated.
    """

    def __init__(self) -> None:
        pass

    def apply(self, customers: List[Customer], data: List[FlightSegment],
              filter_string: str) -> List[FlightSegment]:
        """ Returns a list of all flight segments from <data>, which match the
            filter specified in <filter_string>.

            The <filter_string> is provided by the user through the visual
            prompt, after selecting this filter.

            The <customers> is a list of all customers from the input dataset.

            If the filter has no effect or the <filter_string> is invalid then
            return the same flights segments from the <data> input.

            Precondition:
                - <customers> contains the list of all customers from the input
                  dataset
                - all flight segments included in <data> are valid segments
                  from the input dataset
        """
        raise NotImplementedError

    def __str__(self) -> str:
        """ Returns a description of this filter to be displayed in the UI menu
        """
        raise NotImplementedError


class ResetFilter(Filter):
    """ A class for resetting all previously applied filters, if any. """

    def apply(self, customers: List[Customer], data: List[FlightSegment],
              filter_string: str) -> List[FlightSegment]:
        """ Reset all of the applied filters. Returns a List containing all the
            flight segments corresponding to all trips of <customers>.

            The <data>, <customers>, and <filter_string> arguments for this
            type of filter are ignored.
        """

        flight_segments = []
        for x in customers:
            for j in x.get_trips():
                flight_segments.extend(j.get_flight_segments())

        return _remove_duplicates(flight_segments)

    def __str__(self) -> str:
        """ Returns a description of this filter to be displayed in the UI menu.
            Unlike other __str__ methods, this one is required!
        """
        return "Reset all of the filters applied so far (if any)!"


class CustomerFilter(Filter):
    """ A class for selecting the flight segments for a given customer. """

    def apply(self, customers: List[Customer], data: List[FlightSegment],
              filter_string: str) -> List[FlightSegment]:
        """ Returns a list of all flight segments from <data> made or received
            by the customer with the id specified in <filter_string>.

            The <customers> list contains all customers from the input dataset.

            The filter string is valid if and only if it contains a valid
            customer ID.

            If the filter string is invalid, do the following:
              1. return the original list <data>, and
              2. ensure your code does not crash.
        """
        if filter_string.isdigit() and len(filter_string) == 6:
            customer_id = int(filter_string)
        else:
            return data

        flight_segments = []
        customer_found = False

        for x in customers:
            if x.get_id() == customer_id:
                customer_found = True
                break

        if not customer_found:
            return data

        for j in data:
            if j.check_manifest(customer_id):
                flight_segments.append(j)
        return flight_segments

    def __str__(self) -> str:
        """ Returns a description of this filter to be displayed in the UI menu.
            Unlike other __str__ methods, this one is required!
        """
        return "Filter events based on customer ID"


class DurationFilter(Filter):
    """ A class for selecting only the flight segments lasting either over or
        under a specified duration.
    """

    def apply(self, customers: List[Customer], data: List[FlightSegment],
              filter_string: str) -> List[FlightSegment]:
        """ Returns a list of all flight segments from <data> with a duration of
            under or over the time indicated in the <filter_string>.

            The <customers> list contains all customers from the input dataset.

            The filter string is valid if and only if it contains the following
            input format: either "Lxxxx" or "Gxxxx", indicating to filter
            flight segments less than xxxx or greater than xxxx minutes,
            respectively.

            If the filter string is invalid, do the following:
              1. return the original list <data>, and
              2. ensure your code does not crash.
        """
        duration_greater = ""
        duration_less = ""
        flight_segments = []
        if ((filter_string[0] == "G" or filter_string[0] == "g")
                and filter_string[1:5].isdigit() and len(filter_string) == 5):
            duration_greater = filter_string.upper()
        elif ((filter_string[0] == "L" or filter_string[0] == "l")
              and filter_string[1:5].isdigit() and len(filter_string) == 5):
            duration_less = filter_string.upper()
        else:
            return data

        if duration_greater:
            for d in data:
                duration = d.get_duration()
                total_secs = (duration.hour
                              * 3600 + duration.minute
                              * 60 + duration.second)
                total_min = total_secs // 60
                if total_min > int(duration_greater[1:5]):
                    flight_segments.append(d)

        elif duration_less:
            for d in data:
                duration = d.get_duration()
                total_secs = (duration.hour
                              * 3600 + duration.minute
                              * 60 + duration.second)
                total_min = total_secs // 60
                if total_min < int(duration_less[1:5]):
                    flight_segments.append(d)

        return flight_segments

    def __str__(self) -> str:
        """ Returns a description of this filter to be displayed in the UI menu
        """
        return "Filter flight segments based on duration; " \
               "L#### returns flight segments less than specified length, " \
               "G#### for greater "


class LocationFilter(Filter):
    """ A class for selecting only the flight segments which took place within
        a specific area.
    """

    def apply(self, customers: List[Customer], data: List[FlightSegment],
              filter_string: str) -> List[FlightSegment]:
        """ Returns a list of all flight segments from <data>, which took place
            within a location specified by the <filter_string> (the IATA
            departure or arrival airport code of the segment was
            <filter_string>).

            The <customers> list contains all customers from the input dataset.

            The filter string is valid if and only if it contains a valid
            3-string IATA airport code. In the event of an invalid string:
              1. return the original list <data>, and
              2. your code must not crash.
        """
        flight_segments = []
        dep_str = ""
        arr_str = ""
        if ((filter_string[0] == "D" or filter_string[0] == "d")
                and filter_string[1:4].isalpha()
                and len(filter_string) == 4):
            dep_str = filter_string.upper()
        elif ((filter_string[0] == "A" or filter_string[0] == "a")
              and filter_string[1:4].isalpha()
              and len(filter_string) == 4):
            arr_str = filter_string.upper()
        else:
            return data

        if dep_str:
            for z in data:
                if dep_str[1:4] == z.get_dep():
                    flight_segments.append(z)
        elif arr_str:
            for z in data:
                if arr_str[1:4] == z.get_arr():
                    flight_segments.append(z)

        return flight_segments

    def __str__(self) -> str:
        """ Returns a description of this filter to be displayed in the UI menu.
            Unlike other __str__ methods, this one is required!
        """
        return "Filter flight segments based on an airport location;\n" \
               "DXXX returns flight segments that depart airport XXX,\n" \
               "AXXX returns flight segments that arrive at airport XXX\n"


class DateFilter(Filter):
    """ A class for selecting all flight segments that departed and arrive
    between two dates (i.e. "YYYY-MM-DD/YYYY-MM-DD" or "YYYY-MM-DD,YYYY-MM-DD").
    """

    def apply(self, customers: List[Customer], data: List[FlightSegment],
              filter_string: str) -> List[FlightSegment]:
        """ Returns a list of all flight segments from <data> that have departed
            and arrived between the range of two dates indicated in the
            <filter_string>.

            The <customers> list contains all customers from the input dataset.

            The filter string is valid if and only if it contains the following
            input format: either "YYYY-MM-DD/YYYY-MM-DD" or
            "YYYY-MM-DD,YYYY-MM-DD", indicating to filter flight segments
            between the first occurrence of YYYY-MM-DD and the second occurrence
            of YYYY-MM-DD.

            If the filter string is invalid, do the following:
              1. return the original list <data>, and
              2. ensure your code does not crash.
        """

        flight_segments = []
        if '/' in filter_string:
            arr_dep = filter_string.split("/")
        elif ',' in filter_string:
            arr_dep = filter_string.split(",")
        else:
            return data

        if len(arr_dep) != 2:
            return data

        try:
            start = datetime.datetime.strptime(arr_dep[0].strip(), "%Y-%m-%d")
            end = datetime.datetime.strptime(arr_dep[1].strip(), "%Y-%m-%d")
        except ValueError:
            return data

        if start > end:
            return data

        for x in data:
            dep = x.get_times()[0]
            arr = x.get_times()[1]
            if start <= dep <= end and start <= arr <= end:
                flight_segments.append(x)

        return flight_segments

    def __str__(self) -> str:
        """ Returns a description of this filter to be displayed in the UI menu.
            Unlike other __str__ methods, this one is required!
        """
        return "Filter flight segments based on dates; " \
               "'YYYY-MM-DD/YYYY-MM-DD' or 'YYYY-MM-DD,YYYY-MM-DD'"


class TripFilter(Filter):
    """ A class for selecting the flight segments for a trip. """

    def apply(self, customers: List[Customer], data: List[FlightSegment],
              filter_string: str) -> List[FlightSegment]:
        """ Returns a list of all flight segments from <data> where the
            <filter_string> specified the trip's reservation id.

            The <customers> list contains all customers from the input dataset.

            The filter string is valid if and only if it contains a valid
            Reservation ID.

            If the filter string is invalid, do the following:
              1. return the original list <data>, and
              2. ensure your code does not crash.
        """
        flight_segments = []
        if filter_string.isalnum() and len(filter_string) == 5:
            res_id = filter_string.upper()
        else:
            return data

        for x in customers:
            for j in x.get_trips():
                if j.get_reservation_id().upper() == res_id:
                    for d in j.get_flight_segments():
                        if d in data:
                            flight_segments.append(d)

        return flight_segments

    def __str__(self) -> str:
        """ Returns a description of this filter to be displayed in the UI menu.
            Unlike other __str__ methods, this one is required!
        """
        return "Filter events based on a reservation ID"


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'datetime', 'doctest',
            'customer', 'flight', 'time'
        ],
        'max-nested-blocks': 5,
        'allowed-io': ['apply', '__str__']
    })
