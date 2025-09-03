"""
Configuration settings for California Procurement Assistant
"""

# MongoDB configuration
MONGODB_CONFIG = {
    'host': 'localhost',

    'port': 27017,
    'database': 'procurement_db',
    'collection': 'purchases'
}

# Application settings
APP_CONFIG = {
    'title': 'California Procurement Assistant',
    'description': 'AI-powered assistant for procurement data analysis',
    'version': '1.0.0'
}

# Data column mappings (for reference)
DATA_COLUMNS = {
    'creation_date': 'Creation Date',
    'purchase_date': 'Purchase Date',
    'fiscal_year': 'Fiscal Year',
    'po_number': 'Purchase Order Number',
    'acquisition_type': 'Acquisition Type',
    'acquisition_method': 'Acquisition Method',
    'department': 'Department Name',
    'supplier_name': 'Supplier Name',
    'supplier_code': 'Supplier Code',
    'item_name': 'Item Name',
    'item_description': 'Item Description',
    'quantity': 'Quantity',
    'unit_price': 'Unit Price',
    'total_price': 'Total Price'
}