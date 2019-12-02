from ..parcel import packer
from ..parcel.container import CompartmentMeta
from ..parcel.parcel import ParcelMeta


def test_binpack_simple():
    compt = CompartmentMeta(5, 4, 3)  # volume: 60
    small_parcel = ParcelMeta(1, 1, 1, 10)

    # Test basic perfect fit
    bins, rest = packer.binpack([small_parcel] * 60, compt)
    assert len(bins) == 1
    assert len(bins[0]) == 60
    assert not rest

    # Test just one too many for basic perfect fit
    bins, rest = packer.binpack([small_parcel] * 61, compt)
    assert len(bins) == 2
    assert len(bins[0]) == 60
    assert len(bins[1]) == 1
    assert not rest

    # Test basic perfect fit with unequal parcels
    parcels = [
        ParcelMeta(3, 4, 3, 10),
        ParcelMeta(2, 4, 3, 10),
    ]
    bins, rest = packer.binpack(parcels, compt)
    assert len(bins) == 1
    assert len(bins[0]) == 2
    assert not rest

    # Test basic perfect fit with rotated box
    parcels = [
        ParcelMeta(3, 4, 3, 10),
        ParcelMeta(4, 2, 3, 10),  # must be rotated to fit
    ]
    bins, rest = packer.binpack(parcels, compt)
    assert len(bins) == 1
    assert len(bins[0]) == 2
    assert not rest


def test_binpack_complex():
    compt = CompartmentMeta(5, 4, 3)  # volume: 60
    small_parcel = ParcelMeta(1, 1, 1, 10)

    # Test more complex perfect fit
    parcels = [
        ParcelMeta(4, 3, 2, 10),
        ParcelMeta(1, 3, 3, 10),
        ParcelMeta(4, 3, 1, 10),
        ParcelMeta(2, 1, 3, 10),
        ParcelMeta(3, 1, 3, 10),  # TODO fails after adding this item
    ]
    bins, rest = packer.binpack(parcels, compt)

    # TODO rm
    for idx, bin in enumerate(bins):
        print(f"{idx}: {bin}")

    assert len(bins) == 1
    assert len(bins[0]) == 5
    assert not rest

    # Test just one too many for complex perfect fit
    parcels = [
        ParcelMeta(4, 3, 2, 10),
        ParcelMeta(1, 3, 3, 10),
        ParcelMeta(4, 3, 1, 10),
        ParcelMeta(2, 1, 3, 10),
        ParcelMeta(3, 1, 3, 10),
        small_parcel,  # one too many
    ]
    bins, rest = packer.binpack(parcels, compt)
    assert len(bins) == 2
    assert len(bins[0]) == 5
    assert len(bins[1]) == 1
    assert not rest
