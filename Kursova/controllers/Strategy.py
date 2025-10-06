class ReportStrategy:
    def generate(self, session, start, end, **kwargs):
        pass


class CarsParkStrategy(ReportStrategy):
    def generate(self, session, start, end, **kwargs):
        Trip = kwargs['Trip']
        Driver = kwargs['Driver']
        trips = session.query(Trip).filter(Trip.date >= start, Trip.date <= end).all()
        trip_count = len(trips)
        driver_ids = set(t.driver_id for t in trips)
        drivers = session.query(Driver).filter(Driver.id.in_(driver_ids)).all()
        driver_list = [d.name for d in drivers]
        return f"Trips: {trip_count}, Drivers: {', '.join(driver_list)}"


class MoneyStrategy(ReportStrategy):
    def generate(self, session, start, end, **kwargs):
        FuelCost = kwargs['FuelCost']
        Maintenance = kwargs['Maintenance']
        Insurance = kwargs['Insurance']
        fuel = sum(f.cost for f in session.query(FuelCost).filter(FuelCost.date >= start, FuelCost.date <= end).all())
        maint = sum(
            m.cost for m in session.query(Maintenance).filter(Maintenance.date >= start, Maintenance.date <= end).all())
        insur = sum(i.cost for i in
                    session.query(Insurance).filter(Insurance.expiry_date >= start, Insurance.expiry_date <= end).all())
        total = fuel + maint + insur
        return f"Money spent: {total}$ (Fuel: {fuel}$, Maintenance: {maint}$, Insurance: {insur}$)"


class CarStrategy(ReportStrategy):
    def generate(self, session, start, end, **kwargs):
        Trip = kwargs['Trip']
        car_id = kwargs['car_id']
        trips = session.query(Trip).filter(Trip.car_id == car_id, Trip.date >= start, Trip.date <= end).all()
        trips_cnt = len(trips)
        km = sum(t.distance for t in trips)
        return f"Car {car_id}: trips={trips_cnt}, km={km}"
