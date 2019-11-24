import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """Available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precip():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    results =session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    all_percip = []
    for date, prcp in results:
        percip_dict = {}
        percip_dict["date"] = date
        percip_dict["prcp"] = prcp
        all_percip.append(percip_dict)

    return jsonify(all_percip)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(Station.station).all()

    session.close()

    stations = list(np.ravel(results))

    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    latest_date = session.query(Measurement.date).\
    order_by(Measurement.date.desc()).first().date
    
    year_ago = dt.datetime.strptime(latest_date, '%Y-%m-%d') - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date > year_ago).\
    order_by(Measurement.date).all()

    session.close()

    station_tobs = list(np.ravel(results))

    return jsonify(station_tobs)

@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs)\
                  , func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).all()

    session.close()

    start_nums = list(np.ravel(results))

    return jsonify(start_nums)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Create our session (link) from Python to the DB
    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs)\
                  , func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start, Measurement.date <= end).all()

    session.close()

    start_end_nums = list(np.ravel(results))

    return jsonify(start_end_nums)


if __name__ == '__main__':
    app.run(debug=True)
