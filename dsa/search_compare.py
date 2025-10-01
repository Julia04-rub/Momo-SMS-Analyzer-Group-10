#!/usr/bin/env python3
"""
Data Structures & Algorithms Comparison for MoMo SMS API
Compares Linear Search vs Dictionary Lookup performance
"""


import time
import json
import random
from typing import List, Dict, Any, Optional, Tuple
import matplotlib.pyplot as plt
from xml_to_json import SMSParser




class SearchComparison:
   """Compare different search algorithms for transaction data"""
  
   def __init__(self, transactions: List[Dict[str, Any]]):
       self.transactions_list = transactions
       self.transactions_dict = {tx['id']: tx for tx in transactions}
       self.search_results = []
  
   def linear_search(self, target_id: int) -> Optional[Dict[str, Any]]:
       """Linear search through list of transactions"""
       for transaction in self.transactions_list:
           if transaction['id'] == target_id:
               return transaction
       return None
  
   def dictionary_lookup(self, target_id: int) -> Optional[Dict[str, Any]]:
       """Dictionary lookup by key"""
       return self.transactions_dict.get(target_id)
  
   def binary_search(self, target_id: int) -> Optional[Dict[str, Any]]:
       """Binary search on sorted list (assuming sorted by ID)"""
       left, right = 0, len(self.transactions_list) - 1
      
       while left <= right:
           mid = (left + right) // 2
           mid_id = self.transactions_list[mid]['id']
          
           if mid_id == target_id:
               return self.transactions_list[mid]
           elif mid_id < target_id:
               left = mid + 1
           else:
               right = mid - 1
      
       return None
  
   def measure_search_performance(self, num_searches: int = 100) -> Dict[str, Any]:
       """Measure and compare search algorithm performance"""
       if not self.transactions_list:
           return {}
      
       # Generate random search IDs
       search_ids = [random.choice(self.transactions_list)['id'] for _ in range(num_searches)]
      
       # Measure Linear Search
       start_time = time.perf_counter()
       linear_results = []
       for search_id in search_ids:
           result = self.linear_search(search_id)
           linear_results.append(result is not None)
       linear_time = time.perf_counter() - start_time
      
       # Measure Dictionary Lookup
       start_time = time.perf_counter()
       dict_results = []
       for search_id in search_ids:
           result = self.dictionary_lookup(search_id)
           dict_results.append(result is not None)
       dict_time = time.perf_counter() - start_time
      
       # Measure Binary Search (on sorted data)
       sorted_transactions = sorted(self.transactions_list, key=lambda x: x['id'])
       self.sorted_transactions = sorted_transactions
      
       start_time = time.perf_counter()
       binary_results = []
       for search_id in search_ids:
           result = self.binary_search(search_id)
           binary_results.append(result is not None)
       binary_time = time.perf_counter() - start_time
      
       # Calculate results
       results = {
           'dataset_size': len(self.transactions_list),
           'num_searches': num_searches,
           'linear_search': {
               'total_time': linear_time,
               'avg_time_per_search': linear_time / num_searches,
               'success_rate': sum(linear_results) / len(linear_results),
               'time_complexity': 'O(n)'
           },
           'dictionary_lookup': {
               'total_time': dict_time,
               'avg_time_per_search': dict_time / num_searches,
               'success_rate': sum(dict_results) / len(dict_results),
               'time_complexity': 'O(1) average case'
           },
           'binary_search': {
               'total_time': binary_time,
               'avg_time_per_search': binary_time / num_searches,
               'success_rate': sum(binary_results) / len(binary_results),
               'time_complexity': 'O(log n)'
           }
       }
      
       # Performance comparison
       fastest_time = min(linear_time, dict_time, binary_time)
       results['performance_comparison'] = {
           'linear_vs_dict_speedup': linear_time / dict_time if dict_time > 0 else 0,
           'linear_vs_binary_speedup': linear_time / binary_time if binary_time > 0 else 0,
           'dict_vs_binary_speedup': dict_time / binary_time if binary_time > 0 else 0,
           'fastest_algorithm': self._get_fastest_algorithm(linear_time, dict_time, binary_time)
       }
      
       self.search_results = results
       return results
  
   def _get_fastest_algorithm(self, linear_time: float, dict_time: float, binary_time: float) -> str:
       """Determine which algorithm was fastest"""
       times = {
           'linear_search': linear_time,
           'dictionary_lookup': dict_time,
           'binary_search': binary_time
       }
       return min(times, key=times.get)
  
   def run_scalability_test(self, sizes: List[int] = None) -> Dict[str, List[float]]:
       """Test how algorithms scale with different dataset sizes"""
       if sizes is None:
           sizes = [10, 20, 50, 100, 200, 500, 1000]
      
       # Filter sizes to available data
       max_size = len(self.transactions_list)
       sizes = [s for s in sizes if s <= max_size]
      
       scalability_results = {
           'sizes': sizes,
           'linear_times': [],
           'dict_times': [],
           'binary_times': []
       }
      
       for size in sizes:
           # Create subset of data
           subset = self.transactions_list[:size]
           subset_dict = {tx['id']: tx for tx in subset}
          
           # Test search performance on this subset
           search_ids = [random.choice(subset)['id'] for _ in range(min(20, size))]
          
           # Linear search timing
           start_time = time.perf_counter()
           for search_id in search_ids:
               for tx in subset:
                   if tx['id'] == search_id:
                       break
           linear_time = time.perf_counter() - start_time
           scalability_results['linear_times'].append(linear_time)
          
           # Dictionary lookup timing
           start_time = time.perf_counter()
           for search_id in search_ids:
               subset_dict.get(search_id)
           dict_time = time.perf_counter() - start_time
           scalability_results['dict_times'].append(dict_time)
          
           # Binary search timing (on sorted subset)
           sorted_subset = sorted(subset, key=lambda x: x['id'])
           start_time = time.perf_counter()
           for search_id in search_ids:
               self._binary_search_on_list(sorted_subset, search_id)
           binary_time = time.perf_counter() - start_time
           scalability_results['binary_times'].append(binary_time)
      
       return scalability_results
  
   def _binary_search_on_list(self, sorted_list: List[Dict], target_id: int) -> Optional[Dict]:
       """Binary search on a specific sorted list"""
       left, right = 0, len(sorted_list) - 1
      
       while left <= right:
           mid = (left + right) // 2
           mid_id = sorted_list[mid]['id']
          
           if mid_id == target_id:
               return sorted_list[mid]
           elif mid_id < target_id:
               left = mid + 1
           else:
               right = mid - 1
      
       return None
  
   def generate_performance_report(self) -> str:
       """Generate detailed performance analysis report"""
       if not self.search_results:
           return "No performance data available. Run measure_search_performance() first."
      
       results = self.search_results
      
       report = f"""
=== DATA STRUCTURES & ALGORITHMS PERFORMANCE ANALYSIS ===


Dataset Information:
- Total Transactions: {results['dataset_size']:,}
- Number of Search Operations: {results['num_searches']:,}


Performance Results:


1. LINEAR SEARCH (O(n))
  - Total Time: {results['linear_search']['total_time']:.6f} seconds
  - Average Time per Search: {results['linear_search']['avg_time_per_search']:.8f} seconds
  - Success Rate: {results['linear_search']['success_rate']:.2%}
  - Algorithm: Scan through entire list sequentially


2. DICTIONARY LOOKUP (O(1) average)
  - Total Time: {results['dictionary_lookup']['total_time']:.6f} seconds
  - Average Time per Search: {results['dictionary_lookup']['avg_time_per_search']:.8f} seconds
  - Success Rate: {results['dictionary_lookup']['success_rate']:.2%}
  - Algorithm: Hash table lookup by key


3. BINARY SEARCH (O(log n))
  - Total Time: {results['binary_search']['total_time']:.6f} seconds
  - Average Time per Search: {results['binary_search']['avg_time_per_search']:.8f} seconds
  - Success Rate: {results['binary_search']['success_rate']:.2%}
  - Algorithm: Divide and conquer on sorted data


Performance Comparison:
- Fastest Algorithm: {results['performance_comparison']['fastest_algorithm'].replace('_', ' ').title()}
- Linear vs Dictionary Speedup: {results['performance_comparison']['linear_vs_dict_speedup']:.2f}x
- Linear vs Binary Speedup: {results['performance_comparison']['linear_vs_binary_speedup']:.2f}x
- Dictionary vs Binary Speedup: {results['performance_comparison']['dict_vs_binary_speedup']:.2f}x


Analysis:
Dictionary lookup is typically fastest due to O(1) average case complexity.
Binary search is efficient for sorted data with O(log n) complexity.
Linear search has O(n) complexity, making it slowest for large datasets.


Recommendations for API Implementation:
1. Use dictionary/hash map for primary key lookups (transaction by ID)
2. Implement binary search for range queries on sorted fields
3. Consider database indexing for complex queries
4. Cache frequently accessed data in memory using dictionaries
"""
       return report
  
   def save_results(self, filename: str = 'search_performance_results.json'):
       """Save performance results to JSON file"""
       if self.search_results:
           with open(filename, 'w') as f:
               json.dump(self.search_results, f, indent=2)
           print(f"Performance results saved to {filename}")
  
   def create_performance_visualization(self, save_plot: bool = True):
       """Create visualization of performance comparison"""
       if not self.search_results:
           print("No performance data available for visualization")
           return
      
       # Extract timing data
       algorithms = ['Linear Search', 'Dictionary Lookup', 'Binary Search']
       times = [
           self.search_results['linear_search']['total_time'],
           self.search_results['dictionary_lookup']['total_time'],
           self.search_results['binary_search']['total_time']
       ]
      
       # Create bar chart
       plt.figure(figsize=(10, 6))
       bars = plt.bar(algorithms, times, color=['#ff7f7f', '#7f7fff', '#7fff7f'])
      
       plt.title(f'Search Algorithm Performance Comparison\n({self.search_results["num_searches"]} searches on {self.search_results["dataset_size"]} records)')
       plt.ylabel('Total Time (seconds)')
       plt.xlabel('Search Algorithm')
      
       # Add value labels on bars
       for bar, time_val in zip(bars, times):
           plt.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(times)*0.01,
                   f'{time_val:.6f}s', ha='center', va='bottom')
      
       plt.tight_layout()
      
       if save_plot:
           plt.savefig('search_performance_comparison.png', dpi=300, bbox_inches='tight')
           print("Performance chart saved as 'search_performance_comparison.png'")
      
       plt.show()




def main():
   """Main function to run DSA comparison"""
   print("=== MoMo SMS API - Data Structures & Algorithms Analysis ===\n")
  
   # Load parsed transaction data
   xml_file = '../modified_sms_v2.xml'
   parser = SMSParser(xml_file)
   transactions = parser.parse_xml()
  
   if not transactions:
       print("Error: No transaction data available. Run xml_to_json.py first.")
       return
  
   # Limit to reasonable size for testing
   test_transactions = transactions[:100] if len(transactions) > 100 else transactions
   print(f"Using {len(test_transactions)} transactions for DSA analysis\n")
  
   # Initialize search comparison
   search_comp = SearchComparison(test_transactions)
  
   # Run performance comparison
   print("Running search performance analysis...")
   results = search_comp.measure_search_performance(num_searches=50)
  
   # Generate and display report
   report = search_comp.generate_performance_report()
   print(report)
  
   # Save results
   search_comp.save_results()
  
   # Create visualization
   try:
       search_comp.create_performance_visualization()
   except ImportError:
       print("Matplotlib not available - skipping visualization")
  
   # Run scalability test
   print("\n=== SCALABILITY ANALYSIS ===")
   if len(transactions) >= 50:
       scalability_data = search_comp.run_scalability_test([10, 20, 30, 50])
       print("Scalability test completed - data saved for further analysis")
  
   print("\n=== REFLECTION: Why Dictionary Lookup is Faster ===")
   print("""
1. TIME COMPLEXITY:
  - Linear Search: O(n) - Must check every element in worst case
  - Dictionary Lookup: O(1) average - Direct access via hash function
  - Binary Search: O(log n) - Eliminates half the search space each step


2. IMPLEMENTATION DETAILS:
  - Dictionary uses hash table with direct key-to-memory mapping
  - Linear search requires sequential iteration through array
  - Binary search requires sorted data but reduces comparisons logarithmically


3. PRACTICAL IMPLICATIONS FOR API:
  - Use dictionaries for primary key lookups (GET /transactions/{id})
  - Implement database indexes for complex queries
  - Cache frequently accessed data in hash maps
  - Consider search algorithms based on data size and query patterns


4. ALTERNATIVE DATA STRUCTURES:
  - B-trees: Excellent for database indexes and range queries
  - Trie: Efficient for prefix-based searches (phone numbers)
  - Heap: Priority queues for transaction processing
  - Hash tables with chaining: Handle collisions gracefully
   """)




if __name__ == "__main__":
   main()


