import datetime
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.Report import Report
from models.Trip import Trip
from models.Driver import Driver
from models.FuelCost import FuelCost
from models.Maintenance import Maintenance
from models.Insurance import Insurance
from models.Car import Car

report_bp = Blueprint('report', __name__)
engine = create_engine('sqlite:///fleet.db')
Session = sessionmaker(bind=engine)

def carspark_strategy(session, start, end):
    trips = session.query(Trip).filter(Trip.date >= start, Trip.date <= end).all()
    trips_cnt = len(trips)
    driver_ids = set(t.driver_id for t in trips)
    drivers = session.query(Driver).filter(Driver.id.in_(driver_ids)).all()
    drivers_list = [d.name for d in drivers]
    return f"Trips: {trips_cnt}, Drivers: {', '.join(drivers_list)}"

def money_strategy(session, start, end):
    fuel = sum(f.cost for f in session.query(FuelCost).filter(FuelCost.date >= start, FuelCost.date <= end).all())
    maint = sum(m.cost for m in session.query(Maintenance).filter(Maintenance.date >= start, Maintenance.date <= end).all())
    insur = sum(i.cost for i in session.query(Insurance).filter(Insurance.expiry_date >= start, Insurance.expiry_date <= end).all())
    total = fuel + maint + insur
    return f"Money spent: {total}$ (Fuel: {fuel}$, Maintenance: {maint}$, Insurance: {insur}$)"

def car_strategy(session, car_id, start, end):
    trips = session.query(Trip).filter(Trip.car_id == car_id, Trip.date >= start, Trip.date <= end).all()
    trips_cnt = len(trips)
    km = sum(t.distance for t in trips)
    return f"Car {car_id}: trips={trips_cnt}, km={km}"

# View: список звітів
@report_bp.route('/', methods=['GET'])
def list_reports():
    session = Session()
    reports = session.query(Report).all()
    cars = session.query(Car).all()
    session.close()
    return render_template('reports/reports.html', reports=reports, cars=cars)

# View: створення звіту
@report_bp.route('/new', methods=['GET', 'POST'])
def create_report_view():
    session = Session()
    cars = session.query(Car).all()
    if request.method == 'POST':
        data = request.form
        start = datetime.datetime.strptime(data['start_date'], "%Y-%m-%d").date()
        end = datetime.datetime.strptime(data['end_date'], "%Y-%m-%d").date()
        report_type = data['type']
        if report_type == 'CarsPark':
            result = carspark_strategy(session, start, end)
        elif report_type == 'Money':
            result = money_strategy(session, start, end)
        elif report_type == 'Car':
            car_id = int(data['car_id'])
            result = car_strategy(session, car_id, start, end)
        else:
            result = 'Unknown type'
        report = Report(start_date=start, end_date=end, type=report_type, data=result)
        session.add(report)
        session.commit()
        session.close()
        return redirect(url_for('report.list_reports'))
    session.close()
    return render_template('reports/reports_add.html', cars=cars)

# API: отримати всі звіти
@report_bp.route('/api', methods=['GET'])
def api_get_reports():
    session = Session()
    reports = session.query(Report).all()
    result = [{
        "id": r.id,
        "start_date": r.start_date.isoformat(),
        "end_date": r.end_date.isoformat(),
        "type": r.type,
        "data": r.data
    } for r in reports]
    session.close()
    return jsonify(result)

# API: створити звіт
@report_bp.route('/api', methods=['POST'])
def api_create_report():
    session = Session()
    data = request.json
    start = datetime.datetime.strptime(data['start_date'], "%Y-%m-%d").date()
    end = datetime.datetime.strptime(data['end_date'], "%Y-%m-%d").date()
    report_type = data['type']
    if report_type == 'CarsPark':
        result = carspark_strategy(session, start, end)
    elif report_type == 'Money':
        result = money_strategy(session, start, end)
    elif report_type == 'Car':
        car_id = data.get('car_id')
        result = car_strategy(session, car_id, start, end)
    else:
        result = 'Unknown type'
    report = Report(start_date=start, end_date=end, type=report_type, data=result)
    session.add(report)
    session.commit()
    session.close()
    return jsonify({'message': 'Звіт створено', 'data': result})
