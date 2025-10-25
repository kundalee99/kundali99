from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from datetime import datetime, timedelta
import os
import random
import base64
from io import BytesIO
import tempfile
import requests
import time

# CORRECT CASHFREE IMPORTS FOR v4.3.10
try:
    from cashfree_pg.models.create_order_request import CreateOrderRequest
    from cashfree_pg.api_client import Cashfree
    from cashfree_pg.models.customer_details import CustomerDetails
    from cashfree_pg.models.order_meta import OrderMeta
    CASHFREE_AVAILABLE = True
    print("✅ Cashfree SDK v4.3.10 imported successfully")
except ImportError as e:
    print(f"❌ Cashfree import error: {e}")
    CASHFREE_AVAILABLE = False
    Cashfree = None

import hmac
import hashlib

# Try different PDF libraries
try:
    from weasyprint import HTML
    PDF_ENGINE = 'weasyprint'
    print("✅ Using WeasyPrint for PDF generation")
except ImportError:
    try:
        import pdfkit
        PDF_ENGINE = 'pdfkit'
        print("✅ Using pdfkit for PDF generation")
    except ImportError:
        try:
            from xhtml2pdf import pisa
            PDF_ENGINE = 'xhtml2pdf'
            print("✅ Using xhtml2pdf for PDF generation")
        except ImportError:
            PDF_ENGINE = None
            print("❌ No PDF library available - using HTML fallback")

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

# ENHANCED CORS CONFIGURATION - FIXED
CORS(app, origins=[
    "https://kundali99.com",
    "https://www.kundali99.com", 
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://kundali99.vercel.app"  # Add if using Vercel
], 
supports_credentials=True,
methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
allow_headers=["Content-Type", "Authorization", "X-Requested-With"])

# Add CORS headers manually for all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'https://kundali99.com')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Real Lord Ganesha image URL
GANESHA_IMAGE_URL = "https://i.ibb.co/tgvs8sc/ganesha.jpg"

# Cashfree Configuration
CASHFREE_APP_ID = os.environ.get('CASHFREE_APP_ID')
CASHFREE_SECRET_KEY = os.environ.get('CASHFREE_SECRET_KEY')
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
CASHFREE_ENVIRONMENT = os.environ.get('CASHFREE_ENVIRONMENT', 'PRODUCTION')  # or 'SANDBOX'
X_API_VERSION = '2023-08-01'

# Initialize Cashfree
if CASHFREE_AVAILABLE:
    try:
        Cashfree.XClientId = CASHFREE_APP_ID
        Cashfree.XClientSecret = CASHFREE_SECRET_KEY

        if CASHFREE_ENVIRONMENT == 'PRODUCTION':
            Cashfree.XEnvironment = Cashfree.XProduction
        else:
            Cashfree.XEnvironment = Cashfree.XSandbox

        print(f"✅ Cashfree configured - Environment: {CASHFREE_ENVIRONMENT}")
    except Exception as e:
        print(f"❌ Cashfree configuration error: {e}")
        CASHFREE_AVAILABLE = False
else:
    print("⚠️ Cashfree features disabled")

# ... [KEEP ALL YOUR EXISTING CLASSES AND FUNCTIONS THE SAME] ...
# AdvancedPredictionEngine class and all its methods remain exactly the same
# get_language_name, get_gemstone_recommendation, translate_text_simple, etc. remain the same

@app.route('/api/health', methods=['GET', 'OPTIONS'])
@cross_origin()
def health_check():
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'cashfree_available': CASHFREE_AVAILABLE,
        'pdf_engine': PDF_ENGINE
    })

@app.route('/api/generate-predictions', methods=['POST', 'OPTIONS'])
@cross_origin()
def generate_predictions():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.get_json()
        print(f"📥 Received prediction request: {data}")

        # Validate required fields
        required_fields = ['name', 'birth_date', 'birth_time', 'birth_place']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400

        # Validate birth date format (DDMMYYYY)
        birth_date = data['birth_date']
        if len(birth_date) != 8 or not birth_date.isdigit():
            return jsonify({
                'status': 'error',
                'message': 'Birth date must be in DDMMYYYY format'
            }), 400

        # Validate birth time format (HHMM)
        birth_time = data['birth_time']
        if len(birth_time) != 4 or not birth_time.isdigit():
            return jsonify({
                'status': 'error',
                'message': 'Birth time must be in HHMM format (24-hour)'
            }), 400

        # Get language preference
        language = data.get('language', 'en')
        print(f"🌐 Language preference: {language}")

        # Generate predictions
        predictions_data = prediction_engine.generate_predictions(data)

        # Translate content if needed
        if language != 'en':
            print(f"🔄 Translating predictions to {language}...")
            predictions_data['predictions'] = translate_predictions_content(
                predictions_data['predictions'], language
            )

        # Add gemstone recommendation
        zodiac_sign = predictions_data['chart_info']['zodiac_sign']
        gemstone = get_gemstone_recommendation(zodiac_sign)
        predictions_data['gemstone_recommendation'] = gemstone

        # Add language info
        predictions_data['language'] = language
        predictions_data['language_name'] = get_language_name(language)

        print(f"✅ Predictions generated successfully for {data['name']}")
        return jsonify({
            'status': 'success',
            'data': predictions_data
        })

    except Exception as e:
        print(f"❌ Prediction generation error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to generate predictions: {str(e)}'
        }), 500

# ADD MISSING CREATE-ORDER ENDPOINT
@app.route('/api/create-order', methods=['POST', 'OPTIONS'])
@cross_origin()
def create_order():
    if request.method == 'OPTIONS':
        return '', 200
    """Create Cashfree payment order - FIXED ENDPOINT"""
    try:
        if not CASHFREE_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Payment service temporarily unavailable'
            }), 503

        data = request.get_json()
        print(f"💳 Creating payment order for: {data}")

        # Validate required fields
        required_fields = ['order_id', 'order_amount', 'customer_name', 'customer_email', 'customer_phone']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400

        # Create order request
        customer_details = CustomerDetails(
            customer_id=data.get('customer_id', 'customer_' + str(int(time.time()))),
            customer_name=data['customer_name'],
            customer_email=data['customer_email'],
            customer_phone=data['customer_phone']
        )

        order_meta = OrderMeta(
            return_url=data.get('return_url', 'https://kundali99.com/payment-success'),
            notify_url=data.get('notify_url', f'{request.host_url}api/payment-webhook')
        )

        order_request = CreateOrderRequest(
            order_id=data['order_id'],
            order_amount=data['order_amount'],
            order_currency='INR',
            customer_details=customer_details,
            order_meta=order_meta
        )

        # Create order
        api_instance = Cashfree.PGCreateOrderApi()
        api_response = api_instance.p_g_create_order(
            x_client_id=CASHFREE_APP_ID,
            x_client_secret=CASHFREE_SECRET_KEY,
            x_api_version=X_API_VERSION,
            create_order_request=order_request
        )

        print(f"✅ Payment order created: {api_response}")

        return jsonify({
            'success': True,
            'payment_session_id': api_response.payment_session_id,
            'order_id': api_response.order_id,
            'order_amount': api_response.order_amount
        })

    except Exception as e:
        print(f"❌ Payment order creation error: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to create payment order: {str(e)}'
        }), 500

@app.route('/api/generate-pdf-report', methods=['POST', 'OPTIONS'])
@cross_origin()
def generate_pdf_report():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.get_json()
        print(f"📥 Received PDF generation request for: {data.get('name', 'Unknown')}")

        # Validate required fields
        required_fields = ['name', 'birth_date', 'predictions']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400

        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            pdf_path = temp_file.name

        # Generate PDF
        html_content = create_pdf_html(data)
        success = generate_pdf(html_content, pdf_path)

        if not success:
            return jsonify({
                'status': 'error',
                'message': 'PDF generation failed - no PDF engine available'
            }), 500

        # Return PDF as base64
        with open(pdf_path, 'rb') as f:
            pdf_data = base64.b64encode(f.read()).decode('utf-8')

        # Clean up
        os.unlink(pdf_path)

        print(f"✅ PDF report generated successfully for {data['name']}")
        return jsonify({
            'status': 'success',
            'pdf_data': pdf_data,
            'filename': f"ganesha_predictions_{data['name'].replace(' ', '_')}.pdf"
        })

    except Exception as e:
        print(f"❌ PDF generation error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to generate PDF: {str(e)}'
        }), 500

@app.route('/api/payment-webhook', methods=['POST', 'OPTIONS'])
@cross_origin()
def payment_webhook():
    if request.method == 'OPTIONS':
        return '', 200
    """Handle Cashfree payment webhook"""
    try:
        data = request.get_json()
        print(f"🔄 Received payment webhook: {data}")

        # Verify signature
        signature = request.headers.get('x-webhook-signature')
        if not verify_webhook_signature(data, signature):
            print("❌ Invalid webhook signature")
            return jsonify({'status': 'error', 'message': 'Invalid signature'}), 401

        # Process webhook data
        order_id = data.get('orderId')
        order_status = data.get('orderStatus')

        print(f"💰 Payment update - Order: {order_id}, Status: {order_status}")

        # Here you would update your database with payment status
        # For now, just log it
        if order_status == 'PAID':
            print(f"✅ Payment successful for order: {order_id}")
        elif order_status in ['FAILED', 'CANCELLED']:
            print(f"❌ Payment failed for order: {order_id}")

        return jsonify({'status': 'success'})

    except Exception as e:
        print(f"❌ Webhook processing error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/get-payment-status/<order_id>', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_payment_status(order_id):
    if request.method == 'OPTIONS':
        return '', 200
    """Get payment status for an order - FIXED to GET method"""
    try:
        if not CASHFREE_AVAILABLE:
            return jsonify({
                'status': 'error',
                'message': 'Payment service unavailable'
            }), 503

        api_instance = Cashfree.PGFetchOrderApi()
        api_response = api_instance.p_g_fetch_order(
            x_client_id=CASHFREE_APP_ID,
            x_client_secret=CASHFREE_SECRET_KEY,
            x_api_version=X_API_VERSION,
            order_id=order_id
        )

        return jsonify({
            'status': 'success',
            'payment_verified': api_response.order_status == 'PAID',
            'order_status': api_response.order_status,
            'order_amount': api_response.order_amount,
            'payment_status': api_response.payment_status
        })

    except Exception as e:
        print(f"❌ Payment status check error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to get payment status: {str(e)}'
        }), 500

# ADD THIS MISSING TEST ENDPOINT
@app.route('/api/create-payment-order', methods=['POST', 'OPTIONS'])
@cross_origin()
def create_payment_order_test():
    if request.method == 'OPTIONS':
        return '', 200
    """Test endpoint - returns success for testing"""
    return jsonify({
        'success': True,
        'message': 'Test endpoint working',
        'test_mode': True
    })

def verify_webhook_signature(data, signature):
    """Verify Cashfree webhook signature"""
    try:
        # Sort the data and create signature string
        sorted_data = dict(sorted(data.items()))
        signature_data = "".join([str(value) for value in sorted_data.values()])

        # Compute HMAC
        computed_signature = hmac.new(
            CASHFREE_SECRET_KEY.encode('utf-8'),
            signature_data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return computed_signature == signature
    except Exception as e:
        print(f"Signature verification error: {e}")
        return False

# Initialize prediction engine
prediction_engine = AdvancedPredictionEngine()

# Railway.app specific configuration
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Starting Lord Ganesha Astrology API on port {port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"💰 Cashfree available: {CASHFREE_AVAILABLE}")
    print(f"📄 PDF engine: {PDF_ENGINE}")
    
    app.run(host='0.0.0.0', port=port, debug=False)