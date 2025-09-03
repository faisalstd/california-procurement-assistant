"""
Ollama Agent - Handles natural language queries for procurement data
"""
import requests
import json
from pymongo import MongoClient
from config import MONGODB_CONFIG
from datetime import datetime

class OllamaAgent:
    def __init__(self):
        self.client = MongoClient(
            host=MONGODB_CONFIG['host'],
            port=MONGODB_CONFIG['port']
        )
        self.db = self.client[MONGODB_CONFIG['database']]
        self.collection = self.db[MONGODB_CONFIG['collection']]
        self.ollama_url = "http://localhost:11434/api/generate"
        
    def understand_query(self, question):
        """Parse and understand user query"""
        q = question.lower()
        
        # Year and time filtering
        filters = {}
        
        # Year detection
        if '2013' in question:
            filters['Fiscal Year'] = '2013-2014'
        elif '2012' in question:
            filters['Fiscal Year'] = '2012-2013'
        elif '2014' in question:
            filters['Fiscal Year'] = '2014-2015'
        elif '2015' in question:
            filters['Fiscal Year'] = '2014-2015'
        
        # Quarter detection
        if 'q1' in q or 'first quarter' in q:
            filters['quarter'] = 'Q1'
        elif 'q2' in q or 'second quarter' in q:
            filters['quarter'] = 'Q2'
        elif 'q3' in q or 'third quarter' in q:
            filters['quarter'] = 'Q3'
        elif 'q4' in q or 'fourth quarter' in q:
            filters['quarter'] = 'Q4'
        
        # Price range detection
        if 'over' in q and ('million' in q or '1000000' in q):
            filters['min_price'] = 1000000
        elif 'under' in q and ('thousand' in q or '1000' in q):
            filters['max_price'] = 1000
        
        # Department detection
        if 'it ' in q or 'information technology' in q:
            filters['Department Name'] = {'$regex': 'Information Technology', '$options': 'i'}
        elif 'health' in q:
            filters['Department Name'] = {'$regex': 'Health', '$options': 'i'}
        
        # Query type detection
        if 'quarter' in q and ('highest' in q or 'most' in q) and 'spending' in q:
            return {'query_type': 'highest_quarter', 'filters': filters}
        elif ('month' in q or 'monthly' in q) and ('trend' in q or 'analysis' in q):
            return {'query_type': 'monthly_analysis', 'filters': filters}
        elif 'trend' in q or 'over time' in q:
            return {'query_type': 'trend_analysis', 'filters': filters}
        elif 'compare' in q and ('between' in q or 'vs' in q):
            return {'query_type': 'comparison', 'filters': filters}
        elif 'expensive' in q and ('most' in q or 'top' in q):
            return {'query_type': 'most_expensive', 'filters': filters}
        elif ('highest' in q or 'most' in q) and ('sales' in q or 'item' in q or 'product' in q):
            return {'query_type': 'top_items', 'filters': filters}
        elif 'frequently' in q or 'frequent' in q or 'most ordered' in q or 'most times' in q:
            return {'query_type': 'frequency', 'filters': filters}
        elif 'total' in q or 'spending' in q:
            return {'query_type': 'sum', 'filters': filters}
        elif 'average' in q:
            return {'query_type': 'average', 'filters': filters}
        elif 'count' in q or 'how many' in q:
            return {'query_type': 'count', 'filters': filters}
        elif 'department' in q and 'most' in q:
            return {'query_type': 'top_departments', 'filters': filters}
        elif 'supplier' in q:
            return {'query_type': 'top_suppliers', 'filters': filters}
        elif 'acquisition method' in q:
            return {'query_type': 'acquisition_methods', 'filters': filters}
        else:
            return {'query_type': 'list', 'filters': filters}
            
    def generate_mongodb_query(self, query_info):
        """Generate MongoDB aggregation pipeline"""
        pipeline = []
        
        # Apply filters
        match_conditions = {}
        filters = query_info.get('filters', {})
        
        for key, value in filters.items():
            if key not in ['quarter', 'min_price', 'max_price']:
                match_conditions[key] = value
        
        # Handle price range filters
        if 'min_price' in filters:
            match_conditions['Total Price'] = {'$gte': filters['min_price']}
        if 'max_price' in filters:
            if 'Total Price' in match_conditions:
                match_conditions['Total Price']['$lte'] = filters['max_price']
            else:
                match_conditions['Total Price'] = {'$lte': filters['max_price']}
        
        if match_conditions:
            pipeline.append({'$match': match_conditions})
            
        query_type = query_info.get('query_type', 'list')
        
        # Handle different query types
        if query_type == 'sum':
            pipeline.append({'$group': {'_id': None, 'total': {'$sum': '$Total Price'}}})
            
        elif query_type == 'average':
            pipeline.append({'$group': {'_id': None, 'average': {'$avg': '$Total Price'}}})
            
        elif query_type == 'count':
            pipeline.append({'$count': 'total'})
            
        elif query_type == 'most_expensive':
            pipeline.append({'$sort': {'Total Price': -1}})
            pipeline.append({'$limit': 10})
            
        elif query_type == 'highest_quarter':
            pipeline = [
                {'$addFields': {
                    'month': {'$month': {'$dateFromString': {
                        'dateString': '$Creation Date',
                        'onError': None
                    }}}
                }},
                {'$addFields': {
                    'quarter': {'$cond': [
                        {'$lte': ['$month', 3]}, 'Q1',
                        {'$cond': [
                            {'$lte': ['$month', 6]}, 'Q2',
                            {'$cond': [
                                {'$lte': ['$month', 9]}, 'Q3', 'Q4'
                            ]}
                        ]}
                    ]}
                }},
                {'$group': {
                    '_id': {'fiscal_year': '$Fiscal Year', 'quarter': '$quarter'},
                    'total_spending': {'$sum': '$Total Price'},
                    'count': {'$sum': 1}
                }},
                {'$sort': {'total_spending': -1}},
                {'$limit': 5}
            ]
            
        elif query_type == 'monthly_analysis':
            pipeline = [
                {'$addFields': {
                    'date': {'$dateFromString': {
                        'dateString': '$Creation Date',
                        'onError': None
                    }}
                }},
                {'$match': {'date': {'$ne': None}}},
                {'$group': {
                    '_id': {
                        'year': {'$year': '$date'},
                        'month': {'$month': '$date'}
                    },
                    'total': {'$sum': '$Total Price'},
                    'count': {'$sum': 1},
                    'avg': {'$avg': '$Total Price'}
                }},
                {'$sort': {'_id.year': 1, '_id.month': 1}},
                {'$limit': 12}
            ]
            
        elif query_type == 'trend_analysis':
            pipeline = [
                {'$group': {
                    '_id': '$Fiscal Year',
                    'total_spending': {'$sum': '$Total Price'},
                    'total_orders': {'$sum': 1},
                    'avg_order': {'$avg': '$Total Price'}
                }},
                {'$sort': {'_id': 1}}
            ]
            
        elif query_type == 'comparison':
            pipeline = [
                {'$group': {
                    '_id': '$Fiscal Year',
                    'total': {'$sum': '$Total Price'},
                    'count': {'$sum': 1},
                    'avg': {'$avg': '$Total Price'},
                    'max': {'$max': '$Total Price'}
                }},
                {'$sort': {'_id': 1}}
            ]
            
        elif query_type == 'top_items':
            pipeline.append({
                '$group': {
                    '_id': '$Item Name',
                    'total_sales': {'$sum': '$Total Price'},
                    'quantity': {'$sum': '$Quantity'},
                    'orders': {'$sum': 1}
                }
            })
            pipeline.append({'$sort': {'total_sales': -1}})
            pipeline.append({'$limit': 5})
            
        elif query_type == 'frequency':
            pipeline.append({
                '$group': {
                    '_id': '$Item Name',
                    'frequency': {'$sum': 1},
                    'total_quantity': {'$sum': '$Quantity'},
                    'total_spent': {'$sum': '$Total Price'}
                }
            })
            pipeline.append({'$sort': {'frequency': -1}})
            pipeline.append({'$limit': 5})
            
        elif query_type == 'top_departments':
            pipeline = [
                {'$group': {
                    '_id': '$Department Name',
                    'total': {'$sum': '$Total Price'},
                    'count': {'$sum': 1},
                    'avg_purchase': {'$avg': '$Total Price'}
                }},
                {'$sort': {'total': -1}},
                {'$limit': 5}
            ]
            
        elif query_type == 'top_suppliers':
            pipeline = [
                {'$group': {
                    '_id': '$Supplier Name',
                    'total': {'$sum': '$Total Price'},
                    'count': {'$sum': 1},
                    'avg_order': {'$avg': '$Total Price'}
                }},
                {'$sort': {'total': -1}},
                {'$limit': 5}
            ]
            
        elif query_type == 'acquisition_methods':
            pipeline = [
                {'$group': {
                    '_id': '$Acquisition Method',
                    'count': {'$sum': 1},
                    'total': {'$sum': '$Total Price'},
                    'avg': {'$avg': '$Total Price'}
                }},
                {'$sort': {'count': -1}}
            ]
            
        else:
            pipeline.append({'$limit': 10})
            
        return pipeline
        
    def execute_query(self, pipeline):
        """Execute MongoDB query with better error handling"""
        try:
            # Allow disk use for large aggregations
            results = list(self.collection.aggregate(pipeline, allowDiskUse=True))
            return results
        except Exception as e:
            print(f"Query execution error: {e}")
            print(f"Pipeline: {pipeline}")
            return None
            
    def format_response(self, results, query_info, question):
        """Format results into readable response"""
        if not results:
            return "No results found. Try rephrasing your question or check the date range."
            
        query_type = query_info.get('query_type')
        
        if query_type == 'sum':
            total = results[0].get('total', 0)
            return f"**Total Spending:** ${total:,.2f}"
            
        elif query_type == 'average':
            avg = results[0].get('average', 0)
            return f"**Average Purchase Amount:** ${avg:,.2f}"
            
        elif query_type == 'count':
            count = results[0].get('total', 0)
            return f"**Total Number of Purchases:** {count:,}"
            
        elif query_type == 'most_expensive':
            response = "## Top 10 Most Expensive Purchases:\n\n"
            for i, item in enumerate(results, 1):
                response += f"**{i}.** {item.get('Item Name', 'N/A')}\n"
                response += f"   - Price: ${item.get('Total Price', 0):,.2f}\n"
                response += f"   - Supplier: {item.get('Supplier Name', 'N/A')}\n"
                response += f"   - Department: {item.get('Department Name', 'N/A')}\n\n"
            return response
            
        elif query_type == 'highest_quarter':
            response = "## Quarterly Spending Analysis:\n\n"
            for i, item in enumerate(results, 1):
                fy = item['_id'].get('fiscal_year', 'N/A')
                quarter = item['_id'].get('quarter', 'N/A')
                response += f"**{i}. {fy} - {quarter}**\n"
                response += f"   - Total: ${item['total_spending']:,.2f}\n"
                response += f"   - Orders: {item['count']:,}\n\n"
            return response
            
        elif query_type == 'monthly_analysis':
            response = "## Monthly Spending Trend:\n\n"
            for item in results:
                year = item['_id'].get('year', 'N/A')
                month = item['_id'].get('month', 'N/A')
                response += f"**{year}-{month:02d}:**\n"
                response += f"   - Total: ${item['total']:,.2f}\n"
                response += f"   - Orders: {item['count']:,}\n"
                response += f"   - Average: ${item['avg']:,.2f}\n\n"
            return response
            
        elif query_type == 'trend_analysis':
            response = "## Spending Trend Over Time:\n\n"
            for item in results:
                response += f"**{item['_id']}:**\n"
                response += f"   - Total Spending: ${item['total_spending']:,.2f}\n"
                response += f"   - Total Orders: {item['total_orders']:,}\n"
                response += f"   - Average Order: ${item['avg_order']:,.2f}\n\n"
            return response
            
        elif query_type == 'comparison':
            response = "## Year-over-Year Comparison:\n\n"
            for item in results:
                response += f"**{item['_id']}:**\n"
                response += f"   - Total: ${item['total']:,.2f}\n"
                response += f"   - Count: {item['count']:,}\n"
                response += f"   - Average: ${item['avg']:,.2f}\n"
                response += f"   - Maximum: ${item['max']:,.2f}\n\n"
            return response
            
        elif query_type == 'top_items':
            response = "## Items with Highest Sales:\n\n"
            for i, item in enumerate(results, 1):
                if item['_id']:
                    response += f"**{i}. {item['_id']}**\n"
                    response += f"   - Total Sales: ${item['total_sales']:,.2f}\n"
                    response += f"   - Quantity: {item['quantity']:,.0f}\n"
                    response += f"   - Orders: {item['orders']}\n\n"
            return response
            
        elif query_type == 'frequency':
            response = "## Most Frequently Ordered Items:\n\n"
            for i, item in enumerate(results, 1):
                if item['_id']:
                    response += f"**{i}. {item['_id']}**\n"
                    response += f"   - Ordered {item['frequency']} times\n"
                    response += f"   - Total Quantity: {item.get('total_quantity', 0):,.0f}\n"
                    response += f"   - Total Spent: ${item['total_spent']:,.2f}\n\n"
            return response
            
        elif query_type == 'top_departments':
            response = "## Top Departments by Spending:\n\n"
            for i, item in enumerate(results, 1):
                response += f"**{i}. {item['_id']}**\n"
                response += f"   - Total: ${item['total']:,.2f}\n"
                response += f"   - Orders: {item['count']:,}\n"
                response += f"   - Average Purchase: ${item['avg_purchase']:,.2f}\n\n"
            return response
            
        elif query_type == 'top_suppliers':
            response = "## Top Suppliers by Revenue:\n\n"
            for i, item in enumerate(results, 1):
                response += f"**{i}. {item['_id']}**\n"
                response += f"   - Total Revenue: ${item['total']:,.2f}\n"
                response += f"   - Orders: {item['count']:,}\n"
                response += f"   - Average Order: ${item['avg_order']:,.2f}\n\n"
            return response
            
        elif query_type == 'acquisition_methods':
            response = "## Acquisition Methods Analysis:\n\n"
            for item in results[:10]:
                if item['_id']:
                    response += f"**{item['_id']}:**\n"
                    response += f"   - Orders: {item['count']:,}\n"
                    response += f"   - Total: ${item['total']:,.2f}\n"
                    response += f"   - Average: ${item['avg']:,.2f}\n\n"
            return response
            
        else:
            # Generic list response
            response = "## Query Results:\n\n"
            for i, item in enumerate(results[:10], 1):
                response += f"{i}. Item: {item.get('Item Name', 'N/A')}\n"
                response += f"   Price: ${item.get('Total Price', 0):,.2f}\n\n"
            return response
            
    def answer_question(self, question):
        """Main entry point for answering questions"""
        try:
            # Understand the query
            query_info = self.understand_query(question)
            
            # Generate MongoDB pipeline
            pipeline = self.generate_mongodb_query(query_info)
            
            # Execute query
            results = self.execute_query(pipeline)
            
            # Format and return response
            return self.format_response(results, query_info, question)
            
        except Exception as e:
            return f"An error occurred while processing your question: {str(e)}\n\nPlease try rephrasing your question."