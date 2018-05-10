from myapp.calc import calc_number


def test_calc(send_email):
    result = calc_number(100, 20)
    assert result == 120
