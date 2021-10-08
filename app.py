from flask import Flask, jsonify

import numpy as np
import pandas as pd

import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy import cast, Date

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func

from dateutil import parser

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect = True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station





#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#/
#Home page.
#List all routes that are available.

@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"Search the minimum, average and maximum temperature with start date only:<br/>"
        f"Note to enter the dates in this format dd/(spell the first three letters of the month)/yyyy<br/>"
        f"/api/v1.0/app22a<br/>"
        f"/api/v1.0/"
        
    )

#/api/v1.0/precipitation
#Convert the query results to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def prcp():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement. prcp).all()

    session.close()

    percipitation = []
    for date, prcp in results:
        percipitation_dict = {}
        percipitation_dict["date"] = date
        percipitation_dict["prcp"] = prcp
        percipitation.append(percipitation_dict)

    # Convert list of tuples into normal list
    #all_names = list(np.ravel(results))

    return jsonify(percipitation)

#/api/v1.0/stations
#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    """Return a list of all passenger names"""
    # Query all passengers
    
    results = session.query(Measurement.station).group_by(Measurement.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


#/api/v1.0/tobs
#Query the dates and temperature observations of the most active station for the last year of data.
#Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    #Find the maximum date in the database
    max_date = session.query(func.max(Measurement.date)).all()
    max_date_only = max_date[0][0]
    
    #Convert the string type date into date format
    datetime_object = datetime.datetime.strptime(max_date_only, '%Y-%m-%d')
    datetime_object= datetime.datetime.date(datetime_object)

    # Calculate the date 1 year ago from the last data point in the database
    twelves_months_ago_prcp = datetime_object - relativedelta(months=+12)

    results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date > twelves_months_ago_prcp).filter(Measurement.date < datetime_object).all()

    session.close()

    temperature = []
    for date, tobs in results:
        temperature_dict = {}
        temperature_dict["date"] = date
        temperature_dict["tobs"] = tobs
        temperature.append(temperature_dict)

    # Convert list of tuples into normal list
    #all_names = list(np.ravel(results))

    return jsonify(temperature)



#/api/v1.0/<start> and /api/v1.0/<start>/<end>
#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>")
def min_avg_max_temp_start_dates(start):
   
    session = Session(engine)

    #Find the maximum date in the database
    max_date = session.query(func.max(Measurement.date)).all()
    max_date_only = max_date[0][0]
        
    #Convert the string type date into date format
    datetime_object = datetime.datetime.strptime(max_date_only, '%Y-%m-%d')
    datetime_object= datetime.datetime.date(datetime_object)

    start_date = parser.parse(start)
    start_date = datetime.datetime.date(start_date)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
    filter(Measurement.date > start_date).filter(Measurement.date < datetime_object).all()

    session.close()

    temperature = []
    for minimum_temp, average_temp, max_temp in results:
        temperature_dict = {}
        temperature_dict["min_temp"] = minimum_temp
        temperature_dict["avg_temp"] = average_temp
        temperature_dict["max_temp"] = max_temp
        temperature.append(temperature_dict)

       

    return jsonify(temperature)

@app.route("/api/v1.0/<start>/<end>")
def min_avg_max_temp_start_end_dates(start, end):
   
    session = Session(engine)

    
    #Find start date
    start_date = parser.parse(start)
    start_date = datetime.datetime.date(start_date)

    #Find end date
    end_date = parser.parse(end)
    end_date = datetime.datetime.date(end_date)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
    filter(Measurement.date > start_date).filter(Measurement.date < end_date).all()

    session.close()

    temperature = []
    for minimum_temp, average_temp, max_temp in results:
        temperature_dict = {}
        temperature_dict["min_temp"] = minimum_temp
        temperature_dict["avg_temp"] = average_temp
        temperature_dict["max_temp"] = max_temp
        temperature.append(temperature_dict)

       
        
    return jsonify(temperature) #& f"Start date: {start} and End date: {end}"






if __name__ == "__main__":
    app.run(debug=True)
