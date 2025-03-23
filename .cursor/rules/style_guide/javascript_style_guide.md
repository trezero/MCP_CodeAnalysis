# JavaScript Style Guide

<!-- MEMORY_ANCHOR: javascript_style_guide -->

This document outlines the coding standards for JavaScript code in this project.

## Why

Consistent code style makes it easier for developers to read, understand, and maintain the codebase. By following these standards, we ensure that our code is clean, readable, and maintainable.

## General Guidelines

- Use [ESLint](https://eslint.org/) for code linting
- Use [Prettier](https://prettier.io/) for code formatting
- Use [TypeScript](https://www.typescriptlang.org/) for type safety
- Use modern JavaScript features (ES6+)
- Follow functional programming principles where appropriate

## Code Formatting

### Indentation

- Use 2 spaces for indentation
- Do not use tabs

```javascript
// Good
function goodFunction() {
  doSomething();
}

// Bad
function badFunction() {
	doSomething(); // Uses tab
}
```

### Line Length

- Maximum line length is 80 characters
- Use line breaks for long lines

```javascript
// Good
const longString =
  'This is a very long string that would exceed the line length limit ' +
  'if it were not split across multiple lines.';

// Bad
const longString = 'This is a very long string that would exceed the line length limit if it were not split across multiple lines.';
```

### Semicolons

- Use semicolons at the end of statements
- Do not rely on automatic semicolon insertion

```javascript
// Good
const x = 1;
const y = 2;
const z = x + y;

// Bad
const x = 1
const y = 2
const z = x + y
```

### Quotes

- Use single quotes for string literals
- Use template literals for string interpolation

```javascript
// Good
const name = 'John';
const greeting = `Hello, ${name}!`;

// Bad
const name = "John";
const greeting = "Hello, " + name + "!";
```

### Whitespace

- Use whitespace to improve readability
- Add a space after commas, colons, and semicolons
- Do not add a space before commas, colons, or semicolons
- Add spaces around operators

```javascript
// Good
const x = 1;
const y = 2;
const z = x + y;
const items = [1, 2, 3];
const obj = { key: 'value' };

// Bad
const x=1;
const y=2;
const z=x+y;
const items=[1,2,3];
const obj={key:'value'};
```

### Braces

- Use braces for all blocks, even single-line blocks
- Place opening braces on the same line as the statement
- Place closing braces on a new line

```javascript
// Good
if (condition) {
  doSomething();
}

// Bad
if (condition) doSomething();

// Bad
if (condition)
{
  doSomething();
}
```

### Comments

- Use `//` for single-line comments
- Use `/* */` for multi-line comments
- Use JSDoc comments for documentation

```javascript
// Good: Single-line comment

/*
 * Good: Multi-line comment
 * with multiple lines
 */

/**
 * Good: JSDoc comment
 * @param {string} name - The name parameter
 * @returns {string} The greeting
 */
function greet(name) {
  return `Hello, ${name}!`;
}
```

## Naming Conventions

### Variables and Functions

- Use `camelCase` for variable and function names
- Use descriptive names that convey the purpose

```javascript
// Good
const userCount = 10;
function calculateAverage(numbers) {
  return numbers.reduce((sum, num) => sum + num, 0) / numbers.length;
}

// Bad
const usercount = 10;
function calcavg(numbers) {
  return numbers.reduce((sum, num) => sum + num, 0) / numbers.length;
}
```

### Classes

- Use `PascalCase` for class names
- Use descriptive names that convey the purpose

```javascript
// Good
class UserProfile {
  constructor(name) {
    this.name = name;
  }
}

// Bad
class userprofile {
  constructor(name) {
    this.name = name;
  }
}
```

### Constants

- Use `UPPER_SNAKE_CASE` for constants
- Use descriptive names that convey the purpose

```javascript
// Good
const MAX_RETRY_COUNT = 3;
const DEFAULT_TIMEOUT = 30;

// Bad
const maxRetry = 3;
const defaultTimeout = 30;
```

### Private Variables and Methods

- Use a leading underscore for private variables and methods
- Use the `#` prefix for truly private class fields (ES2020+)

```javascript
// Good (ES2020+)
class MyClass {
  #privateVariable = 10;
  
  #privateMethod() {
    return this.#privateVariable;
  }
  
  publicMethod() {
    return this.#privateMethod();
  }
}

// Good (pre-ES2020)
class MyClass {
  constructor() {
    this._privateVariable = 10;
  }
  
  _privateMethod() {
    return this._privateVariable;
  }
  
  publicMethod() {
    return this._privateMethod();
  }
}

// Bad
class MyClass {
  constructor() {
    this.privateVariable = 10;
  }
  
  privateMethod() {
    return this.privateVariable;
  }
  
  publicMethod() {
    return this.privateMethod();
  }
}
```

## TypeScript

- Use TypeScript for all new code
- Use explicit types for function parameters and return values
- Use interfaces for object shapes
- Use type aliases for complex types
- Use generics for reusable code

```typescript
// Good
interface User {
  id: string;
  name: string;
  email: string;
  age?: number;
}

function processUser(user: User): User {
  return {
    ...user,
    name: user.name.trim()
  };
}

// Bad
function processUser(user) {
  return {
    ...user,
    name: user.name.trim()
  };
}
```

## Functions

### Arrow Functions

- Use arrow functions for anonymous functions
- Use function declarations for named functions
- Use concise body syntax when appropriate

```javascript
// Good
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(num => num * 2);

// Good
function calculateAverage(numbers) {
  return numbers.reduce((sum, num) => sum + num, 0) / numbers.length;
}

// Bad
const calculateAverage = function(numbers) {
  return numbers.reduce(function(sum, num) {
    return sum + num;
  }, 0) / numbers.length;
};
```

### Default Parameters

- Use default parameters instead of conditional expressions

```javascript
// Good
function greet(name = 'Guest') {
  return `Hello, ${name}!`;
}

// Bad
function greet(name) {
  name = name || 'Guest';
  return `Hello, ${name}!`;
}
```

### Rest Parameters

- Use rest parameters instead of `arguments`

```javascript
// Good
function sum(...numbers) {
  return numbers.reduce((total, num) => total + num, 0);
}

// Bad
function sum() {
  let total = 0;
  for (let i = 0; i < arguments.length; i++) {
    total += arguments[i];
  }
  return total;
}
```

## Objects and Arrays

### Object Shorthand

- Use object property shorthand
- Use object method shorthand

```javascript
// Good
const name = 'John';
const age = 30;
const user = { name, age };

// Bad
const name = 'John';
const age = 30;
const user = { name: name, age: age };

// Good
const user = {
  name: 'John',
  greet() {
    return `Hello, ${this.name}!`;
  }
};

// Bad
const user = {
  name: 'John',
  greet: function() {
    return `Hello, ${this.name}!`;
  }
};
```

### Destructuring

- Use object destructuring
- Use array destructuring

```javascript
// Good
const user = { name: 'John', age: 30 };
const { name, age } = user;

// Bad
const user = { name: 'John', age: 30 };
const name = user.name;
const age = user.age;

// Good
const numbers = [1, 2, 3];
const [first, second, third] = numbers;

// Bad
const numbers = [1, 2, 3];
const first = numbers[0];
const second = numbers[1];
const third = numbers[2];
```

### Spread Operator

- Use the spread operator to copy objects and arrays

```javascript
// Good
const original = { a: 1, b: 2 };
const copy = { ...original };

// Bad
const original = { a: 1, b: 2 };
const copy = Object.assign({}, original);

// Good
const original = [1, 2, 3];
const copy = [...original];

// Bad
const original = [1, 2, 3];
const copy = original.slice();
```

## Control Flow

### Loops

- Use `for...of` for arrays
- Use `for...in` for objects
- Use `forEach`, `map`, `filter`, and `reduce` for array operations

```javascript
// Good
const numbers = [1, 2, 3, 4, 5];
for (const num of numbers) {
  console.log(num);
}

// Bad
const numbers = [1, 2, 3, 4, 5];
for (let i = 0; i < numbers.length; i++) {
  console.log(numbers[i]);
}

// Good
const obj = { a: 1, b: 2, c: 3 };
for (const key in obj) {
  if (Object.prototype.hasOwnProperty.call(obj, key)) {
    console.log(`${key}: ${obj[key]}`);
  }
}

// Bad
const obj = { a: 1, b: 2, c: 3 };
const keys = Object.keys(obj);
for (let i = 0; i < keys.length; i++) {
  const key = keys[i];
  console.log(`${key}: ${obj[key]}`);
}
```

### Conditionals

- Use `===` and `!==` instead of `==` and `!=`
- Use ternary operators for simple conditionals
- Use `if...else` for complex conditionals

```javascript
// Good
if (value === 0) {
  // ...
}

// Bad
if (value == 0) {
  // ...
}

// Good
const result = condition ? valueIfTrue : valueIfFalse;

// Bad
let result;
if (condition) {
  result = valueIfTrue;
} else {
  result = valueIfFalse;
}
```

### Error Handling

- Use `try...catch` for error handling
- Use specific error types
- Include helpful error messages

```javascript
// Good
async function fetchData(url) {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Error fetching data: ${error.message}`);
    throw error;
  }
}

// Bad
async function fetchData(url) {
  try {
    const response = await fetch(url);
    return await response.json();
  } catch (error) {
    console.error('Error');
    throw error;
  }
}
```

## Asynchronous Code

### Promises

- Use `async/await` for asynchronous code
- Use Promise chaining when appropriate
- Handle errors with `try...catch`

```javascript
// Good
async function fetchData(url) {
  try {
    const response = await fetch(url);
    return await response.json();
  } catch (error) {
    console.error(`Error fetching data: ${error.message}`);
    throw error;
  }
}

// Good (Promise chaining)
function fetchData(url) {
  return fetch(url)
    .then(response => response.json())
    .catch(error => {
      console.error(`Error fetching data: ${error.message}`);
      throw error;
    });
}

// Bad
function fetchData(url, callback) {
  fetch(url)
    .then(response => response.json())
    .then(data => callback(null, data))
    .catch(error => callback(error));
}
```

## Modules

- Use ES modules (`import`/`export`)
- Use named exports for multiple exports
- Use default exports for single exports

```javascript
// Good
// math.js
export function add(a, b) {
  return a + b;
}

export function subtract(a, b) {
  return a - b;
}

// main.js
import { add, subtract } from './math';

// Good
// user.js
export default class User {
  constructor(name) {
    this.name = name;
  }
}

// main.js
import User from './user';
```

## JSDoc Comments

- Use JSDoc comments for documentation
- Include a description, parameters, return value, and examples
- Include a "Why" section for non-trivial functions

```javascript
/**
 * Process user data for storage.
 * 
 * This function validates, transforms, and prepares user data for storage.
 * 
 * Why:
 * Raw user data may contain invalid or inconsistent values. This function
 * ensures that the data is valid and consistent before storage.
 * 
 * @param {Object} userData - A dictionary containing user data.
 * @param {string} userData.name - The user's name.
 * @param {string} userData.email - The user's email address.
 * @param {number} [userData.age] - The user's age.
 * @param {string} [userData.address] - The user's address.
 * @returns {Object} A dictionary containing processed user data.
 * @throws {Error} If required keys are missing or invalid.
 * 
 * @example
 * processUserData({ name: "John", email: "john@example.com" });
 * // Returns: { name: "John", email: "john@example.com", createdAt: "2023-01-01T00:00:00Z" }
 */
function processUserData(userData) {
  // Implementation
}
```

## Memory Anchors

- Use memory anchors to mark important sections of code
- Format: `// MEMORY_ANCHOR: anchor_type`
- Common anchor types:
  - `performance_bottleneck`: Code that may cause performance issues
  - `architecture_decision`: Code that reflects an important architectural decision
  - `security_sensitive`: Code that handles sensitive data or operations
  - `error_prone`: Code that is prone to errors or requires careful attention

```javascript
// MEMORY_ANCHOR: performance_bottleneck
function expensiveOperation() {
  // This operation is expensive and may cause performance issues
}
```

## Component Maturity

- Include a maturity level in component JSDoc comments
- Format: `@maturity {maturity_level}`
- Maturity levels:
  - `experimental`: New component, not ready for production use
  - `beta`: Component is functional but may have issues
  - `stable`: Component is well-tested and ready for production use
  - `deprecated`: Component is being phased out

```javascript
/**
 * User Authentication Module
 * 
 * This module provides functions for user authentication.
 * 
 * @module UserAuth
 * @maturity {stable}
 */
```

## Why Section

- Include a "Why" section in JSDoc comments for non-trivial functions
- Explain the rationale behind the function or component
- Include any trade-offs or alternatives considered

```javascript
/**
 * Process data for analysis.
 * 
 * Why:
 * Raw data may contain outliers or missing values that can skew analysis.
 * This function removes outliers and imputes missing values to ensure
 * accurate analysis results.
 * 
 * @param {Array} data - The data to process.
 * @returns {Array} Processed data.
 */
function processData(data) {
  // Implementation
}
```

## Linting and Formatting

- Use ESLint for code linting
- Use Prettier for code formatting
- Configure your editor to run these tools automatically

```bash
# Lint code with ESLint
eslint .

# Format code with Prettier
prettier --write .
```

## Examples

### Good Example

```javascript
/**
 * User Authentication Module
 * 
 * This module provides functions for user authentication.
 * 
 * @module UserAuth
 * @maturity {stable}
 */

import crypto from 'crypto';

/**
 * Hash a password for storage.
 * 
 * Why:
 * Storing passwords in plain text is a security risk. Hashing passwords
 * with a salt ensures that even if the database is compromised, the
 * passwords cannot be easily recovered.
 * 
 * @param {string} password - The password to hash.
 * @returns {string} A string containing the hashed password.
 * 
 * @example
 * hashPassword("password123");
 * // Returns: 'a1b2c3d4e5f6g7h8i9j0'
 */
// MEMORY_ANCHOR: security_sensitive
function hashPassword(password) {
  const salt = crypto.randomBytes(16).toString('hex');
  const hash = crypto.pbkdf2Sync(password, salt, 1000, 64, 'sha512').toString('hex');
  return `${salt}:${hash}`;
}

/**
 * Verify a password against a stored hash.
 * 
 * Why:
 * When a user logs in, we need to verify that the provided password
 * matches the stored hash without storing the original password.
 * 
 * @param {string} storedPassword - The stored hashed password.
 * @param {string} providedPassword - The password provided by the user.
 * @returns {boolean} True if the password matches, False otherwise.
 * 
 * @example
 * verifyPassword(hashPassword("password123"), "password123");
 * // Returns: true
 * verifyPassword(hashPassword("password123"), "wrong_password");
 * // Returns: false
 */
function verifyPassword(storedPassword, providedPassword) {
  const [salt, hash] = storedPassword.split(':');
  const providedHash = crypto.pbkdf2Sync(providedPassword, salt, 1000, 64, 'sha512').toString('hex');
  return hash === providedHash;
}

/**
 * User authentication manager.
 * 
 * This class manages user authentication, including login and logout.
 */
class UserAuth {
  /**
   * Create a new UserAuth instance.
   */
  constructor() {
    this.#users = new Map();
  }
  
  /**
   * Private users map.
   * @type {Map<string, string>}
   */
  #users;
  
  /**
   * Register a new user.
   * 
   * @param {string} username - The username to register.
   * @param {string} password - The password to register.
   * @returns {boolean} True if registration was successful, False otherwise.
   * @throws {Error} If the username is already taken.
   */
  register(username, password) {
    if (this.#users.has(username)) {
      throw new Error(`Username already taken: ${username}`);
    }
    
    this.#users.set(username, hashPassword(password));
    return true;
  }
  
  /**
   * Log in a user.
   * 
   * @param {string} username - The username to log in.
   * @param {string} password - The password to log in.
   * @returns {boolean} True if login was successful, False otherwise.
   */
  login(username, password) {
    if (!this.#users.has(username)) {
      return false;
    }
    
    return verifyPassword(this.#users.get(username), password);
  }
}

export default UserAuth;
export { hashPassword, verifyPassword };
```

### Bad Example

```javascript
// User authentication
import crypto from 'crypto';

function hashPw(pw) {
  var salt = crypto.randomBytes(16).toString('hex');
  var hash = crypto.pbkdf2Sync(pw, salt, 1000, 64, 'sha512').toString('hex');
  return salt + ':' + hash;
}

function verifyPw(storedPw, providedPw) {
  var parts = storedPw.split(':');
  var salt = parts[0];
  var hash = parts[1];
  var providedHash = crypto.pbkdf2Sync(providedPw, salt, 1000, 64, 'sha512').toString('hex');
  return hash == providedHash;
}

class UserAuth {
  constructor() {
    this.users = {};
  }
  
  register(username, password) {
    if (this.users[username]) {
      throw new Error('Username already taken: ' + username);
    }
    
    this.users[username] = hashPw(password);
    return true;
  }
  
  login(username, password) {
    if (!this.users[username]) {
      return false;
    }
    
    return verifyPw(this.users[username], password);
  }
}

module.exports = UserAuth;
``` 