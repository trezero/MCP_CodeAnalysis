# Python Style Guide

<!-- MEMORY_ANCHOR: python_style_guide -->

This document outlines the coding standards for Python code in this project.

## Why

Consistent code style makes it easier for developers to read, understand, and maintain the codebase. By following these standards, we ensure that our code is clean, readable, and maintainable.

## General Guidelines

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for code style
- Use [Black](https://black.readthedocs.io/) for code formatting
- Use [Pylint](https://pylint.org/) for code linting
- Use [mypy](https://mypy.readthedocs.io/) for static type checking
- Use Python 3.6+ features and idioms

## Code Formatting

### Indentation

- Use 4 spaces for indentation
- Do not use tabs

```python
# Good
def good_function():
    do_something()
    
# Bad
def bad_function():
	do_something()  # Uses tab
```

### Line Length

- Maximum line length is 88 characters (Black's default)
- Use parentheses for line continuation

```python
# Good
long_string = (
    "This is a very long string that would exceed the line length limit "
    "if it were not split across multiple lines."
)

# Bad
long_string = "This is a very long string that would exceed the line length limit if it were not split across multiple lines."
```

### Imports

- Group imports in the following order:
  1. Standard library imports
  2. Related third-party imports
  3. Local application/library specific imports
- Separate each group with a blank line
- Sort imports alphabetically within each group

```python
# Good
import os
import sys
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from mymodule import myfunction
from mypackage.mymodule import another_function
```

### Whitespace

- Use whitespace to improve readability
- Add a space after commas, colons, and semicolons
- Do not add a space before commas, colons, or semicolons
- Add spaces around operators

```python
# Good
x = 1
y = 2
z = x + y
items = [1, 2, 3]
d = {"key": "value"}

# Bad
x=1
y=2
z=x+y
items=[1,2,3]
d={"key":"value"}
```

## Naming Conventions

### Variables and Functions

- Use `snake_case` for variable and function names
- Use descriptive names that convey the purpose

```python
# Good
user_count = 10
def calculate_average(numbers):
    return sum(numbers) / len(numbers)

# Bad
usercount = 10
def calcavg(numbers):
    return sum(numbers) / len(numbers)
```

### Classes

- Use `CamelCase` for class names
- Use descriptive names that convey the purpose

```python
# Good
class UserProfile:
    def __init__(self, name):
        self.name = name

# Bad
class userprofile:
    def __init__(self, name):
        self.name = name
```

### Constants

- Use `UPPER_CASE` for constants
- Use descriptive names that convey the purpose

```python
# Good
MAX_RETRY_COUNT = 3
DEFAULT_TIMEOUT = 30

# Bad
max_retry = 3
defaultTimeout = 30
```

### Private Variables and Methods

- Use a leading underscore for private variables and methods

```python
# Good
class MyClass:
    def __init__(self):
        self._private_variable = 10
        
    def _private_method(self):
        return self._private_variable

# Bad
class MyClass:
    def __init__(self):
        self.privateVariable = 10
        
    def privateMethod(self):
        return self.privateVariable
```

## Type Hints

- Use type hints for function parameters and return values
- Use `Optional` for parameters that can be `None`
- Use `Union` for parameters that can be multiple types
- Use `Any` sparingly, only when the type is truly unknown

```python
# Good
from typing import Dict, List, Optional, Union

def process_data(data: List[Dict[str, Union[str, int]]]) -> Optional[Dict[str, int]]:
    if not data:
        return None
    result = {}
    for item in data:
        key = item.get("key", "")
        value = item.get("value", 0)
        if isinstance(key, str) and isinstance(value, int):
            result[key] = value
    return result

# Bad
def process_data(data):
    if not data:
        return None
    result = {}
    for item in data:
        key = item.get("key", "")
        value = item.get("value", 0)
        result[key] = value
    return result
```

## Docstrings

- Use [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Write docstrings for all modules, classes, and functions
- Include a "Why" section in docstrings for non-trivial functions

```python
"""Module for processing user data.

This module provides functions for processing user data, including
validation, transformation, and storage.
"""

def process_user_data(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process user data for storage.
    
    This function validates, transforms, and prepares user data for storage.
    
    Why:
        Raw user data may contain invalid or inconsistent values. This function
        ensures that the data is valid and consistent before storage.
    
    Args:
        user_data: A dictionary containing user data.
            Required keys:
            - name: The user's name.
            - email: The user's email address.
            Optional keys:
            - age: The user's age.
            - address: The user's address.
    
    Returns:
        A dictionary containing processed user data.
    
    Raises:
        ValueError: If required keys are missing or invalid.
    
    Examples:
        >>> process_user_data({"name": "John", "email": "john@example.com"})
        {"name": "John", "email": "john@example.com", "created_at": "2023-01-01T00:00:00Z"}
    """
    # Implementation
```

## Error Handling

- Use specific exception types
- Handle exceptions at the appropriate level
- Include helpful error messages

```python
# Good
def read_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except PermissionError:
        raise PermissionError(f"Permission denied: {file_path}")
    except Exception as e:
        raise RuntimeError(f"Error reading file: {file_path}") from e

# Bad
def read_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except:
        raise Exception("Error")
```

## Testing

- Write tests for all code
- Use [pytest](https://docs.pytest.org/) for testing
- Use [pytest-cov](https://pytest-cov.readthedocs.io/) for coverage reporting
- Aim for 80% or higher test coverage

```python
# Good
def add(a, b):
    return a + b

def test_add():
    assert add(1, 2) == 3
    assert add(-1, 1) == 0
    assert add(0, 0) == 0
```

## Memory Anchors

- Use memory anchors to mark important sections of code
- Format: `# MEMORY_ANCHOR: anchor_type`
- Common anchor types:
  - `performance_bottleneck`: Code that may cause performance issues
  - `architecture_decision`: Code that reflects an important architectural decision
  - `security_sensitive`: Code that handles sensitive data or operations
  - `error_prone`: Code that is prone to errors or requires careful attention

```python
# MEMORY_ANCHOR: performance_bottleneck
def expensive_operation():
    """This operation is expensive and may cause performance issues."""
    # Implementation
```

## Component Maturity

- Include a maturity level in component docstrings
- Format: `Maturity: maturity_level`
- Maturity levels:
  - `experimental`: New component, not ready for production use
  - `beta`: Component is functional but may have issues
  - `stable`: Component is well-tested and ready for production use
  - `deprecated`: Component is being phased out

```python
"""User Authentication Module

This module provides functions for user authentication.

Maturity: stable
"""
```

## Why Section

- Include a "Why" section in docstrings for non-trivial functions
- Explain the rationale behind the function or component
- Include any trade-offs or alternatives considered

```python
def process_data(data):
    """Process data for analysis.
    
    Why:
        Raw data may contain outliers or missing values that can skew analysis.
        This function removes outliers and imputes missing values to ensure
        accurate analysis results.
    
    Args:
        data: The data to process.
    
    Returns:
        Processed data.
    """
    # Implementation
```

## Linting and Formatting

- Use Black for code formatting
- Use Pylint for code linting
- Use mypy for static type checking
- Configure your editor to run these tools automatically

```bash
# Format code with Black
black .

# Lint code with Pylint
pylint your_module

# Check types with mypy
mypy your_module
```

## Examples

### Good Example

```python
"""User Authentication Module

This module provides functions for user authentication.

Maturity: stable
"""

import hashlib
import os
from typing import Dict, Optional

# MEMORY_ANCHOR: security_sensitive
def hash_password(password: str) -> str:
    """Hash a password for storage.
    
    Why:
        Storing passwords in plain text is a security risk. Hashing passwords
        with a salt ensures that even if the database is compromised, the
        passwords cannot be easily recovered.
    
    Args:
        password: The password to hash.
    
    Returns:
        A string containing the hashed password.
    
    Examples:
        >>> hash_password("password123")
        'a1b2c3d4e5f6g7h8i9j0'
    """
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000
    )
    return salt.hex() + key.hex()

def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify a password against a stored hash.
    
    Why:
        When a user logs in, we need to verify that the provided password
        matches the stored hash without storing the original password.
    
    Args:
        stored_password: The stored hashed password.
        provided_password: The password provided by the user.
    
    Returns:
        True if the password matches, False otherwise.
    
    Examples:
        >>> verify_password(hash_password("password123"), "password123")
        True
        >>> verify_password(hash_password("password123"), "wrong_password")
        False
    """
    salt = bytes.fromhex(stored_password[:64])
    stored_key = bytes.fromhex(stored_password[64:])
    key = hashlib.pbkdf2_hmac(
        'sha256',
        provided_password.encode('utf-8'),
        salt,
        100000
    )
    return key == stored_key

class UserAuth:
    """User authentication manager.
    
    This class manages user authentication, including login and logout.
    
    Attributes:
        users: A dictionary mapping usernames to hashed passwords.
    """
    
    def __init__(self):
        """Initialize the UserAuth instance."""
        self._users: Dict[str, str] = {}
    
    def register(self, username: str, password: str) -> bool:
        """Register a new user.
        
        Args:
            username: The username to register.
            password: The password to register.
        
        Returns:
            True if registration was successful, False otherwise.
        
        Raises:
            ValueError: If the username is already taken.
        """
        if username in self._users:
            raise ValueError(f"Username already taken: {username}")
        
        self._users[username] = hash_password(password)
        return True
    
    def login(self, username: str, password: str) -> bool:
        """Log in a user.
        
        Args:
            username: The username to log in.
            password: The password to log in.
        
        Returns:
            True if login was successful, False otherwise.
        """
        if username not in self._users:
            return False
        
        return verify_password(self._users[username], password)
```

### Bad Example

```python
# User authentication
import hashlib, os

def hash_pw(pw):
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', pw.encode('utf-8'), salt, 100000)
    return salt.hex() + key.hex()

def verify_pw(stored_pw, provided_pw):
    salt = bytes.fromhex(stored_pw[:64])
    stored_key = bytes.fromhex(stored_pw[64:])
    key = hashlib.pbkdf2_hmac('sha256', provided_pw.encode('utf-8'), salt, 100000)
    return key == stored_key

class UserAuth:
    def __init__(self):
        self.users = {}
    
    def register(self, username, password):
        if username in self.users:
            raise ValueError(f"Username already taken: {username}")
        
        self.users[username] = hash_pw(password)
        return True
    
    def login(self, username, password):
        if username not in self.users:
            return False
        
        return verify_pw(self.users[username], password)
``` 