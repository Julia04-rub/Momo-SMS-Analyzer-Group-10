#!/usr/bin/env python3
"""
MoMo SMS REST API Server
A simple HTTP server implementing CRUD operations for SMS transaction data
with Basic Authentication
"""


import json
import base64
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, List, Any, Optional, Tuple
import sys
import os


# Add parent directory to path to import DSA modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'dsa'))
from xml_to_json import SMSParser
from search_compare import SearchComparison




class MoMoAPIHandler(BaseHTTPRequestHandler):
   """HTTP request handler for MoMo SMS API"""
  
   # In-memory data storage (in production, use a proper database)
   transactions_list = []
   transactions_dict = {}
   next_id = 1
  
   # Basic Authentication credentials (in production, use proper auth)
   VALID_CREDENTIALS = {
       'admin': 'password123',
       'user': 'momo2024',
       'testuser': 'test123'
   }
  
   def _authenticate(self) -> bool:
       """Verify Basic Authentication credentials"""
       auth_header = self.headers.get('Authorization')
       if not auth_header or not auth_header.startswith('Basic '):
           return False
      
       try:
           # Decode base64 credentials
           encoded_credentials = auth_header.split(' ')[1]
           decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
           username, password = decoded_credentials.split(':', 1)
          
           # Verify credentials
           return self.VALID_CREDENTIALS.get(username) == password
       except Exception:
           return False
  
   def _send_auth_required(self):
       """Send 401 Unauthorized response"""
       self.send_response(401)
       self.send_header('WWW-Authenticate', 'Basic realm="MoMo API"')
       self.send_header('Content-type', 'application/json')
       self.end_headers()
      
       error_response = {
           'error': 'Authentication required',
           'message': 'Please provide valid Basic Authentication credentials',
           'status_code': 401
       }
       self.wfile.write(json.dumps(error_response, indent=2).encode())
  
   def _send_json_response(self, data: Any, status_code: int = 200):
       """Send JSON response with proper headers"""
       self.send_response(status_code)
       self.send_header('Content-type', 'application/json')
       self.send_header('Access-Control-Allow-Origin', '*')
       self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
       self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
       self.end_headers()
      
       json_data = json.dumps(data, indent=2, ensure_ascii=False)
       self.wfile.write(json_data.encode('utf-8'))
  
   def _parse_request_body(self) -> Optional[Dict[str, Any]]:
       """Parse JSON request body"""
       try:
           content_length = int(self.headers.get('Content-Length', 0))
           if content_length == 0:
               return {}
          
           body = self.rfile.read(content_length)
           return json.loads(body.decode('utf-8'))
       except Exception as e:
           return None
  
   def _validate_transaction_data(self, data: Dict[str, Any], require_id: bool = False) -> Tuple[bool, str]:
       """Validate transaction data"""
       required_fields = ['type', 'amount']
       if require_id:
           required_fields.append('id')
      
       # Check required fields
       for field in required_fields:
           if field not in data:
               return False, f"Missing required field: {field}"
      
       # Validate data types
       if not isinstance(data.get('amount'), (int, float)) or data['amount'] < 0:
           return False, "Amount must be a non-negative number"
      
       if 'fee' in data and (not isinstance(data['fee'], (int, float)) or data['fee'] < 0):
           return False, "Fee must be a non-negative number"
      
       # Validate transaction type
       valid_types = ['received', 'payment', 'transfer', 'deposit', 'airtime', 'business_payment']
       if data['type'] not in valid_types:
           return False, f"Invalid transaction type. Must be one of: {valid_types}"
      
       return True, ""
  
   def do_OPTIONS(self):
       """Handle CORS preflight requests"""
       self.send_response(200)
       self.send_header('Access-Control-Allow-Origin', '*')
       self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
       self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
       self.end_headers()
  
   def do_GET(self):
       """Handle GET requests"""
       if not self._authenticate():
           self._send_auth_required()
           return
      
       parsed_url = urlparse(self.path)
       path_parts = parsed_url.path.strip('/').split('/')
      
       if not path_parts or path_parts[0] == '':
           # Root endpoint - API info
           api_info = {
               'message': 'MoMo SMS Transaction API',
               'version': '1.0',
               'endpoints': {
                   'GET /transactions': 'List all transactions',
                   'GET /transactions/{id}': 'Get specific transaction',
                   'POST /transactions': 'Create new transaction',
                   'PUT /transactions/{id}': 'Update transaction',
                   'DELETE /transactions/{id}': 'Delete transaction',
                   'GET /stats': 'Get API statistics'
               },
               'authentication': 'Basic Auth required',
               'total_transactions': len(self.transactions_list)
           }
           self._send_json_response(api_info)
           return
      
       if path_parts[0] == 'transactions':
           if len(path_parts) == 1:
               # GET /transactions - List all transactions
               self._handle_get_all_transactions(parsed_url)
           elif len(path_parts) == 2:
               # GET /transactions/{id} - Get specific transaction
               try:
                   transaction_id = int(path_parts[1])
                   self._handle_get_transaction(transaction_id)
               except ValueError:
                   self._send_json_response({
                       'error': 'Invalid transaction ID',
                       'message': 'Transaction ID must be a number'
                   }, 400)
           else:
               self._send_json_response({
                   'error': 'Invalid endpoint',
                   'message': 'Endpoint not found'
               }, 404)
      
       elif path_parts[0] == 'stats':
           # GET /stats - API statistics
           self._handle_get_stats()
      
       else:
           self._send_json_response({
               'error': 'Endpoint not found',
               'message': f'Unknown endpoint: /{path_parts[0]}'
           }, 404)
  
   def _handle_get_all_transactions(self, parsed_url):
       """Handle GET /transactions with optional query parameters"""
       query_params = parse_qs(parsed_url.query)
      
       # Apply filters
       filtered_transactions = self.transactions_list.copy()
      
       # Filter by type
       if 'type' in query_params:
           transaction_type = query_params['type'][0]
           filtered_transactions = [tx for tx in filtered_transactions if tx['type'] == transaction_type]
      
       # Filter by amount range
       if 'min_amount' in query_params:
           try:
               min_amount = float(query_params['min_amount'][0])
               filtered_transactions = [tx for tx in filtered_transactions if tx['amount'] >= min_amount]
           except ValueError:
               pass
      
       if 'max_amount' in query_params:
           try:
               max_amount = float(query_params['max_amount'][0])
               filtered_transactions = [tx for tx in filtered_transactions if tx['amount'] <= max_amount]
           except ValueError:
               pass
      
       # Pagination
       page = 1
       per_page = 10
       if 'page' in query_params:
           try:
               page = int(query_params['page'][0])
           except ValueError:
               pass
      
       if 'per_page' in query_params:
           try:
               per_page = min(int(query_params['per_page'][0]), 100)  # Max 100 per page
           except ValueError:
               pass
      
       start_idx = (page - 1) * per_page
       end_idx = start_idx + per_page
       paginated_transactions = filtered_transactions[start_idx:end_idx]
      
       response = {
           'transactions': paginated_transactions,
           'pagination': {
               'page': page,
               'per_page': per_page,
               'total_transactions': len(filtered_transactions),
               'total_pages': (len(filtered_transactions) + per_page - 1) // per_page
           },
           'filters_applied': dict(query_params),
           'timestamp': time.time()
       }
      
       self._send_json_response(response)
  
   def _handle_get_transaction(self, transaction_id: int):
       """Handle GET /transactions/{id}"""
       # Demonstrate DSA comparison
       start_time = time.perf_counter()
      
       # Use dictionary lookup (O(1))
       transaction = self.transactions_dict.get(transaction_id)
      
       lookup_time = time.perf_counter() - start_time
      
       if transaction:
           response = {
               'transaction': transaction,
               'search_performance': {
                   'algorithm': 'dictionary_lookup',
                   'time_complexity': 'O(1)',
                   'search_time_seconds': lookup_time,
                   'dataset_size': len(self.transactions_list)
               }
           }
           self._send_json_response(response)
       else:
           self._send_json_response({
               'error': 'Transaction not found',
               'message': f'No transaction with ID {transaction_id}',
               'search_time_seconds': lookup_time
           }, 404)
  
   def _handle_get_stats(self):
       """Handle GET /stats"""
       if not self.transactions_list:
           stats = {
               'total_transactions': 0,
               'message': 'No transaction data available'
           }
       else:
           # Calculate statistics
           types = {}
           total_amount = 0
           total_fees = 0
           amounts = []
          
           for tx in self.transactions_list:
               tx_type = tx.get('type', 'unknown')
               types[tx_type] = types.get(tx_type, 0) + 1
               amount = tx.get('amount', 0)
               total_amount += amount
               total_fees += tx.get('fee', 0)
               amounts.append(amount)
          
           amounts.sort()
           n = len(amounts)
           median = amounts[n//2] if n % 2 == 1 else (amounts[n//2-1] + amounts[n//2]) / 2
          
           stats = {
               'total_transactions': len(self.transactions_list),
               'transaction_types': types,
               'financial_summary': {
                   'total_amount': total_amount,
                   'total_fees': total_fees,
                   'average_amount': total_amount / len(self.transactions_list),
                   'median_amount': median,
                   'min_amount': min(amounts),
                   'max_amount': max(amounts),
                   'currency': 'RWF'
               },
               'data_structures': {
                   'list_size': len(self.transactions_list),
                   'dict_size': len(self.transactions_dict),
                   'next_available_id': self.next_id
               }
           }
      
       self._send_json_response(stats)
  
   def do_POST(self):
       """Handle POST requests"""
       if not self._authenticate():
           self._send_auth_required()
           return
      
       parsed_url = urlparse(self.path)
       path_parts = parsed_url.path.strip('/').split('/')
      
       if path_parts[0] == 'transactions' and len(path_parts) == 1:
           self._handle_create_transaction()
       else:
           self._send_json_response({
               'error': 'Invalid endpoint for POST',
               'message': 'Only POST /transactions is supported'
           }, 404)
  
   def _handle_create_transaction(self):
       """Handle POST /transactions"""
       data = self._parse_request_body()
       if data is None:
           self._send_json_response({
               'error': 'Invalid JSON',
               'message': 'Request body must contain valid JSON'
           }, 400)
           return
      
       # Validate data
       is_valid, error_msg = self._validate_transaction_data(data)
       if not is_valid:
           self._send_json_response({
               'error': 'Validation error',
               'message': error_msg
           }, 400)
           return
      
       # Create new transaction
       new_transaction = {
           'id': self.next_id,
           'type': data['type'],
           'amount': float(data['amount']),
           'fee': float(data.get('fee', 0.0)),
           'currency': data.get('currency', 'RWF'),
           'sender': data.get('sender', ''),
           'receiver': data.get('receiver', ''),
           'sender_phone': data.get('sender_phone', ''),
           'receiver_phone': data.get('receiver_phone', ''),
           'balance': float(data.get('balance', 0.0)),
           'transaction_id': data.get('transaction_id', f'TXN_{self.next_id}'),
           'status': data.get('status', 'completed'),
           'message': data.get('message', ''),
           'timestamp': time.time(),
           'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
       }
      
       # Add to data structures
       self.transactions_list.append(new_transaction)
       self.transactions_dict[self.next_id] = new_transaction
       self.next_id += 1
      
       self._send_json_response({
           'message': 'Transaction created successfully',
           'transaction': new_transaction
       }, 201)
  
   def do_PUT(self):
       """Handle PUT requests"""
       if not self._authenticate():
           self._send_auth_required()
           return
      
       parsed_url = urlparse(self.path)
       path_parts = parsed_url.path.strip('/').split('/')
      
       if path_parts[0] == 'transactions' and len(path_parts) == 2:
           try:
               transaction_id = int(path_parts[1])
               self._handle_update_transaction(transaction_id)
           except ValueError:
               self._send_json_response({
                   'error': 'Invalid transaction ID',
                   'message': 'Transaction ID must be a number'
               }, 400)
       else:
           self._send_json_response({
               'error': 'Invalid endpoint for PUT',
               'message': 'Use PUT /transactions/{id}'
           }, 404)
  
   def _handle_update_transaction(self, transaction_id: int):
       """Handle PUT /transactions/{id}"""
       # Check if transaction exists
       if transaction_id not in self.transactions_dict:
           self._send_json_response({
               'error': 'Transaction not found',
               'message': f'No transaction with ID {transaction_id}'
           }, 404)
           return
      
       data = self._parse_request_body()
       if data is None:
           self._send_json_response({
               'error': 'Invalid JSON',
               'message': 'Request body must contain valid JSON'
           }, 400)
           return
      
       # Validate data (ID not required for updates)
       is_valid, error_msg = self._validate_transaction_data(data, require_id=False)
       if not is_valid:
           self._send_json_response({
               'error': 'Validation error',
               'message': error_msg
           }, 400)
           return
      
       # Update transaction
       transaction = self.transactions_dict[transaction_id]
       updatable_fields = ['type', 'amount', 'fee', 'sender', 'receiver', 'sender_phone',
                          'receiver_phone', 'balance', 'status', 'message']
      
       for field in updatable_fields:
           if field in data:
               transaction[field] = data[field]
      
       transaction['updated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
      
       # Update in list as well
       for i, tx in enumerate(self.transactions_list):
           if tx['id'] == transaction_id:
               self.transactions_list[i] = transaction
               break
      
       self._send_json_response({
           'message': 'Transaction updated successfully',
           'transaction': transaction
       })
  
   def do_DELETE(self):
       """Handle DELETE requests"""
       if not self._authenticate():
           self._send_auth_required()
           return
      
       parsed_url = urlparse(self.path)
       path_parts = parsed_url.path.strip('/').split('/')
      
       if path_parts[0] == 'transactions' and len(path_parts) == 2:
           try:
               transaction_id = int(path_parts[1])
               self._handle_delete_transaction(transaction_id)
           except ValueError:
               self._send_json_response({
                   'error': 'Invalid transaction ID',
                   'message': 'Transaction ID must be a number'
               }, 400)
       else:
           self._send_json_response({
               'error': 'Invalid endpoint for DELETE',
               'message': 'Use DELETE /transactions/{id}'
           }, 404)
  
   def _handle_delete_transaction(self, transaction_id: int):
       """Handle DELETE /transactions/{id}"""
       # Check if transaction exists
       if transaction_id not in self.transactions_dict:
           self._send_json_response({
               'error': 'Transaction not found',
               'message': f'No transaction with ID {transaction_id}'
           }, 404)
           return
      
       # Remove from dictionary
       deleted_transaction = self.transactions_dict.pop(transaction_id)
      
       # Remove from list
       self.transactions_list = [tx for tx in self.transactions_list if tx['id'] != transaction_id]
      
       self._send_json_response({
           'message': 'Transaction deleted successfully',
           'deleted_transaction': deleted_transaction,
           'remaining_transactions': len(self.transactions_list)
       })
  
   def log_message(self, format, *args):
       """Override to provide custom logging"""
       timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
       print(f"[{timestamp}] {self.address_string()} - {format % args}")




class MoMoAPIServer:
   """MoMo SMS API Server wrapper"""
  
   def __init__(self, host='localhost', port=8000):
       self.host = host
       self.port = port
       self.server = None
  
   def load_data_from_xml(self, xml_file: str = '../modified_sms_v2.xml'):
       """Load transaction data from XML file"""
       # If relative path, make it relative to this script's directory
       if not os.path.isabs(xml_file):
           script_dir = os.path.dirname(os.path.abspath(__file__))
           xml_file = os.path.join(script_dir, xml_file)
      
       print(f"Loading data from {xml_file}...")
       if not os.path.exists(xml_file):
           print(f"File not found: {xml_file}")
           return False
          
       parser = SMSParser(xml_file)
       transactions = parser.parse_xml()
      
       if transactions:
           # Initialize class variables
           MoMoAPIHandler.transactions_list = transactions
           MoMoAPIHandler.transactions_dict = {tx['id']: tx for tx in transactions}
           MoMoAPIHandler.next_id = max(tx['id'] for tx in transactions) + 1
          
           print(f"Loaded {len(transactions)} transactions")
           print(f"Transaction types: {set(tx['type'] for tx in transactions)}")
           return True
       else:
           print("No transactions loaded. Starting with empty dataset.")
           return False
  
   def start(self):
       """Start the API server"""
       try:
           self.server = HTTPServer((self.host, self.port), MoMoAPIHandler)
           print(f"\n=== MoMo SMS API Server Started ===")
           print(f"Server: http://{self.host}:{self.port}")
           print(f"Endpoints:")
           print(f"  GET    /                     - API information")
           print(f"  GET    /transactions         - List all transactions")
           print(f"  GET    /transactions/{{id}}   - Get specific transaction")
           print(f"  POST   /transactions         - Create new transaction")
           print(f"  PUT    /transactions/{{id}}   - Update transaction")
           print(f"  DELETE /transactions/{{id}}   - Delete transaction")
           print(f"  GET    /stats               - API statistics")
           print(f"\nAuthentication: Basic Auth")
           print(f"Valid credentials:")
           for username, password in MoMoAPIHandler.VALID_CREDENTIALS.items():
               print(f"  {username}:{password}")
           print(f"\nPress Ctrl+C to stop the server")
           print(f"========================================\n")
          
           self.server.serve_forever()
          
       except KeyboardInterrupt:
           print("\n\nShutting down server...")
           if self.server:
               self.server.shutdown()
               self.server.server_close()
           print("Server stopped.")
       except Exception as e:
           print(f"Error starting server: {e}")




def main():
   """Main function to start the API server"""
   import argparse
  
   parser = argparse.ArgumentParser(description='MoMo SMS REST API Server')
   parser.add_argument('--host', default='localhost', help='Server host (default: localhost)')
   parser.add_argument('--port', type=int, default=8000, help='Server port (default: 8000)')
   parser.add_argument('--xml-file', default='../modified_sms_v2.xml', help='XML data file path')
  
   args = parser.parse_args()
  
   # Create and configure server
   api_server = MoMoAPIServer(args.host, args.port)
  
   # Load data
   api_server.load_data_from_xml(args.xml_file)
  
   # Start server
   api_server.start()




if __name__ == "__main__":
   main()


