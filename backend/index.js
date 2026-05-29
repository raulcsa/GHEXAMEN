// Backend main application file
function getStatus() {
  return { status: 'healthy', timestamp: Date.now() };
}

function validateSchema() {
  // Mock validation logic for demonstration
  const requiredFields = ['status'];
  const missingFields = requiredFields.filter(field => !getStatus().hasOwnProperty(field));

  if (missingFields.length > 0) {
    throw new Error(`Missing required fields: ${missingFields.join(', ')}`);
  }

  console.log('✅ Backend schema validation passed');
}

module.exports = { getStatus, validateSchema };
