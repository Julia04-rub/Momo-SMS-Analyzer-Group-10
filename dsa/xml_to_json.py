#!/usr/bin/env python3
"""
XML to JSON Parser for MoMo SMS Data
Parses modified_sms_v2.xml and converts SMS records to JSON format
"""


import xml.etree.ElementTree as ET
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional




class SMSParser:
   """Parser for MoMo SMS XML data"""
  
   def __init__(self, xml_file: str):
       self.xml_file = xml_file
       self.transactions = []
       self.transaction_counter = 1
  
   def parse_xml(self) -> List[Dict[str, Any]]:
       """Parse XML file and convert to JSON-like dictionaries"""
       try:
           tree = ET.parse(self.xml_file)
           root = tree.getroot()
          
           for sms in root.findall('sms'):
               transaction = self._parse_sms_record(sms)
               if transaction:
                   self.transactions.append(transaction)
                  
           print(f"Parsed {len(self.transactions)} SMS transactions")
           return self.transactions
          
       except ET.ParseError as e:
           print(f"Error parsing XML: {e}")
           return []
       except FileNotFoundError:
           print(f"File not found: {self.xml_file}")
           return []
  
   def _parse_sms_record(self, sms_element) -> Optional[Dict[str, Any]]:
       """Parse individual SMS record into transaction dictionary"""
       try:
           # Extract basic SMS attributes
           body = sms_element.get('body', '')
           date = sms_element.get('date', '')
           readable_date = sms_element.get('readable_date', '')
          
           # Parse transaction details from SMS body
           transaction_data = self._extract_transaction_details(body)
           if not transaction_data:
               return None
          
           # Convert timestamp
           timestamp = self._convert_timestamp(date, readable_date)
          
           # Create transaction record
           transaction = {
               'id': self.transaction_counter,
               'transaction_id': transaction_data.get('transaction_id', f"TXN_{self.transaction_counter}"),
               'type': transaction_data.get('type', 'unknown'),
               'amount': transaction_data.get('amount', 0.0),
               'fee': transaction_data.get('fee', 0.0),
               'currency': 'RWF',
               'sender': transaction_data.get('sender', ''),
               'receiver': transaction_data.get('receiver', ''),
               'sender_phone': transaction_data.get('sender_phone', ''),
               'receiver_phone': transaction_data.get('receiver_phone', ''),
               'balance': transaction_data.get('balance', 0.0),
               'timestamp': timestamp,
               'readable_date': readable_date,
               'message': body[:200] + '...' if len(body) > 200 else body,
               'status': 'completed',
               'created_at': datetime.now().isoformat()
           }
          
           self.transaction_counter += 1
           return transaction
          
       except Exception as e:
           print(f"Error parsing SMS record: {e}")
           return None
  
   def _extract_transaction_details(self, body: str) -> Optional[Dict[str, Any]]:
       """Extract transaction details from SMS body using regex patterns"""
       try:
           transaction_data = {}
          
           # Pattern 1: Money received
           received_pattern = r"You have received (\d+(?:,\d+)*) RWF from (.+?) \(\*+(\d+)\) on your mobile money account.*?Your new balance:(\d+(?:,\d+)*) RWF.*?Financial Transaction Id: (\d+)"
           received_match = re.search(received_pattern, body)
          
           if received_match:
               transaction_data.update({
                   'type': 'received',
                   'amount': float(received_match.group(1).replace(',', '')),
                   'sender': received_match.group(2).strip(),
                   'sender_phone': received_match.group(3),
                   'receiver': 'User Account',
                   'balance': float(received_match.group(4).replace(',', '')),
                   'transaction_id': received_match.group(5),
                   'fee': 0.0
               })
               return transaction_data
          
           # Pattern 2: Payment/Transfer sent
           payment_pattern = r"TxId: (\d+).*?Your payment of ([\d,]+) RWF to (.+?) (\d+) has been completed.*?Your new balance: ([\d,]+) RWF.*?Fee was (\d+) RWF"
           payment_match = re.search(payment_pattern, body)
          
           if payment_match:
               transaction_data.update({
                   'type': 'payment',
                   'transaction_id': payment_match.group(1),
                   'amount': float(payment_match.group(2).replace(',', '')),
                   'receiver': payment_match.group(3).strip(),
                   'sender': 'User Account',
                   'balance': float(payment_match.group(5).replace(',', '')),
                   'fee': float(payment_match.group(6))
               })
               return transaction_data
          
           # Pattern 3: Money transfer
           transfer_pattern = r"\*165\*S\*([\d,]+) RWF transferred to (.+?) \((\d+)\) from (\d+) at.*?Fee was: (\d+) RWF.*?New balance: ([\d,]+) RWF"
           transfer_match = re.search(transfer_pattern, body)
          
           if transfer_match:
               transaction_data.update({
                   'type': 'transfer',
                   'amount': float(transfer_match.group(1).replace(',', '')),
                   'receiver': transfer_match.group(2).strip(),
                   'receiver_phone': transfer_match.group(3),
                   'sender': 'User Account',
                   'fee': float(transfer_match.group(5)),
                   'balance': float(transfer_match.group(6).replace(',', ''))
               })
               return transaction_data
          
           # Pattern 4: Bank deposit
           deposit_pattern = r"\*113\*R\*A bank deposit of ([\d,]+) RWF has been added.*?Your NEW BALANCE :([\d,]+) RWF"
           deposit_match = re.search(deposit_pattern, body)
          
           if deposit_match:
               transaction_data.update({
                   'type': 'deposit',
                   'amount': float(deposit_match.group(1).replace(',', '')),
                   'sender': 'Bank Account',
                   'receiver': 'User Account',
                   'balance': float(deposit_match.group(2).replace(',', '')),
                   'fee': 0.0
               })
               return transaction_data
          
           # Pattern 5: Airtime purchase
           airtime_pattern = r"\*162\*TxId:(\d+)\*S\*Your payment of (\d+) RWF to Airtime.*?Fee was (\d+) RWF.*?Your new balance: ([\d,]+) RWF"
           airtime_match = re.search(airtime_pattern, body)
          
           if airtime_match:
               transaction_data.update({
                   'type': 'airtime',
                   'transaction_id': airtime_match.group(1),
                   'amount': float(airtime_match.group(2)),
                   'receiver': 'Airtime Service',
                   'sender': 'User Account',
                   'fee': float(airtime_match.group(3)),
                   'balance': float(airtime_match.group(4).replace(',', ''))
               })
               return transaction_data
          
           # Pattern 6: Business payment
           business_pattern = r"\*164\*S\*.*?transaction of ([\d,]+) RWF by (.+?) on your MOMO account.*?Your new balance:([\d,]+) RWF.*?Fee was (\d+) RWF.*?Financial Transaction Id: (\d+)"
           business_match = re.search(business_pattern, body)
          
           if business_match:
               transaction_data.update({
                   'type': 'business_payment',
                   'amount': float(business_match.group(1).replace(',', '')),
                   'receiver': business_match.group(2).strip(),
                   'sender': 'User Account',
                   'balance': float(business_match.group(3).replace(',', '')),
                   'fee': float(business_match.group(4)),
                   'transaction_id': business_match.group(5)
               })
               return transaction_data
          
           return None
          
       except Exception as e:
           print(f"Error extracting transaction details: {e}")
           return None
  
   def _convert_timestamp(self, date_ms: str, readable_date: str) -> str:
       """Convert timestamp to ISO format"""
       try:
           if date_ms:
               timestamp = int(date_ms) / 1000
               return datetime.fromtimestamp(timestamp).isoformat()
           else:
               return datetime.now().isoformat()
       except (ValueError, TypeError):
           return datetime.now().isoformat()
  
   def save_to_json(self, output_file: str = 'transactions.json') -> None:
       """Save parsed transactions to JSON file"""
       try:
           with open(output_file, 'w', encoding='utf-8') as f:
               json.dump(self.transactions, f, indent=2, ensure_ascii=False)
           print(f"Saved {len(self.transactions)} transactions to {output_file}")
       except Exception as e:
           print(f"Error saving to JSON: {e}")
  
   def get_transaction_summary(self) -> Dict[str, Any]:
       """Get summary statistics of parsed transactions"""
       if not self.transactions:
           return {}
      
       types = {}
       total_amount = 0
       total_fees = 0
      
       for tx in self.transactions:
           tx_type = tx.get('type', 'unknown')
           types[tx_type] = types.get(tx_type, 0) + 1
           total_amount += tx.get('amount', 0)
           total_fees += tx.get('fee', 0)
      
       return {
           'total_transactions': len(self.transactions),
           'transaction_types': types,
           'total_amount': total_amount,
           'total_fees': total_fees,
           'currency': 'RWF'
       }




def main():
   """Main function to parse XML and save JSON"""
   xml_file = '../modified_sms_v2.xml'
   output_file = 'parsed_transactions.json'
  
   parser = SMSParser(xml_file)
   transactions = parser.parse_xml()
  
   if transactions:
       parser.save_to_json(output_file)
       summary = parser.get_transaction_summary()
      
       print("\n=== PARSING SUMMARY ===")
       print(f"Total Transactions: {summary.get('total_transactions', 0)}")
       print(f"Total Amount: {summary.get('total_amount', 0):,.2f} RWF")
       print(f"Total Fees: {summary.get('total_fees', 0):,.2f} RWF")
       print("\nTransaction Types:")
       for tx_type, count in summary.get('transaction_types', {}).items():
           print(f"  {tx_type}: {count}")
      
       print(f"\nFirst 3 transactions:")
       for i, tx in enumerate(transactions[:3]):
           print(f"\n{i+1}. ID: {tx['id']} | Type: {tx['type']} | Amount: {tx['amount']} RWF")
           print(f"   From: {tx['sender']} → To: {tx['receiver']}")
           print(f"   Date: {tx['readable_date']}")
   else:
       print("No transactions parsed. Check XML file and parsing logic.")




if __name__ == "__main__":
   main()


