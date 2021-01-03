from main import kelvin_to_celcius

def test_correct_value():
    assert kelvin_to_celcius(temp = 300) == 26.85
    assert kelvin_to_celcius(temp = 350) == 76.85

def test_negative_value():
    assert kelvin_to_celcius(temp = 0) == -273.15
    assert kelvin_to_celcius(temp =76) == -197.15

def test_string():
    assert kelvin_to_celcius(temp = '0') == -273.15
