import pytest

from src.manager import Manager
from src.models import ApartmentSettlement, Bill, Parameters


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


def test_apartment_settlement_with_bills():
    manager = make_manager()
    settlement = manager.get_apartment_settlement('apart-polanka', 2025, 1)

    assert isinstance(settlement, ApartmentSettlement)
    assert settlement.apartment == 'apart-polanka'
    assert settlement.year == 2025
    assert settlement.month == 1
    assert settlement.total_bills_pln == 910.0
    assert settlement.total_rent_pln == 0.0
    assert settlement.total_due_pln == -910.0

    # inny miesiąc tego samego mieszkania
    other = manager.get_apartment_settlement('apart-polanka', 2025, 2)
    assert other.total_bills_pln == 200.0
    assert other.total_due_pln == -200.0


def test_apartment_settlement_without_bills_in_month():
    manager = make_manager()
    settlement = manager.get_apartment_settlement('apart-polanka', 2025, 3)

    assert isinstance(settlement, ApartmentSettlement)
    assert settlement.month == 3
    assert settlement.total_bills_pln == 0.0
    assert settlement.total_rent_pln == 0.0
    assert settlement.total_due_pln == 0.0


def test_apartment_settlement_for_nonexistent_apartment_and_invalid_month():
    manager = make_manager()
    assert manager.get_apartment_settlement('apart-nie-istnieje', 2025, 1) is None
    with pytest.raises(ValueError):
        manager.get_apartment_settlement('apart-polanka', 2025, 13)