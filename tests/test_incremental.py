import incremental


def fake_pipeline(monkeypatch, counts, stats_for):
    """counts: candle counts per batch; stats_for(count) -> load_dw stats."""
    calls = iter(counts)
    current = {}

    def fake_load_raw():
        count = next(calls)
        current["count"] = count
        return 1, count

    monkeypatch.setattr(incremental, "load_raw", fake_load_raw)
    monkeypatch.setattr(incremental, "load_dw", lambda _id: stats_for(current["count"]))


def new_rows(count):
    return {"inserted": count - 1, "updated": 0, "unchanged": 1, "processed": count}


def test_single_batch_when_caught_up(monkeypatch):
    fake_pipeline(monkeypatch, [2], new_rows)
    totals = incremental.run_incremental()
    assert totals["inserted"] == 1
    assert totals["processed"] == 2


def test_catches_up_over_several_batches(monkeypatch):
    fake_pipeline(monkeypatch, [1000, 1000, 300], new_rows)
    totals = incremental.run_incremental()
    assert totals["inserted"] == 999 + 999 + 299
    assert totals["processed"] == 2300


def test_stops_when_full_batch_makes_no_progress(monkeypatch):
    nothing = lambda c: {"inserted": 0, "updated": 0, "unchanged": c, "processed": c}
    fake_pipeline(monkeypatch, [1000, 1000], nothing)
    totals = incremental.run_incremental()
    assert totals["processed"] == 1000  # stopped after the first batch


def test_respects_max_batches(monkeypatch):
    fake_pipeline(monkeypatch, [1000] * 10, new_rows)
    totals = incremental.run_incremental(max_batches=3)
    assert totals["processed"] == 3000
