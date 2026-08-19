import pytest
from src.domain.scoring.scales import score_item, calculate_primary_scales
from src.domain.scoring.core_engine import calculate_core_signals, evaluate_core_conflicts
from src.domain.scoring.patterns import evaluate_full_patterns
from src.domain.scoring.conflicts import evaluate_full_conflicts


def test_score_item_direct_and_reverse():
    # Direct
    assert score_item(1, "D") == 1
    assert score_item(7, "D") == 7
    assert score_item(4, "D") == 4

    # Reverse (8 - x)
    assert score_item(1, "R") == 7
    assert score_item(7, "R") == 1
    assert score_item(4, "R") == 4


def test_primary_scales_normalization():
    # Construct answers where all questions scored = 4 -> mean 4.0 -> normalized = (4-1)/6 * 100 = 50.0
    answers_all_4 = {f"Q{i:03d}": 4 for i in range(1, 161)}
    
    # Reverse items should also give scored=4 when raw=4
    scales = calculate_primary_scales(answers_all_4)
    assert len(scales) == 46

    for scale_id, data in scales.items():
        assert data["normalized"] == 50.0
        assert data["raw_mean"] == 4.0
        assert data["relative_delta"] == 0.0


def test_primary_scales_extreme_values():
    # All raw answers = 7
    # Direct items = 7, Reverse items (R) = 1 (8-7)
    # Check that scoring functions properly
    answers_all_7 = {}
    from src.services.config_loader import PRIMARY_SCALES_MAP
    
    for scale_id, items in PRIMARY_SCALES_MAP.items():
        for q_id, direction in items:
            answers_all_7[q_id] = 7 if direction == "D" else 1  # So scored is always 7

    scales = calculate_primary_scales(answers_all_7)
    for scale_id, data in scales.items():
        assert data["raw_mean"] == 7.0
        assert data["normalized"] == 100.0


def test_core_signals_and_gaps():
    # Test CONSISTENT signal (gap=0) vs CONTRADICTORY (gap=4)
    answers = {
        "Q018": 7, "Q019": 1,  # CS_RECOGNITION: Q018(7)=7, Q019(1)=7 (R) -> mean=7, gap=0 -> conf 0.80
        "Q028": 7, "Q029": 7,  # CS_AVOIDANCE: Q028(7)=7, Q029(7)=1 (R) -> mean=4, gap=6 -> conf 0.35
    }

    signals = calculate_core_signals(answers)
    
    assert "CS_RECOGNITION" in signals
    assert signals["CS_RECOGNITION"]["score"] == 100.0
    assert signals["CS_RECOGNITION"]["confidence"] == 0.80

    assert "CS_AVOIDANCE" in signals
    assert signals["CS_AVOIDANCE"]["confidence"] == 0.35


def test_core_conflicts_evaluation():
    answers = {f"Q{i:03d}": 4 for i in range(1, 161)}
    signals = calculate_core_signals(answers)
    conflicts, top_id, report_mode = evaluate_core_conflicts(signals)

    assert "CF01" in conflicts
    assert "CF02" in conflicts
    assert report_mode in ("CONFLICT", "CONFIGURATION_ONLY")


def test_full_patterns_and_conflicts():
    answers = {f"Q{i:03d}": 4 for i in range(1, 161)}
    scales = calculate_primary_scales(answers)
    
    patterns = evaluate_full_patterns(scales)
    conflicts = evaluate_full_conflicts(scales)

    assert len(patterns) == 37
    assert len(conflicts) == 12
