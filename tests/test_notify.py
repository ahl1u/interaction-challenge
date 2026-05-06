from src.db import Transition
from src.notify import should_send_sms


def test_status_not_notifiable_returns_false():
    transition = Transition(False, None, "ordered", None)
    assert should_send_sms(transition, 1.0) is False


def test_confidence_below_threshold_returns_false():
    transition = Transition(False, None, "shipped", None)
    assert should_send_sms(transition, 0.69) is False


def test_same_status_as_last_notified_returns_false():
    transition = Transition(False, "ordered", "shipped", "shipped")
    assert should_send_sms(transition, 1.0) is False


def test_backwards_transition_returns_false():
    transition = Transition(False, "delivered", "shipped", None)
    assert should_send_sms(transition, 1.0) is False


def test_exception_from_delivered_bypasses_rank_check():
    transition = Transition(False, "delivered", "exception", None)
    assert should_send_sms(transition, 1.0) is True


def test_new_shipped_transition_returns_true():
    transition = Transition(True, None, "shipped", None)
    assert should_send_sms(transition, 1.0) is True


def test_forward_transition_returns_true():
    transition = Transition(False, "shipped", "out_for_delivery", "shipped")
    assert should_send_sms(transition, 1.0) is True
