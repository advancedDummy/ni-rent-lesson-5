import pytest

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


def test_costs_for_whole_year_and_whole_history():
    manager = make_manager()
    manager.bills.append(make_bill('apart-polanka', 2024, 5, 100.0))
    assert manager.get_apartment_costs('apart-polanka', 2025) == 1110.0
    assert manager.get_apartment_costs('apart-polanka') == 1210.0


@pytest.mark.parametrize('month', [0, 13, -1, 100])
def test_costs_with_invalid_month(month):
    manager = make_manager()
    with pytest.raises(ValueError):
        manager.get_apartment_costs('apart-polanka', 2025, month)


def test_costs_with_month_but_without_year():
    manager = make_manager()
    with pytest.raises(ValueError):
        manager.get_apartment_costs('apart-polanka', None, 1)


# ---- test z gałęzi extra-integration-test (prowadzący) ----
def test_apartment_costs_with_optional_parameters():
    manager = Manager(Parameters())
    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2025-03-15',
        settlement_year=2025,
        settlement_month=2,
        amount_pln=1250.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-03-15',
        settlement_year=2024,
        settlement_month=2,
        amount_pln=1150.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-02-02',
        settlement_year=2024,
        settlement_month=1,
        amount_pln=222.0,
        type='electricity'
    ))

    costs = manager.get_apartment_costs('apartment-1', 2024, 1)
    assert costs is None

    costs = manager.get_apartment_costs('apart-polanka', 2024, 3)
    assert costs == 0.0

    costs = manager.get_apartment_costs('apart-polanka', 2024, 1)
    assert costs == 222.0

    costs = manager.get_apartment_costs('apart-polanka', 2025, 1)
    assert costs == 910.0
    
    costs = manager.get_apartment_costs('apart-polanka', 2024)
    assert costs == 1372.0

    costs = manager.get_apartment_costs('apart-polanka')
    assert costs == 3532.0