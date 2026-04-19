from engine.memory import Memory


def test_turns_are_capped():
    mem = Memory(max_turns=3)
    for i in range(10):
        mem.add_turn("user", str(i))
    assert len(mem.recent_turns()) == 3
    assert mem.recent_turns()[-1][1] == "9"


def test_kv_roundtrip():
    mem = Memory()
    mem.remember("foo", "bar")
    assert mem.recall("foo") == "bar"
    assert mem.recall("missing", "default") == "default"
    mem.forget("foo")
    assert mem.recall("foo") is None
