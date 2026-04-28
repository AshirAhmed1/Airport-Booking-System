# Airport Booking System

## Overview

Airport Booking System is a Python-based flight booking and visualization project. The system models airports, customers, flight segments, trips, seat bookings, frequent flyer status, and flight filtering. It uses CSV datasets to load airports, customers, available flight segments, and customer trip requests.

The application also includes a visual map interface that displays booked flight routes across the world. Users can filter displayed flights by customer, duration, location, date, or trip reservation ID.

This project was created for a CSC148 software design assignment and demonstrates object-oriented programming, data processing, file parsing, filtering, testing, and visualization.

## Features

- Load airport, customer, flight segment, and trip data from CSV files
- Store airport information using IATA airport codes
- Track airport longitude and latitude coordinates
- Create flight segments with departure/arrival airports, times, distances, and costs
- Book seats for customers in Economy or Business class
- Track seat capacity and seat availability
- Prevent duplicate seat bookings for the same customer
- Allow seat class changes if space is available
- Cancel booked seats
- Create trips from one or more flight segments
- Calculate total trip time
- Calculate total in-flight time
- Calculate customer trip costs
- Track customer flight history
- Track customer frequent flyer miles
- Assign frequent flyer status based on accumulated miles
- Apply frequent flyer discounts to future trips
- Display flight routes on a world map
- Filter displayed flight segments
- Run automated tests with `pytest`

## Technologies Used

- Python
- CSV file processing
- Object-Oriented Programming
- PyGame
- Tkinter
- Pytest
- PythonTA

## How to Run

1. Clone the repository:

```bash
git clone https://github.com/your-username/Airport-Booking-System.git
```

2. Open the project folder.

3. Make sure the project contains the required data files:

```text
data/airports.csv
data/customers.csv
data/segments.csv
data/segments_small.csv
data/trips.csv
data/trips_small.csv
```

4. Make sure the map image is stored in:

```text
images/map.png
```

5. Install the required Python packages:

```bash
pip install pygame pytest python-ta
```

6. Run the main application file:

```bash
python application.py
```

The application starts by loading the CSV data, creating airports, flight segments, customers, and trips, then opens the visualizer.

## Main File

Run this file to start the project:

```text
application.py
```

This file handles the main program flow:

- reads CSV files
- creates airport objects
- creates customer objects
- creates flight segment objects
- loads trips
- opens the visual map interface
- handles filter updates through the visualizer

## Project Structure

```text
Airport-Booking-System/
│
├── airport.py
├── application.py
├── customer.py
├── filter.py
├── flight.py
├── visualizer.py
│
├── data/
│   ├── airports.csv
│   ├── customers.csv
│   ├── segments.csv
│   ├── segments_small.csv
│   ├── trips.csv
│   └── trips_small.csv
│
├── images/
│   └── map.png
│
├── test_airport.py
├── test_application.py
├── test_customer.py
├── test_flight_segment.py
├── test_load_trips_robust.py
├── test_task4_filters.py
└── test_trip.py
```

## Data Files

The system uses CSV files as the main source of data.

### `airports.csv`

Stores airport information, including:

- airport ID
- airport name
- longitude
- latitude

### `customers.csv`

Stores customer information, including:

- customer ID
- customer name
- age
- nationality

### `segments.csv` and `segments_small.csv`

Store available flight segment information, including:

- flight ID
- departure airport
- arrival airport
- flight date
- departure time
- arrival time
- flight distance

### `trips.csv` and `trips_small.csv`

Store trip reservation requests, including:

- reservation ID
- customer ID
- trip date
- itinerary
- seat class for each segment

## Main Classes

## `Airport`

The `Airport` class represents an airport in the system.

Each airport stores:

- airport ID
- airport name
- map location as longitude and latitude

Important methods include:

```python
get_airport_id()
get_name()
get_location()
```

## `FlightSegment`

The `FlightSegment` class represents one flight from one airport to another.

Each flight segment stores:

- flight ID
- departure airport
- arrival airport
- departure time
- arrival time
- flight duration
- flight distance
- base fare cost
- seat capacity
- seat availability
- passenger manifest
- longitude/latitude coordinates for map display

Important methods include:

```python
get_fid()
get_dep()
get_arr()
get_times()
get_duration()
get_length()
get_base_fare_cost()
get_long_lat()
book_seat()
cancel_seat()
check_manifest()
check_seat_class()
```

## `Trip`

The `Trip` class represents a complete customer itinerary.

A trip may contain one flight segment or multiple connecting flight segments.

Each trip stores:

- reservation ID
- customer ID
- trip departure date
- list of flight segments

Important methods include:

```python
get_reservation_id()
get_flight_segments()
get_in_flight_time()
get_total_trip_time()
```

## `Customer`

The `Customer` class represents a customer of the airline system.

Each customer stores:

- customer ID
- name
- age
- nationality
- booked trips
- total flight costs
- frequent flyer miles
- frequent flyer status

Important methods include:

```python
get_id()
get_trips()
get_total_flight_costs()
get_cost_of_trip()
get_ff_status()
get_miles()
book_trip()
cancel_trip()
```

## Frequent Flyer System

The project includes a frequent flyer system based on accumulated qualifying miles.

### Frequent Flyer Status Levels

| Status | Required Miles | Discount |
|---|---:|---:|
| Prestige | 15,000 | 10% |
| Elite-Light | 30,000 | 15% |
| Elite-Regular | 50,000 | 20% |
| Super-Elite | 100,000 | 25% |

Discounts apply to future trips after the customer reaches the required status.

### Seat Class Multipliers

| Seat Class | Cost Multiplier | Miles Multiplier |
|---|---:|---:|
| Economy | 1.0x | 1x |
| Business | 2.5x | 5x |

Business class costs more but earns more qualifying miles.

## Seat Booking System

Each `FlightSegment` has a fixed seat capacity:

| Seat Class | Capacity |
|---|---:|
| Economy | 150 |
| Business | 22 |

When a customer books a seat, the system:

1. Checks whether the seat type exists.
2. Checks whether seats are still available.
3. Adds the customer to the flight manifest.
4. Reduces the available seat count.

If the customer is already booked on the same flight, the system does not duplicate the booking. If the customer changes seat class and the new class has availability, the system updates the manifest and adjusts seat availability.

## Filters

The project includes several filters that can be used through the visualizer.

## `CustomerFilter`

Filters flight segments based on a customer ID.

Input format:

```text
111111
```

The filter returns all displayed flight segments booked by that customer.

## `DurationFilter`

Filters flight segments by duration.

Input format:

```text
L#### 
G####
```

Examples:

```text
L0300
```

Returns flights less than 300 minutes.

```text
G0300
```

Returns flights greater than 300 minutes.

## `LocationFilter`

Filters flight segments based on departure or arrival airport.

Input format:

```text
DXXX
AXXX
```

Examples:

```text
DYYZ
```

Returns flights departing from `YYZ`.

```text
ACDG
```

Returns flights arriving at `CDG`.

## `DateFilter`

Filters flight segments that depart and arrive within a date range.

Input format:

```text
YYYY-MM-DD/YYYY-MM-DD
```

or:

```text
YYYY-MM-DD,YYYY-MM-DD
```

Example:

```text
2019-01-01/2019-01-05
```

## `TripFilter`

Filters flight segments based on a reservation ID.

Input example:

```text
ABC12
```

The filter returns all flight segments belonging to that trip.

## `ResetFilter`

Resets all filters and returns the flight segments from all customer trips.

## Visualizer Controls

The application includes a PyGame map visualizer with keyboard controls.

| Key | Action |
|---|---|
| C | Filter by customer ID |
| D | Filter by duration |
| L | Filter by location |
| T | Filter by trip reservation ID |
| Y | Filter by date |
| S | Print trip summary |
| R | Reset filters |
| Q | Quit application |

The visualizer draws flight paths on a world map using each flight segment's longitude and latitude coordinates.

## Trip Summary

The visualizer can print a trip summary by reservation ID.

A trip summary includes:

- trip reservation ID
- itinerary
- trip cost
- total trip time
- in-flight time

To use this feature, press:

```text
S
```

Then enter a reservation ID.

## How Trip Loading Works

The project loads trip data from CSV files and builds real booked trips.

The general flow is:

1. `import_data()` reads the airport, customer, segment, and trip CSV files.
2. `create_airports()` creates airport objects and stores airport coordinates.
3. `create_flight_segments()` creates flight segment objects and groups them by departure date.
4. `create_customers()` creates customer objects.
5. `load_trips()` reads each trip itinerary.
6. The program searches for matching flights between each pair of airports.
7. The earliest valid flight is selected.
8. Seats are booked for the customer.
9. A `Trip` object is created and added to the customer.

If a trip has an invalid reservation ID, invalid customer, malformed itinerary, or no matching flights, it is skipped safely.

## Testing

The project includes unit tests for the main system components.

Test files include:

```text
test_airport.py
test_application.py
test_customer.py
test_flight_segment.py
test_load_trips_robust.py
test_task4_filters.py
test_trip.py
```

To run all tests:

```bash
pytest
```

These tests check:

- airport creation
- airport coordinate storage
- customer creation
- flight segment creation
- seat booking
- seat cancellation
- customer trip booking
- frequent flyer status updates
- trip time calculations
- CSV loading
- itinerary parsing
- invalid trip handling
- filters
- edge cases

## Object-Oriented Concepts Used

## Encapsulation

Each class manages its own data. For example, `Customer` stores its own trips and frequent flyer status, while `FlightSegment` stores its own manifest and seat availability.

## Abstraction

The `Filter` class defines a general filtering interface. Specific filters such as `CustomerFilter`, `DurationFilter`, `LocationFilter`, `DateFilter`, and `TripFilter` implement the actual filtering logic.

## Composition

A `Trip` is composed of multiple `FlightSegment` objects. A `Customer` stores multiple `Trip` objects.

## Data Validation

The project checks for invalid input in several places, including:

- invalid customer IDs
- invalid reservation IDs
- invalid date ranges
- invalid location filter strings
- invalid duration filter strings
- missing flight matches
- unavailable seat types

## Possible Future Improvements

- Add a full booking user interface
- Allow users to create new bookings manually
- Add login support for customers and airline staff
- Add search by destination city or airport name
- Add more seat classes, such as Premium Economy or First Class
- Add cancellation through the visualizer
- Add sorting by price, duration, or departure time
- Add better route optimization for connecting flights
- Add database storage instead of CSV files
- Add exportable customer trip summaries
- Add stronger error messages for invalid trip data
- Add a web-based interface

## Contributors

- Ashir

## Notes

This project was created for a CSC148 assignment. It demonstrates Python object-oriented programming, CSV data processing, airline booking logic, customer rewards tracking, filtering, automated testing, and map-based visualization.
