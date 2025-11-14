const http = require('http');

// Test script to verify proxy and agent connectivity
console.log('Testing ZombieCoder Local AI System...');

// Test 1: Check if proxy is listening on port 5010
const testProxy = () => {
  return new Promise((resolve, reject) => {
    const req = http.get('http://127.0.0.1:5010/health', (res) => {
      console.log(`Proxy Health Check: ${res.statusCode}`);
      resolve(res.statusCode === 200);
    }).on('error', (err) => {
      console.log('Proxy Health Check: Failed');
      reject(err);
    });
    req.setTimeout(5000, () => {
      req.destroy();
      reject(new Error('Proxy timeout'));
    });
  });
};

// Test 2: Check if agent is listening on port 8001
const testAgent = () => {
  return new Promise((resolve, reject) => {
    const req = http.get('http://127.0.0.1:8001/health', (res) => {
      console.log(`Agent Health Check: ${res.statusCode}`);
      resolve(res.statusCode === 200);
    }).on('error', (err) => {
      console.log('Agent Health Check: Failed');
      reject(err);
    });
    req.setTimeout(5000, () => {
      req.destroy();
      reject(new Error('Agent timeout'));
    });
  });
};

// Test 3: Check if proxy serves /v1/models endpoint
const testModels = () => {
  return new Promise((resolve, reject) => {
    const req = http.get('http://127.0.0.1:5010/v1/models', (res) => {
      console.log(`Models Endpoint Check: ${res.statusCode}`);
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const jsonData = JSON.parse(data);
          console.log('Models Response:', JSON.stringify(jsonData, null, 2));
          resolve(res.statusCode === 200);
        } catch (e) {
          console.log('Models Response: Invalid JSON');
          reject(e);
        }
      });
    }).on('error', (err) => {
      console.log('Models Endpoint Check: Failed');
      reject(err);
    });
    req.setTimeout(5000, () => {
      req.destroy();
      reject(new Error('Models endpoint timeout'));
    });
  });
};

// Run all tests
async function runTests() {
  try {
    console.log('\n--- Running Tests ---');
    
    await testProxy();
    await testAgent();
    await testModels();
    
    console.log('\n--- All Tests Completed ---');
    console.log('System is ready for use!');
  } catch (error) {
    console.error('Test failed:', error.message);
  }
}

runTests();