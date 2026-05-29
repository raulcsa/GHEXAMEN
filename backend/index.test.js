const test = require('node:test');
const assert = require('node:assert');
const { getStatus } = require('./index');

test('backend getStatus function', (t) => {
  const result = getStatus();
  assert.strictEqual(result.status, 'healthy');
  assert.strictEqual(typeof result.timestamp, 'number');
});
