# testing
Testing tutorial with unitest

1- How and what to test
2- Fixtures
3- Mocking
   3.1- Where to mock
   3.2- How to mock
4- Parametrize
5- Test raise exceptions
6- Assert called, not called and has calls


1- How and what to test
-

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
-

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
-

Mocking means change some class, function, module with a fake object that can simulate results and know how it was called after calling the test function.

3.1- Where to mock

The biggest mistake that the devs face when starting to use Mock is the right place to mock. And mainly this happens because no one pay attention in how python import modules works (me included).

I will try to explain in some examples what happens when you write the test module and where you have to mock and why.

Let's start with a simple function that send emails in the package myapp and module mail:

# code my_app.mail.py
def send_email(address, body, title=None):
    email_to_send = Email.create(address=address, body=body, title=title)
    email_to_send.send()
#

Now, we are going to write another function in our app that will use this send_email function. This will be in the package my_app and module calc.py.

# code my_app.calc.py
from my_app.mail import send_email

def calc_number(one, two):
    result = one * two
    if result > 100:
        send_email('test@test.com', result)
    return result
#

So, in this module calc.py we imported the send_email function from mail.py module and used it inside our calc_number function.

Now, we are going to write a function test for our function calc_number, and we need to mock send_email so we don't actually send an email when we execute the function.

First, I'm going to write the function without the mock, than I'll mock the send_email function.

- Pay attention in the modules and packages, this is important.

# code tests.test_calc.py
from my_app.calc import calc_number  # 1

def test_calc_number():
    result = calc_number(1, 2)  # 2
    assert result == 3  # 3
#

In this test function, we imported the calc_number and executed it without any mock. And this is what happens:

1- Import the function to be tested
2- Execute the function being tested
3- Verify if the result is the expected

If you run like that, the email will be sent. So, let's mock. But where to mock ?

HERE


3.2- How to mock

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

Now, changing the parameters that we pass to calc_number, we know what result is expected, and now we write an assert_called_with passing the expected results.
If the function is not called, the test will fail, and we will be sure that this is not working as expected.

There's more assertive functions in mock that we can call like:

- assert_called: Assert that the mock was called.
- assert_called_once: Assert that the mock was called only one time.
- assert_called_once_with: Assert that the mock was called only one time with something.
- assert_any_call: Assert that the mock was called with any of the values.
- assert_has_calls: Assert that the mock was called with all the values.

This is all covered by the python docs with examples: https://docs.python.org/dev/library/unittest.mock.html

Besides every assert_called function work in the same way, I would like to show an example using assert_has_calls to test multiple calls.

Let's change the example to this:

# code
def calc_number(one, two):
    result = one * two
    if result > 100:
        send_email('user1@test.com', result)
    if result > 200:
        send_email('user2@test.com', title='More than 200', body=result)
    return result
#

Now, with these changes, if the result is bigger than 100, we will send an email for the user1, and if it is bigger than 200, we also will send an email to the user2.
So, what do we have to test now ?

- if the result is less than 100, send_email must be NOT called
- if the result is bigger than 100 and less than 200, send_email must be called ONE time with the user1 email
- if the result is bigger than 200, send_email must be called TWO times, one with the user1 and one with the user2

This means we need at least 3 tests for this function now. Let's do it.

First test:

#code
from mock import patch
from my_module import calc_number

@patch('my_module.send_email')
def test_calc_number_less_than_100(send_email):
    res = calc_number(10, 30)
    assert res == 40
    send_email.assert_not_called()
#

Like before, we just mocked the send_email function and assert that it was not called.

Second test:

#code
from mock import patch
from my_module import calc_number

@patch('my_module.send_email')
def test_calc_number_less_than_100(send_email):
    res = calc_number(50, 60)
    assert res == 110
    send_email.assert_called_once_with('user1@test.com', 110)
#

Now we mocked the function send_email and asserted that it was called only ONE time with assert_called_once_with.

Third test:

#code
from mock import patch, call
from my_module import calc_number

@patch('my_module.send_email')
def test_calc_number_less_than_100(send_email):
    res = calc_number(100, 130)
    assert res == 230
    send_email.assert_has_calls([
        call('user1@test.com', 230),
        call('user2@test.com', title='More than 200', body=result)
    ])
#

Now, we used another function from mock module, call. The call function simulates how our mock was called and we used with the assert_has_calls.
If the send_email has exactly these two calls, the test will pass. If if it is not called or it was called one time, or it have different call, it will fail.

Pay attention here. The call function must be coded exactly identical the real call in the mocked function. If you miss the named parameter, it will fail.



4- Parametrize
5- Test raise exceptions



