"""Tests for the zone manager."""

import json
import tempfile
from pathlib import Path

import numpy as np

from src.zone_manager import Zone, ZoneManager


def _make_square_zone(name="test", x=0, y=0, size=100, severity="high"):
    polygon = np.array([
        [x, y], [x + size, y], [x + size, y + size], [x, y + size]
    ], dtype=np.int32)
    return Zone(name=name, polygon=polygon, severity=severity)


def test_zone_contains_point_inside():
    zone = _make_square_zone(x=0, y=0, size=100)
    assert zone.contains_point((50, 50))


def test_zone_does_not_contain_point_outside():
    zone = _make_square_zone(x=0, y=0, size=100)
    assert not zone.contains_point((200, 200))


def test_zone_contains_point_on_edge():
    zone = _make_square_zone(x=0, y=0, size=100)
    assert zone.contains_point((0, 50))


def test_zone_manager_from_json():
    config = {
        "zones": [
            {"name": "A", "polygon": [[0, 0], [100, 0], [100, 100], [0, 100]], "severity": "high"},
            {"name": "B", "polygon": [[200, 200], [300, 200], [300, 300], [200, 300]]},
        ]
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(config, f)
        f.flush()
        manager = ZoneManager.from_json(f.name)

    assert len(manager.zones) == 2
    assert manager.zones[0].severity == "high"
    assert manager.zones[1].severity == "medium"  # default


def test_check_intrusions():
    manager = ZoneManager(zones=[
        _make_square_zone("A", 0, 0, 100),
        _make_square_zone("B", 200, 200, 100),
    ])
    violated = manager.check_intrusions((50, 50))
    assert len(violated) == 1
    assert violated[0].name == "A"

    violated = manager.check_intrusions((500, 500))
    assert len(violated) == 0
