from ..parcel.container import ContainerMeta, CompartmentMeta
from ..parcel.parcel import ParcelMeta

TEST_COMPARTMENT_SMALL = CompartmentMeta(10, 20, 30)
TEST_COMPARTMENT_LARGE = CompartmentMeta(40, 50, 60)
TEST_CONTAINER = ContainerMeta('test',
                               [TEST_COMPARTMENT_SMALL,
                                TEST_COMPARTMENT_LARGE],
                               max_single_weight=50, max_total_weight=100)


def test_can_carry_all_by_weight():
    small_parcel = ParcelMeta(1, 1, 1, 5)
    large_parcel = ParcelMeta(1, 1, 1, 10)
    very_large_parcel = ParcelMeta(1, 1, 1, 60)

    # Test basic case
    assert TEST_CONTAINER.can_carry_all_by_weight([small_parcel, large_parcel])
    # Test single weight too high
    assert not TEST_CONTAINER.can_carry_all_by_weight([large_parcel,
                                                       very_large_parcel])
    # Test total weight too high
    assert not TEST_CONTAINER.can_carry_all_by_weight([large_parcel] * 10
                                                      + [small_parcel])


def test_can_fit():
    small_parcel = ParcelMeta(5, 5, 5, 1)
    tall_parcel = ParcelMeta(5, 5, 50, 1)
    very_tall_parcel = ParcelMeta(5, 5, 70, 1)
    long_parcel = ParcelMeta(50, 5, 5, 1)
    very_long_parcel = ParcelMeta(60, 5, 5, 1)
    large_parcel = ParcelMeta(40, 40, 40, 1)
    very_large_parcel = ParcelMeta(50, 50, 50, 1)

    # Test basic cases
    assert TEST_CONTAINER.can_fit(small_parcel)
    assert TEST_CONTAINER.can_fit(large_parcel)
    assert not TEST_CONTAINER.can_fit(very_large_parcel)
    # Test height
    assert TEST_CONTAINER.can_fit(tall_parcel)
    assert not TEST_CONTAINER.can_fit(very_tall_parcel)
    # Test rotations
    assert TEST_CONTAINER.can_fit(long_parcel)
    assert not TEST_CONTAINER.can_fit(very_long_parcel)


def test_can_fit_all_individually():
    small_parcel = ParcelMeta(5, 5, 5, 1)
    tall_parcel = ParcelMeta(5, 5, 50, 1)
    very_tall_parcel = ParcelMeta(5, 5, 70, 1)
    long_parcel = ParcelMeta(50, 5, 5, 1)
    very_long_parcel = ParcelMeta(60, 5, 5, 1)

    # Test basic cases
    assert TEST_CONTAINER.can_fit_all_individually([small_parcel])
    assert TEST_CONTAINER.can_fit_all_individually([small_parcel] * 1000)
    assert TEST_CONTAINER.can_fit_all_individually([small_parcel, tall_parcel])
    # Test height
    assert not TEST_CONTAINER.can_fit_all_individually([small_parcel,
                                                        very_tall_parcel])
    # Test rotations
    assert TEST_CONTAINER.can_fit_all_individually([long_parcel])
    assert not TEST_CONTAINER.can_fit_all_individually([long_parcel,
                                                        very_long_parcel])
