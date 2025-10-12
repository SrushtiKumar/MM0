// Frontend API Test Script
// Run this in the browser console at http://localhost:8080

console.log('🔍 Testing Frontend API Connection...');

const API_BASE_URL = 'http://localhost:8000/api';

async function testAPI() {
    console.log('Testing API Base URL:', API_BASE_URL);
    
    // Test 1: Health Check
    console.log('\n📡 Test 1: Health Check');
    try {
        const healthResponse = await fetch(`${API_BASE_URL}/health`);
        console.log('Health response status:', healthResponse.status);
        console.log('Health response headers:', healthResponse.headers);
        
        if (healthResponse.ok) {
            const healthData = await healthResponse.json();
            console.log('✅ Health Check SUCCESS:', healthData);
        } else {
            console.log('❌ Health Check FAILED:', healthResponse.statusText);
        }
    } catch (error) {
        console.log('❌ Health Check ERROR:', error);
        console.log('Error details:', {
            name: error.name,
            message: error.message,
            stack: error.stack
        });
    }

    // Test 2: Supported Formats
    console.log('\n📡 Test 2: Supported Formats');
    try {
        const formatsResponse = await fetch(`${API_BASE_URL}/supported-formats`);
        console.log('Formats response status:', formatsResponse.status);
        
        if (formatsResponse.ok) {
            const formatsData = await formatsResponse.json();
            console.log('✅ Supported Formats SUCCESS:', formatsData);
        } else {
            console.log('❌ Supported Formats FAILED:', formatsResponse.statusText);
        }
    } catch (error) {
        console.log('❌ Supported Formats ERROR:', error);
    }

    // Test 3: CORS Preflight
    console.log('\n📡 Test 3: CORS Test');
    try {
        const corsResponse = await fetch(`${API_BASE_URL}/health`, {
            method: 'GET',
            mode: 'cors',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        console.log('CORS response status:', corsResponse.status);
        if (corsResponse.ok) {
            console.log('✅ CORS TEST SUCCESS');
        }
    } catch (error) {
        console.log('❌ CORS TEST ERROR:', error);
    }

    console.log('\n🏁 API Test Complete');
}

// Run the test
testAPI();