from main import valid_alarm

def test_valid_future_alarm():
    assert(valid_alarm("2030-11-28T12:00")[0]) == True
    assert(valid_alarm("3000-11-28T12:00")[0]) == True


def test_valid_past_alarm():
    assert(valid_alarm("2000-11-28T12:00")[0]) == False
    assert(valid_alarm("2019-11-28T12:00")[0]) == False
