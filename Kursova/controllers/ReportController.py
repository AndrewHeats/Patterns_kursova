from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.Driver import Driver
from models.FuelCost import FuelCost
from models.Insurance import Insurance
from models.Maintenance import Maintenance
from models.Report import Report
from models.Trip import Trip

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
    maint = sum(
        m.cost for m in session.query(Maintenance).filter(Maintenance.date >= start, Maintenance.date <= end).all())
    insur = sum(i.cost for i in
                session.query(Insurance).filter(Insurance.expiry_date >= start, Insurance.expiry_date <= end).all())
    total = fuel + maint + insur
    return f"Money spent: {total}$ (Fuel: {fuel}$, Maintenance: {maint}$, Insurance: {insur}$)"


def car_strategy(session, car_id, start, end):
    trips = session.query(Trip).filter(Trip.car_id == car_id, Trip.date >= start, Trip.date <= end).all()
    trips_cnt = len(trips)
    km = sum(t.distance for t in trips)
    return f"Car {car_id}: trips={trips_cnt}, km={km}"


@report_bp.route('/reports', methods=['POST'])
def create_report():
    session = Session()
    data = request.json
    start = data['start_date']
    end = data['end_date']
    report_type = data['type']
    if report_type == "CarsPark":
        result = carspark_strategy(session, start, end)
    elif report_type == "Money":
        result = money_strategy(session, start, end)
    elif report_type == "Car":
        car_id = data.get('car_id')
        result = car_strategy(session, car_id, start, end)
    else:
        result = "Unknown type"
    report = Report(start_date=start, end_date=end, type=report_type, data=result)
    session.add(report)
    session.commit()
    session.close()
    return jsonify({'message': 'Звіт створено', 'data': result})


@report_bp.route('/reports', methods=['GET'])
def get_reports():
    session = Session()
    reports = session.query(Report).all()
    result = [{"id": r.id, "start_date": r.start_date, "end_date": r.end_date, "type": r.type, "data": r.data} for r in
              reports]
    session.close()
    return jsonify(result)


@report_bp.route('/reports/<int:id>', methods=['PUT'])
def update_report(id):
    session = Session()
    report = session.query(Report).filter_by(id=id).first()
    if not report:
        session.close()
        return jsonify({'error': 'Звіт не знайдено'}), 404
    for key, value in request.json.items():
        setattr(report, key, value)
    session.commit()
    session.close()
    return jsonify({'message': 'Звіт оновлено'})


@report_bp.route('/reports/<int:id>', methods=['DELETE'])
def delete_report(id):
    session = Session()
    report = session.query(Report).filter_by(id=id).first()
    if not report:
        session.close()
        return jsonify({'error': 'Звіт не знайдено'}), 404
    session.delete(report)
    session.commit()
    session.close()
    return jsonify({'message': 'Звіт видалено'})
