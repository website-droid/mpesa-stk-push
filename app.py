from flask import Flask, request, jsonify, render_template_string, session
import requests
import secrets
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Paynecta Credentials
PAYNECTA_API_KEY = os.environ.get('PAYNECTA_API_KEY', 'hmp_c9Hxlv0cIze7jbNqOkl4knNNnDmOHrtvv6Om89pk')
PAYNECTA_USER_EMAIL = os.environ.get('PAYNECTA_USER_EMAIL', 'muhsinswaleh69@gmail.com')
PAYNECTA_BASE_URL = 'https://paynecta.co.ke/api/v1'

# HTML Template - Same beautiful design
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Registration - Pay 50 KES</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 500px;
            width: 100%;
        }
        h1 { color: #333; margin-bottom: 10px; }
        .price { font-size: 48px; color: #667eea; font-weight: bold; margin: 20px 0; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; color: #555; font-weight: 500; }
        input, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input:focus, select:focus { outline: none; border-color: #667eea; }
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover { transform: translateY(-2px); }
        .message {
            margin-top: 20px;
            padding: 15px;
            border-radius: 8px;
            display: none;
        }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .loading { display: none; text-align: center; margin-top: 20px; }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .debug-info { 
            margin-top: 20px; 
            padding: 10px; 
            background: #f8f9fa; 
            border-radius: 8px; 
            font-size: 12px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎓 Student Registration</h1>
        <p>Pay 50 KES to register a new student</p>
        <div class="price">KES 50</div>
        
        <form id="paymentForm">
            <div class="form-group">
                <label>Student Full Name *</label>
                <input type="text" id="studentName" required placeholder="e.g., John Otieno">
            </div>
            <div class="form-group">
                <label>Parent/Guardian Phone *</label>
                <input type="tel" id="phone" required placeholder="254700000000" pattern="254[0-9]{9}">
                <small>Format: 254700000000 (without +)</small>
            </div>
            <div class="form-group">
                <label>Payment Method *</label>
                <select id="paymentMethod" required>
                    <option value="">Select payment method</option>
                    <option value="mpesa">M-Pesa</option>
                    <option value="card">Card</option>
                </select>
            </div>
            <button type="submit">Pay 50 KES & Register</button>
        </form>
        
        <div id="message" class="message"></div>
        <div id="loading" class="loading">
            <div class="spinner"></div>
            <p style="margin-top: 10px;">Processing payment...</p>
        </div>
        <div id="debugInfo" class="debug-info"></div>
    </div>

    <script>
        document.getElementById('paymentForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const studentName = document.getElementById('studentName').value;
            const phone = document.getElementById('phone').value;
            const paymentMethod = document.getElementById('paymentMethod').value;
            
            document.getElementById('loading').style.display = 'block';
            document.getElementById('message').style.display = 'none';
            
            try {
                const response = await fetch('/api/register-student', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        student_name: studentName,
                        phone: phone,
                        amount: 50,
                        payment_method: paymentMethod
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showMessage('✅ ' + result.message, 'success');
                    document.getElementById('paymentForm').reset();
                    if (result.data && result.data.payment_link) {
                        showMessage('📱 Payment link: ' + result.data.payment_link, 'success');
                    }
                } else {
                    showMessage('❌ ' + result.message, 'error');
                }
            } catch (error) {
                showMessage('❌ Network error. Please try again.', 'error');
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        });
        
        function showMessage(msg, type) {
            const messageDiv = document.getElementById('message');
            messageDiv.textContent = msg;
            messageDiv.className = 'message ' + type;
            messageDiv.style.display = 'block';
            setTimeout(() => {
                messageDiv.style.display = 'none';
            }, 8000);
        }
        
        function showDebug(data) {
            const debugDiv = document.getElementById('debugInfo');
            debugDiv.textContent = JSON.stringify(data, null, 2);
            debugDiv.style.display = 'block';
        }
    </script>
</body>
</html>
'''

def verify_paynecta_auth():
    """Verify API credentials with Paynecta"""
    try:
        response = requests.get(
            f'{PAYNECTA_BASE_URL}/auth/verify',
            headers={
                'X-API-Key': PAYNECTA_API_KEY,
                'X-User-Email': PAYNECTA_USER_EMAIL
            },
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {'success': False, 'message': str(e)}

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/register-student', methods=['POST'])
def register_student():
    """Process student registration and payment"""
    try:
        data = request.json
        student_name = data.get('student_name')
        phone = data.get('phone')
        amount = data.get('amount', 50)
        payment_method = data.get('payment_method')
        
        # Validate input
        if not all([student_name, phone, payment_method]):
            return jsonify({
                'success': False,
                'message': 'All fields are required'
            }), 400
        
        # Try different possible Paynecta endpoints
        
        # FIRST: Try to get payment link/code info
        endpoints_to_try = [
            '/payments',
            '/payment',
            '/mpesa/stkpush',
            '/mpesa/initiate',
            '/transaction/initiate'
        ]
        
        payment_result = None
        working_endpoint = None
        
        for endpoint in endpoints_to_try:
            try:
                test_response = requests.post(
                    f'{PAYNECTA_BASE_URL}{endpoint}',
                    headers={
                        'X-API-Key': PAYNECTA_API_KEY,
                        'X-User-Email': PAYNECTA_USER_EMAIL,
                        'Content-Type': 'application/json'
                    },
                    json={
                        'amount': amount,
                        'phone_number': phone,
                        'reference': f'STU{datetime.now().strftime("%Y%m%d%H%M%S")}',
                        'description': f'Student registration fee for {student_name}'
                    },
                    timeout=10
                )
                
                if test_response.status_code != 404:
                    payment_result = test_response.json()
                    working_endpoint = endpoint
                    break
            except:
                continue
        
        # If no endpoint worked, return helpful error
        if not payment_result:
            return jsonify({
                'success': False,
                'message': 'Paynecta API endpoint not found. Please check your Paynecta account for the correct API documentation.',
                'debug': 'The API endpoints we tried did not work. You may need to get the correct endpoint from Paynecta support.'
            }), 500
        
        if payment_result.get('success'):
            print(f"✅ Student Registered: {student_name} | Phone: {phone}")
            
            return jsonify({
                'success': True,
                'message': f'Student {student_name} registered successfully! Payment of KES {amount} has been initiated.',
                'data': payment_result.get('data')
            })
        else:
            return jsonify({
                'success': False,
                'message': payment_result.get('message', 'Payment failed. Please try again.')
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint - visit this first to test your API key"""
    auth_status = verify_paynecta_auth()
    return jsonify({
        'status': 'healthy',
        'paynecta_auth': auth_status.get('success', False),
        'auth_message': auth_status.get('message', ''),
        'your_api_key': PAYNECTA_API_KEY[:20] + '...' if PAYNECTA_API_KEY else 'Not set',
        'your_email': PAYNECTA_USER_EMAIL,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
