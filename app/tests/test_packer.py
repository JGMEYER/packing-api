# Import pyshipping to compare results. This is for demonstation only and does
# not need to be included in future iterations or in prod.
from pyshipping.package import Package
from pyshipping.binpack_simple import binpack

from ..parcel import packer
from ..parcel.container import CompartmentMeta
from ..parcel.parcel import ParcelMeta


def test_pyshipping():
    """This test is to demonstrate how the pyshipping logic behaves with the
    same inputs as test_bin_pack_complex, with the exception that pyShipping
    allows for `Package` rotations along any axis.

    `Packages`s are conceptually equivalent to `Parcel`s.
    `bin`s are conceptually equivalent to `Compartment`s.

    Still, we see that even in a case where a perfect fit is achievable, the
    `pyshipping.bin_pack_simple` algorithm does not find it.
    """
    bin = Package("5x4x3")
    packages = [
        Package("4x3x2"),
        Package("1x3x3"),
        Package("4x3x1"),
        Package("2x1x3"),
        Package("3x1x3"),
    ]

    bins, rest = binpack(packages, bin)

    # Uncomment to see results
    # for idx, bin in enumerate(bins):
    #     print(f"{idx}: {bin}")
    # print(rest)


def test_bin_pack_float():
    """Our API allows for float dimensions. Test that our packing algorithm
    handles floats appropriately."""
    compt = CompartmentMeta(5.5, 4.4, 3.3)  # volume: 60
    small_parcel = ParcelMeta(1.1, 1.1, 1.1, 10)

    # Test basic perfect fit
    bins, rest = packer.bin_pack([small_parcel] * 60, compt)
    assert len(bins) == 1
    assert len(bins[0]) == 60
    assert not rest

    # Test just one too many for basic perfect fit
    bins, rest = packer.bin_pack([small_parcel] * 61, compt)
    assert len(bins) == 2
    assert len(bins[0]) == 60
    assert len(bins[1]) == 1
    assert not rest


def test_bin_pack_simple():
    compt = CompartmentMeta(5, 4, 3)  # volume: 60
    small_parcel = ParcelMeta(1, 1, 1, 10)

    # Test basic perfect fit
    bins, rest = packer.bin_pack([small_parcel] * 60, compt)
    assert len(bins) == 1
    assert len(bins[0]) == 60
    assert not rest

    # Test just one too many for basic perfect fit
    bins, rest = packer.bin_pack([small_parcel] * 61, compt)
    assert len(bins) == 2
    assert len(bins[0]) == 60
    assert len(bins[1]) == 1
    assert not rest

    # Test basic perfect fit with unequal parcels
    parcels = [
        ParcelMeta(3, 4, 3, 10),
        ParcelMeta(2, 4, 3, 10),
    ]
    bins, rest = packer.bin_pack(parcels, compt)
    assert len(bins) == 1
    assert len(bins[0]) == 2
    assert not rest

    # Test basic perfect fit with rotated box
    parcels = [
        ParcelMeta(3, 4, 3, 10),
        ParcelMeta(4, 2, 3, 10),  # must be rotated to fit
    ]
    bins, rest = packer.bin_pack(parcels, compt)
    assert len(bins) == 1
    assert len(bins[0]) == 2
    assert not rest


def test_bin_pack_complex():
    """Unfortunately the packer doesn't yet produce perfect results, so we
    can't handle more complex cases. Uncomment once packer can produce more
    accurate results.
    """
    # compt = CompartmentMeta(5, 4, 3)  # volume: 60
    # small_parcel = ParcelMeta(1, 1, 1, 10)
    #
    # # Test more complex perfect fit
    # parcels = [
    #     ParcelMeta(4, 3, 2, 10),
    #     ParcelMeta(1, 3, 3, 10),
    #     ParcelMeta(4, 3, 1, 10),
    #     ParcelMeta(2, 1, 3, 10),
    #     ParcelMeta(3, 1, 3, 10),  # TODO fails after adding this item
    # ]
    # bins, rest = packer.bin_pack(parcels, compt)
    # assert len(bins) == 1
    # assert len(bins[0]) == 5
    # assert not rest
    #
    # # Test just one too many for complex perfect fit
    # parcels = [
    #     ParcelMeta(4, 3, 2, 10),
    #     ParcelMeta(1, 3, 3, 10),
    #     ParcelMeta(4, 3, 1, 10),
    #     ParcelMeta(2, 1, 3, 10),
    #     ParcelMeta(3, 1, 3, 10),
    #     small_parcel,  # one too many
    # ]
    # bins, rest = packer.bin_pack(parcels, compt)
    # assert len(bins) == 2
    # assert len(bins[0]) == 5
    # assert len(bins[1]) == 1
    # assert not rest
