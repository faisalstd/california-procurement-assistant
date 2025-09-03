"""
Data Loader - Imports CSV data into MongoDB
"""

import pandas as pd
from pymongo import MongoClient
import os
from config import MONGODB_CONFIG

print("="*50)
print("Data Loader - Starting...")
print("="*50)

# Check for CSV file
print("\n1. Checking for data file...")

possible_names = [
    'data/procurement_data.csv',
    'data/PURCHASE ORDER DATA EXTRACT 2012-2015_0.csv',
    'data/purchase_order_data.csv'
]

csv_file = None
for name in possible_names:
    if os.path.exists(name):
        csv_file = name
        print(f"   Found: {name}")
        break

if not csv_file:
    print("   ERROR: No CSV file found!")
    print("\n   Files in 'data' folder:")
    if os.path.exists('data'):
        files = os.listdir('data')
        for f in files:
            print(f"   - {f}")
    else:
        print("   - 'data' folder doesn't exist!")
    print("\n   Please:")
    print("   1. Download the file from Kaggle")
    print("   2. Put it in 'data' folder")
    exit()

# Connect to MongoDB
print("\n2. Connecting to MongoDB...")
try:
    client = MongoClient(
        host=MONGODB_CONFIG['host'],
        port=MONGODB_CONFIG['port'],
        serverSelectionTimeoutMS=5000
    )
    client.server_info()
    db = client[MONGODB_CONFIG['database']]
    collection = db[MONGODB_CONFIG['collection']]
    print("   Connected successfully!")
except Exception as e:
    print(f"   ERROR: Cannot connect to MongoDB!")
    print(f"   {e}")
    print("\n   Make sure MongoDB Compass is open and connected")
    exit()

# Read CSV file
print(f"\n3. Reading CSV file...")
print(f"   File: {csv_file}")

try:
    df = pd.read_csv(csv_file, low_memory=False)
    print(f"   Success! Loaded {len(df):,} rows")
    print(f"   Columns: {len(df.columns)}")
    
    print(f"\n   Sample columns:")
    for col in df.columns[:5]:
        print(f"   - {col}")
        
except Exception as e:
    print(f"   ERROR reading file: {e}")
    exit()

# Clean data
print("\n4. Cleaning data...")

rows_before = len(df)

# Remove empty rows
df = df.dropna(how='all')

# Clean price columns
for col in ['Total Price', 'Unit Price']:
    if col in df.columns:
        df[col] = df[col].astype(str).str.replace('$', '').str.replace(',', '')
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col] = df[col].fillna(0)

# Clean quantity column
if 'Quantity' in df.columns:
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)

rows_after = len(df)
print(f"   Cleaned! Removed {rows_before - rows_after} empty rows")
print(f"   Final rows: {rows_after:,}")

# Load to MongoDB
print("\n5. Loading to MongoDB...")
print("   This may take 1-2 minutes...")

try:
    # Delete old data
    old_count = collection.count_documents({})
    if old_count > 0:
        print(f"   Deleting {old_count:,} old records...")
        collection.delete_many({})
    
    # Convert to dictionary
    records = df.to_dict('records')
    
    # Insert in batches
    batch_size = 5000
    total = len(records)
    inserted = 0
    
    for i in range(0, total, batch_size):
        batch = records[i:i+batch_size]
        collection.insert_many(batch)
        inserted += len(batch)
        
        # Show progress
        percent = (inserted / total) * 100
        print(f"   Progress: {inserted:,}/{total:,} ({percent:.0f}%)")
    
    print(f"   Complete! Inserted {inserted:,} records")
    
except Exception as e:
    print(f"   ERROR: {e}")
    exit()

# Verify data
print("\n6. Verifying data...")

count = collection.count_documents({})
print(f"   Total records: {count:,}")

depts = len(collection.distinct('Department Name'))
print(f"   Departments: {depts}")

suppliers = len(collection.distinct('Supplier Name'))
print(f"   Suppliers: {suppliers}")

# Calculate total spending
pipeline = [
    {'$group': {
        '_id': None,
        'total': {'$sum': '$Total Price'},
        'avg': {'$avg': '$Total Price'}
    }}
]
result = list(collection.aggregate(pipeline))
if result:
    print(f"   Total spending: ${result[0]['total']:,.2f}")
    print(f"   Average order: ${result[0]['avg']:,.2f}")

print("\n" + "="*50)
print("SUCCESS! Data is ready to use")
print("="*50)

client.close()