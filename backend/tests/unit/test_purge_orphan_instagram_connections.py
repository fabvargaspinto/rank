from purge_orphan_instagram_connections import (
    _parse_args,
    orphan_ratio_exceeds_limit,
)


def test_dry_run_is_the_default():
    assert _parse_args([]).apply is False


def test_apply_flag_enables_deletes():
    assert _parse_args(["--apply"]).apply is True


def test_orphan_ratio_aborts_above_twenty_percent():
    assert orphan_ratio_exceeds_limit(3, 10) is True
    assert orphan_ratio_exceeds_limit(2, 10) is False
    assert orphan_ratio_exceeds_limit(0, 0) is False
