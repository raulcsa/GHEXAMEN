const test = require('node:test');
const assert = require('node:assert');
const { greet } = require('./index');

test('frontend greet function', (t) => {
  const result = greet('User');
  assert.strictEqual(result, 'Hello, User! Welcome to our Monorepo App V2.');
});
