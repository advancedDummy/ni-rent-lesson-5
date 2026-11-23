import pytest

from src.manager import Manager
from src.models import Bill, Parameters, Tenant, TenantSettlement


def make_tenant(name, apartment='apart-polanka'):
    return Tenant(
        name=name,
        apartment=apartment,
        room='room-test',
        rent_pln=1000.0,
        deposit_pln=2000.0,
        date_agreement_from='2024-01-01',
        date_agreement_to='2024-12-31',
    )


def make_manager(tenants):
    manager = Manager(Parameters())
    manager.tenants = tenants
    manager.bills = [
        Bill(apartment='apart-polanka', date_due='2025-02-15', settlement_year=2025,
             settlement_month=1, amount_pln=760.0, type='rent'),
        Bill(apartment='apart-polanka', date_due='2025-02-12', settlement_year=2025,
             settlement_month=1, amount_pln=150.0, type='electricity'),
    ]
    return manager


def test_tenant_settlements_for_two_tenants():
    manager = make_manager({
        'tenant-1': make_tenant('Jan Nowak'),
        'tenant-2': make_tenant('Adam Kowalski'),
        'tenant-x': make_tenant('Ktoś z innego mieszkania', apartment='apart-inne'),
    })
    settlements = manager.get_tenant_settlements('apart-polanka', 2025, 1)

    assert len(settlements) == 2
    assert all(isinstance(s, TenantSettlement) for s in settlements)
    assert {s.tenant for s in settlements} == {'tenant-1', 'tenant-2'}
    for s in settlements:
        assert s.apartment_settlement == 'apart-polanka'
        assert s.year == 2025
        assert s.month == 1
        assert s.bills_pln == 455.0
        assert s.total_due_pln == 455.0
        assert s.balance_pln == -455.0   # bez przelewów


def test_tenant_settlements_for_three_tenants_split_equally():
    manager = make_manager({
        'tenant-1': make_tenant('A'),
        'tenant-2': make_tenant('B'),
        'tenant-3': make_tenant('C'),
    })
    settlements = manager.get_tenant_settlements('apart-polanka', 2025, 1)
    assert len(settlements) == 3
    assert sum(s.bills_pln for s in settlements) == pytest.approx(910.0)
    assert settlements[0].bills_pln == pytest.approx(910.0 / 3)


def test_tenant_settlements_for_single_tenant():
    manager = make_manager({'tenant-1': make_tenant('Jan Nowak')})
    settlements = manager.get_tenant_settlements('apart-polanka', 2025, 1)

    assert len(settlements) == 1
    assert settlements[0].tenant == 'tenant-1'
    assert settlements[0].bills_pln == 910.0
    assert settlements[0].total_due_pln == 910.0


def test_tenant_settlements_for_apartment_without_tenants():
    manager = make_manager({'tenant-x': make_tenant('Ktoś', apartment='apart-inne')})
    assert manager.get_tenant_settlements('apart-polanka', 2025, 1) == []
    assert manager.get_tenant_settlements('apart-nie-istnieje', 2025, 1) == []