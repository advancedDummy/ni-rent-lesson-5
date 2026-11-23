from src.manager import Manager
from src.models import Bill, Parameters


def make_bill(apartment, year, month, amount, bill_type='electricity'):
    return Bill(
        apartment=apartment,
        date_due=f'{year}-{month:02d}-15',
        settlement_year=year,
        settlement_month=month,
        amount_pln=amount,
        type=bill_type,
    )


def make_manager():
    manager = Manager(Parameters())
    manager.bills = [
        make_bill('apart-polanka', 2025, 1, 760.0, 'rent'),
        make_bill('apart-polanka', 2025, 1, 150.0, 'electricity'),
        make_bill('apart-polanka', 2025, 2, 200.0, 'gas'),
        make_bill('apart-inne', 2025, 1, 9999.0, 'rent'),
    ]
    return manager


def test_costs_for_nonexistent_apartment():
    manager = make_manager()
    assert manager.get_apartment_costs('apart-nie-istnieje', 2025, 1) is None


def test_costs_for_month_without_bills():
    manager = make_manager()
    assert manager.get_apartment_costs('apart-polanka', 2025, 3) == 0.0


def test_costs_for_month_with_bills():
    manager = make_manager()
    assert manager.get_apartment_costs('apart-polanka', 2025, 1) == 910.0
    assert manager.get_apartment_costs('apart-polanka', 2025, 2) == 200.0