# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine)
# reflect the tables
msmnt = Base.classes.measurement
st = Base.classes.station

# Save references to each table


# Create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
#Welcome page to display all available API routes
@app.route("/")
def welcome():
    return(f"Available Routes: <br/>"
           f'Here you can see precipitation data for the last year from the most recent date: /api/v1.0/precipitation <br/>'
           f'Provides a list of all stations: /api/v1.0/stations <br/>'
           f'Lets you take a look at the temperature for the past year: /api/v1.0/tobs <br/>'
           f'If you would like to find min, max, and avg temp for a certain date in the past year: /api/v1.0/yyyy-mm-dd <br/>'
           f'Use this for finding min, max, and avg between two specific dates: /api/v1.0/tobs/yyyy-mm-dd/yyyy-mm-dd'
           )
@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    stations = session.query(st.station).all()
    session.close()
    st_data = list(np.ravel(stations))
    return jsonify(st_data)

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    prcp_data = session.query(msmnt.date,msmnt.prcp).filter(msmnt.date > "2016-08-2022").\
                order_by(msmnt.date).all()
    session.close()
    results = []
    for data in prcp_data:
        results.append(data)
    prcp_dict = dict(results)
    return jsonify(prcp_dict)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    tobs_data = session.query(msmnt.date,msmnt.tobs).filter(msmnt.station == 'USC00519281').\
                filter(msmnt.date > '2016-08-22')
    results = []
    for tob in tobs_data:
        results.append(tob)
    session.close()
    temp_data = dict(results)
    return jsonify(temp_data)

@app.route('/api/v1.0/<start>')
def start_year(start):
    session = Session(engine)
    start = dt.datetime.strptime(start,"%Y-%m-%d").date()
    sel = [func.min(msmnt.tobs), func.max(msmnt.tobs), func.avg(msmnt.tobs)]
    results = session.query(*sel).filter(msmnt.date >= start).all()
    session.close()
    list = []
    for data in results:
        dict = {}
        (min_temp, avg_temp, max_temp) = data
        dict['min_temp'] = min_temp
        dict['max_temp'] =  max_temp
        dict['avg_temp'] = avg_temp
        list.append(dict)
    return jsonify(list)

@app.route('/api/v1.0/<start>/<end>')
def start_end(start, end):
    session = Session(engine)
    start = dt.datetime.strptime(start, "%Y-%m-%d").date()
    end = dt.datetime.strptime(end, "%Y-%m-%d").date()
    sel = [func.min(msmnt.tobs), func.max(msmnt.tobs),func.avg(msmnt.tobs)]
    start_end_data = session.query(*sel).filter(msmnt.date >= start).filter(msmnt.date <= end)
    session.close()
    list_temp = []
    for data in start_end_data:
        temp_dict = {}
        (temp_min,temp_max,temp_avg) = data
        temp_dict["min_temp"] = temp_min
        temp_dict["max_temp"] = temp_max
        temp_dict["avg_temp"] = temp_avg
        list_temp.append(temp_dict)
    return jsonify(list_temp)

if __name__ == "__main__":
    app.run(debug=True)