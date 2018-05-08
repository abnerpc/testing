# testing
Testing tutorial with unitest

1- How and what to test
2- Fixtures
3- Mocking
4- Parametrize
5- Test raise exceptions
6- Assert called, not called and has calls


1- How and what to test

Test is a function that tests the result and what is called (or not) inside another function.

- It is very common to have another functions calls inside the tested function that has no effect in the final result.

For example a function that do some calculation, and based on the result sends an email:

# code
def calc_number(one, two):
    result = one * two
    if result > 100:
        send_email('test@test.com', result)
    return result
#

This is how we write a simple function to test the result of calc_number:

# code
from my_module import calc_number  # 1

def test_calc_number():
    result = calc_number(10, 30)  # 2
    assert result == 40  # 3
#

How it works:

1- Import the function to be tested (calc_number)
2- Call the function we want to test
3- Verify if the result of the tested function is the expected

Now, the result of the function is not the only thing we need to test in order to have sure that this function is working as expected.
We have a send_email call based on the result of the calculation, and we need to test if it was called or not. This will be explained in the Mocking part.

So, basicaly to test a function, we have to cover all the calls inside the function, and of course the result.


2- Fixtures

Fixtures are functions usualy placed in a file called conftest in the package of the test, that can be used as parameters in the test functions.
It is used to keep code simple and avoid repeated code.

For example, to test some view function we need a request object, so instead of faking the request object everytime we test a view function, we write a fixture so we can reuse the code.

# code
@pytest.fixture
def dummy_request():
    return testing.DummyRequest()
#

After we create this fixture, we can use it in any test just using the same name of the fixture as parameter:

# code
def test_some_view(dummy_request):
    assert dummy_request == testing.DummyRequest()
#

We can also build fixture based on another fixture.
Imagine now that instead of this dummy_request fixture, we need a request with some user logged on, so we can write a new fixture using the dummy_request one:

# code
def user_logged_request(dummy_request, basic_user):
    dummy_request.user = basic_user
    return dummy_request
#

Also, this is a very good practice because keeps the data consistent and easy to change if we need something new for all the requests fixtures.


3- Mocking

Mocking means change some class, function, module with a fake object that can simulate results and know how it was called before calling the test function.

Let's start with the first example again:

# code
def calc_number(one, two):
    result = one * two
    if result > 100:
        send_email('test@test.com', result)
    return result
#

Just running a simple test function, we can test the result of this function, but we need to test if the send_email function was called, and here enters the Mock:

#code
from mock import patch  # 1
from my_module import calc_number  # 2

@patch('my_module.send_email')  # 3
def test_calc_number_less_than_100(send_email):
    res = calc_number(10, 30)  # 4
    assert res == 40  # 5
    send_email.assert_not_called()  # 6
#

How it works:
1- Import the patch decorator
2- Import the function to be tested
3- Apply the decorator to mock the function send_email
4- Call the function to be tested
5- Verify if the result of the tested function is the expected
6- Verify if the function was NOT called as expected

In this first example, we passed 10 and 30 as parameter, so we know that the function send_email has to be called only if the calculated number is bigger than 100.
So we use the mock function assert_not_called, which will return an error if this function was called. If the function is working and the send_email was not called, the test will return success.

Now, this is not the only situation we need to test. In the other hand, if the calculated result is bigger the function MUST be called.

So we need to write another test to be sure it is working as expected:

#code
from mock import patch
from my_module import calc_number

@patch('my_module.send_email')
def test_calc_number_less_than_100(send_email):
    res = calc_number(60, 50)
    assert res == 110
    send_email.assert_called_with('test@test.com', 100)
#

Now, changing the parameters that we pass to calc_number, we know what result is expected, and now we write a assert_called_with passing the expected results.
If the function is not called, the test will fail, and we will be sure that this is not working as expected.






4- Parametrize
5- Test raise exceptions
6- Assert called, not called and has calls



