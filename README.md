# Testing tutorial with unitest

1. How and what to test
2. Fixtures
3. Mocking
   1. Where to mock
   2. How to verify mock calls
4. Parametrize
5. Side effects
6. Test raise exceptions


## 1. How and what to test

Test is a function that tests the result and what is called (or not) inside another function.

For example a function that make some calculation, and based on the result sends an email:

```python
def calc_number(one, two):
    result = one + two
    return result
```

And here is how we write a simple function to test the result of calc_number:

```python
import calc_number  # 1

def test_calc_number():
    result = calc_number(10, 30)   # 2
    assert result == 40            # 3
```

How it works:

1. Import the function to be tested (calc_number)
2. Call the function we want to test
3. Verify if the result of the tested function is the expected

To run this test function we just have to call the runner, in our case pytest:

`$ pytest`

And if the test pass, this is what you should see:

```
Results (0.02s):
       1 passed
```

Back to our example function, it is very common to have another functions calls inside the tested function that has no effect in the final result.

Let's change the function we are testing like this:

```python
def calc_number(one, two):
    result = one + two
    if result > 100:
        send_email('test@test.com', result)
    return result
```

Now, the result of the function is the same, the test we did before still passes, but there's something new that we also need to test.

We have a send_email call based on the result of the calculation, and we need to test if it was called or not. This will be explained in the Mocking part.

So, basicaly to test a function, we have to cover all the calls inside the function, and of course the result.


## 2. Fixtures

Fixtures are functions usualy placed in a file called conftest.py in the tests package, which can be used as parameters in the test functions.

It is used to keep code simple and avoid repeated code.

For example, to test some pyramid view function we need a request object, so instead of creating a fake request object everytime we test a view function, we write a fixture so we can reuse the code.

```python
# tests/conftest.py
import pytest
from pyramid.testing import DummyRequest

@pytest.fixture
def dummy_request():
    return DummyRequest()
```

After we create this fixture, we can use it in any test function using the exactly same name of the fixture as parameter:

```python
# tests/test_calc.py
def test_some_view(dummy_request):
    assert dummy_request == testing.DummyRequest()
```

We can also create fixtures based on another fixture.
Imagine now that instead of this dummy_request fixture, we need a request with some user logged on, so we can write a new fixture using the dummy_request one:

```python
# tests/conftest.py
import pytest
from pyramid.testing import DummyRequest

@pytest.fixture
def dummy_request():
    return DummyRequest()

@pytest.fixture
def user_logged_request(dummy_request):  # uses the fixture we defined before
    dummy_request.user = {'fake': 'user'}
    return dummy_request
```

Also, this is a very good practice because keeps the data consistent and easy to change if we need something new for all the requests fixtures.


## 3. Mocking

Mocking means change some class, function, module with a fake object that can simulate results and know how it was called after calling the function being tested.

You can mock using two different ways, using a decorator on the function test or creating the mock object by hand.

Using the decorator patch:

```python
from mock import patch

@patch('mymodule.some_function')
def test_myfunction(some_function):
    myfunction()
```

This is the most common way. You apply the patch in your test function and when you run the function you are testing, the mocked function or class or module will contain an object Mock, which you can configure to return any result you want using the parameter on the test function, and later you can check if this object was called like it meant to be.

To configure the mock to return an specific value, just use the return_value attribute in the Mock parameter. Like:

```python
from mock import patch

@patch('mymodule.some_function')
def test_myfunction(some_function):
    some_function.return_value = 'testing'
    myfunction()
```

Just like that, when you execute your myfunction and the some_function mocked runs, it will returns the 'testing' string.

Another way to mock, is creating the mock by hand like this:

```python
from mock import Mock

def test_myfunction():
    some_function = Mock(return_value='testing')
    myfunction()
```

In this example we assigned a Mock object to the function and it will work exactly like the patch version. Well, not exactly because we used the Mock object, and the patch uses the MagicMock object, which I will explain the difference some time in this text :).

### 3.1 Where to mock

The biggest mistake that the devs face when starting to use Mock is the right place to mock. And in general, this happens because they do not pay attention in how python import modules works (me included).

I will try to explain in some examples what happens when you write the test module and where you have to mock and why.

Let's start with a function that send emails in the package myapp and module mail.py:

```python
# myapp/mail.py

def send_email(address, body, title=None):
    email = {
        'address': address,
        'body': body,
        'title': title or 'Cool email'
    }
    print '\n#### Sending email: %s ####\n' % email
```

Now, we are going to write another function in our app that will use this send_email function.

This will be in the package myapp and module calc.py:

```python
# myapp/calc.py
from myapp.mail import send_email

def calc_number(one, two):
    result = one + two
    if result > 100:
        send_email('user@test.com', result)
    return result
```

So, in this module calc.py we imported the `send_email` function from mail.py module and used it inside our `calc_number` function.

Now, we are going to write a function to test our function `calc_number`, and we need to mock `send_email` so we **don't** actually send an email when we execute the function.

First, I'm going to write the function without the mock, than I'll mock the `send_email` function.

> Pay attention in the modules and packages, this is important.

```python
# tests/test_calc.py
from myapp.calc import calc_number  # 1

def test_calc_number():
    result = calc_number(100, 2)    # 2
    assert result == 102            # 3
```

In this test function, we imported the `calc_number` and executed it without any mock. And this is what happens:

1. Import the function to be tested
2. Execute the function being tested
3. Verify if the result is the expected

If you run like that, the test will pass, but the email will be sent. So, let's mock. But where to mock ?

The first time you will try to mock, using this examples, you will try to mock `myapp.mail.send_email` like this:

```python
# tests/test_calc.py
from mock import patch
from myapp.calc import calc_number  # 1

@patch('myapp.mail.send_email')     # 2
def test_calc_number(send_email):
    result = calc_number(100, 2)    # 3
    assert result == 102            # 4
```

If you execute this test function, the test will pass, but the email still will be sent, and the `send_email` function was not mocked as expected.

But why ? Let's walk through this test function again, and in more details :)

1. Import the function to be tested:
Here, right here. You notice what we did ? I will explain: We imported `calc_number`, but what this means in python ?
When this line of code runs, it will run the module `myapp.calc.py`, *import* everything inside it, define the functions, etc.
So, right now, the `myapp.main.send_email` function was already imported, and the real one. The one that sends the email.
You can also import the `send_email` real function directly from the module `myapp.calc.py`, yes, from the calc module.

2. Apply the decorator for `myapp.mail.send_email`:
So, before the test function runs, this decorator will take action and apply the Mock in the function `myapp.mail.send_email`.
And here you can see that this is the wrong place. We are mocking now, but the other module `myapp.calc.py` already has the real one imported.
This will not have effect inside our test.

3. Execute the function being tested:
So, we are going to run the function we are testing here, and the real `send_email` function will be used and send the email.
And right here you will try everything to fix this and complain with the Mock creator. But you are wrong. :P

4. Verify if the result is the expected:
Well, the result is the one expected, but the `send_email` function still is sending emails and the mock is not working.


Well, after this little trip inside the test, I think now we can fix this. Because now we know which `send_email` function we need to mock.

And here we go again:

```python
# tests/test_calc.py
from mock import patch
from myapp.calc import calc_number

@patch('myapp.calc.send_email')
def test_calc_number(send_email):
    result = calc_number(100, 2)
    assert result == 102
```

Now, we run the tests and we can see that the emails is not being sent and the test pass. Yay \o/.

When the function being tested `calc_number` runs, it will use the `send_email` function from the `myapp.calc.py` module, and the function would be correctly mocked.

So, now we are going to change our `calc_number` a little bit :).

```python
# myapp/calc.py

def calc_number(one, two):
    from myapp.mail import send_email
    result = one + two
    if result > 100:
        send_email('user@test.com', result)
    return result
```

Run the same test before and you will see a big failure.

Why ? Now, we are mocking the `myapp.calc.send_email` funtion that is not there anymore. Now we moved the import of the function `send_email` inside `calc_number`.

So, in this situation, the first test we wrote mocking `myapp.mail.send_email` will work again:

```python
# tests/test_calc.py
from mock import patch
from myapp.calc import calc_number

@patch('myapp.mail.send_email')
def test_calc_number(send_email):
    result = calc_number(100, 2)
    assert result == 102
```

The difference now is that the function `send_email` will be imported only inside `calc_number`, and when this ocurr, it will import the mocked one ;).

### 3.2 How to verify mock calls

Let's start with the first example again:

```python
def calc_number(one, two):
    result = one + two
    if result > 100:
        send_email('test@test.com', result)
    return result
```

Just running a simple test function, we can test the result of this function, but we need to test if the `send_email` function was called, and here enters the Mock:

```python
from mock import patch                            # 1
from myapp.calc import calc_number                 # 2

@patch('myapp.mail.send_email')                    # 3
def test_calc_number_less_than_100(send_email):
    res = calc_number(10, 30)                     # 4
    assert res == 40                              # 5
    send_email.assert_not_called()                # 6
```

How it works:
1. Import the patch decorator
2. Import the function to be tested
3. Apply the decorator to mock the function `send_email`
4. Call the function to be tested
5. Verify if the result of the tested function is the expected
6. Verify if the function was NOT called as expected

In this first example, we passed 10 and 30 as parameter, so we know that the function `send_email` has to be called only if the calculated number is bigger than 100.
So we use the mock function `assert_not_called`, which will return an error if this function was called. If the function is working and the `send_email` was not called, the test will pass.

Now, this is not the only situation we need to test. In the other hand, if the calculated result is bigger the function **MUST** be called.

So we need to write another test to be sure it is working as expected:

```python
from mock import patch
from myapp.calc import calc_number

@patch('myapp.mail.send_email')
def test_calc_number_less_than_100(send_email):
    res = calc_number(60, 50)
    assert res == 110
    send_email.assert_called_with('test@test.com', 110)
```

Now, changing the parameters that we pass to `calc_number`, we know what result is expected, and now we write an `assert_called_with` passing the expected results.
If the function is not called, the test will fail, and we will be sure that this is not working as expected.

There's more assertive functions in mock that we can call like:

* `assert_called`: Assert that the mock was called.
* `assert_called_once`: Assert that the mock was called only one time.
* `assert_called_once_with`: Assert that the mock was called only one time with something.
* `assert_any_call`: Assert that the mock was called with any of the values.
* `assert_has_calls`: Assert that the mock was called with all the values.

This is all covered by the python docs with examples here [https://docs.python.org/dev/library/unittest.mock.html](https://docs.python.org/dev/library/unittest.mock.html)

Besides every `assert_called` function work in the same way, I would like to show an example using `assert_has_calls` to test multiple calls.

Let's change the example to this:

```python
def calc_number(one, two):
    result = one + two
    if result > 100:
        send_email('user1@test.com', result)
    if result > 200:
        send_email('user2@test.com', title='More than 200', body=result)
    return result
```

Now, with these changes, if the result is bigger than 100, we will send an email for the user1, and if it is bigger than 200, we also will send an email to the user2.
So, what do we have to test now ?

* if the result is less than 100, `send_email` must be **NOT** called
* if the result is bigger than 100 and less than 200, `send_email` must be called **ONE** time with the user1 email
* if the result is bigger than 200, `send_email` must be called **TWO** times, one with the user1 and one with the user2

This means we need at least 3 tests for this function now. Let's do it.

First test:

```python
from mock import patch
from myapp.calc import calc_number

@patch('myapp.mail.send_email')
def test_calc_number_less_than_100(send_email):
    res = calc_number(10, 30)
    assert res == 40
    send_email.assert_not_called()
```

Like before, we just mocked the `send_email` function and assert that it was not called.

Second test:

```
from mock import patch
from myapp.calc import calc_number

@patch('myapp.mail.send_email')
def test_calc_number_less_than_100(send_email):
    res = calc_number(50, 60)
    assert res == 110
    send_email.assert_called_once_with('user1@test.com', 110)
```

Now we mocked the function `send_email` and asserted that it was called only **ONE** time with `assert_called_once_with`.

Third test:

```python
from mock import patch, call
from myapp.calc import calc_number

@patch('myapp.mail.send_email')
def test_calc_number_less_than_100(send_email):
    res = calc_number(100, 130)
    assert res == 230
    send_email.assert_has_calls([
        call('user1@test.com', 230),
        call('user2@test.com', title='More than 200', body=result)
    ])
```

Now, we used another function from mock module, `call`. This function simulates how our mock was called and we used with the `assert_has_calls`.
If the `send_email` has exactly these two calls, the test will pass. If if it is not called or it was called one time, or it have different call, it will fail.

> Pay attention here. The call function must be coded exactly identical the real call in the mocked function. If you miss the named parameter, it will fail.


## 4. Parametrize

Parametrize is a feature of the pytest lib and it is very handy if you need to make tests in a function using different values.

Let's use our first example again:

```python
def calc_number(one, two):
    result = one + two
    return result
```

Now, you can write only one test to this function, but with different values it will work in the same way ? Well, this is very simple and we are sure of that, but imagine you are testing a function with more code on it :).

So, instead of writing like five different functions to test this function, we can parametrize values and expected results using pytest:

```python
import pytest
import calc_number

@pytest.mark.parametrize('one_param,two_param,expected_result', [
    (10, 20, 30),
    (40, 40, 80),
    (100, 200, 300),
    (1, 2, 3),
    (8, 8, 16),
])
def test_cal_number(one_param, two_param, expected_result):
    result = calc_number(one_param, two_param)
    assert result == expected_result
```

Using the parametrize decorator, this test function will run five times with the different values and verifying the expected result.


## 5. Side effects
## 6. Test raise exceptions
