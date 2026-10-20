from sds_origin_trainer.processors.stat_processor import StatPatch


def test_stat_patch_packs_float():
    p = StatPatch(0x00, "<f", 9999999.0)
    import struct
    assert struct.unpack("<f", struct.pack(p.fmt, p.value))[0] == 9999999.0