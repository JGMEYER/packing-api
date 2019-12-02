from ..parcel.parcel import ParcelMeta


def test_volume():
    parcel = ParcelMeta(3, 4, 5, 1)
    assert parcel.volume == 60


def test_legal_orientations():
    parcel = ParcelMeta(3, 4, 5, 1)
    orientations = parcel.legal_orientations()
    assert len(orientations) == 2
    assert (3, 4, 5) in orientations
    assert (4, 3, 5) in orientations
