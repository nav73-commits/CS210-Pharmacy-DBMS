#!/usr/bin/env python3
"""
Pharmacy Database Management System
Python version of the Java Pharmacy Database application

DATABASE CONNECTION INFO:
- Database Type: SQLite
- Database File: pharmacy_database.db (local file)
- Connection Method: sqlite3.connect()
- Tables: location, pharmacy, medicine, customer, available, purchase
"""

import sqlite3
import os
import sys
import io

# Fix Unicode printing issues on Windows terminals
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf8')
    except (AttributeError, io.UnsupportedOperation):
        pass # Fallback if stdout is already wrapped or not a buffer

# ============================================================================
# DATABASE CONNECTION CONFIGURATION
# ============================================================================

# Database file path (SQLite creates a local file)
DB_PATH = 'pharmacy_database.db'

def get_connection():
    """
    Create and return a database connection
    
    Connection Details:
    - Type: SQLite (file-based database)
    - File: pharmacy_database.db
    - Location: Same directory as this script
    - No username/password required for SQLite
    """
    print(f"[DB CONNECTION] Connecting to SQLite database: {DB_PATH}")
    print(f"[DB CONNECTION] Database location: {os.path.abspath(DB_PATH)}")
    conn = sqlite3.connect(DB_PATH)
    print("[DB CONNECTION] Successfully connected!")
    return conn

def show_database_info():
    """Display database connection and schema information"""
    print("\n" + "="*70)
    print("DATABASE CONNECTION INFORMATION")
    print("="*70)
    print(f"Database Type: SQLite")
    print(f"Database File: {DB_PATH}")
    print(f"Full Path: {os.path.abspath(DB_PATH)}")
    if os.path.exists(DB_PATH):
        print(f"File Size: {os.path.getsize(DB_PATH) / 1024:.2f} KB")
    else:
        print(f"File Size: 0.00 KB (File not found - will be initialized)")
    print("\nConnection String: sqlite3.connect('pharmacy_database.db')")
    print("\nTables:")
    print("  1. location   - Stores location information")
    print("  2. pharmacy   - Stores pharmacy details")
    print("  3. medicine   - Stores medicine information")
    print("  4. customer   - Stores customer details")
    print("  5. available  - Junction table (medicine-pharmacy)")
    print("  6. purchase   - Junction table (medicine-customer)")
    print("="*70)
    
    # Show current data counts
    conn = get_connection()
    cursor = conn.cursor()
    print("\nCurrent Data Counts:")
    tables = ['location', 'pharmacy', 'medicine', 'customer', 'available', 'purchase']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table:12} : {count:3} records")
    conn.close()
    print("="*70)

def init_database():
    """Initialize the database with all tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Location table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS location (
            location_id TEXT PRIMARY KEY,
            location_name TEXT NOT NULL
        )
    ''')
    
    # Pharmacy table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pharmacy (
            pharmacy_id TEXT PRIMARY KEY,
            pharmacy_name TEXT NOT NULL,
            location_id TEXT,
            FOREIGN KEY (location_id) REFERENCES location(location_id)
        )
    ''')
    
    # Medicine table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicine (
            med_id TEXT PRIMARY KEY,
            med_name TEXT NOT NULL,
            cost REAL NOT NULL,
            dosage_mg INTEGER NOT NULL
        )
    ''')
    
    # Customer table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customer (
            cust_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER,
            address TEXT,
            phone TEXT,
            pharmacy_id TEXT,
            FOREIGN KEY (pharmacy_id) REFERENCES pharmacy(pharmacy_id)
        )
    ''')
    
    # Available table (junction table for medicine-pharmacy)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS available (
            med_id TEXT,
            pharmacy_id TEXT,
            PRIMARY KEY (med_id, pharmacy_id),
            FOREIGN KEY (med_id) REFERENCES medicine(med_id),
            FOREIGN KEY (pharmacy_id) REFERENCES pharmacy(pharmacy_id)
        )
    ''')
    
    # Purchase table (junction table for medicine-customer)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchase (
            med_id TEXT,
            cust_id TEXT,
            PRIMARY KEY (med_id, cust_id),
            FOREIGN KEY (med_id) REFERENCES medicine(med_id),
            FOREIGN KEY (cust_id) REFERENCES customer(cust_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✓ Database initialized successfully!")

# ==================== LOCATION MANAGEMENT ====================

def add_location(location_id, location_name):
    """Add a new location to the database"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO location VALUES (?, ?)", (location_id, location_name))
        conn.commit()
        print(f"✓ Location '{location_name}' added successfully!")
        return True
    except sqlite3.IntegrityError:
        print(f"✗ Error: Location ID '{location_id}' already exists!")
        return False
    finally:
        conn.close()

def display_locations():
    """Display all locations"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM location")
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("No locations found.")
    else:
        print("\n=== All Locations ===")
        print(f"{'Location ID':<15} {'Location Name'}")
        print("-" * 40)
        for row in rows:
            print(f"{row[0]:<15} {row[1]}")
    return rows

def delete_location(location_id):
    """Delete a location from the database"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM location WHERE location_id = ?", (location_id,))
    if cursor.rowcount > 0:
        conn.commit()
        print(f"✓ Location '{location_id}' deleted successfully!")
    else:
        print(f"✗ Error: Location '{location_id}' not found!")
    conn.close()

# ==================== PHARMACY MANAGEMENT ====================

def add_pharmacy(pharmacy_id, pharmacy_name, location_id):
    """Add a new pharmacy to the database"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO pharmacy VALUES (?, ?, ?)", 
                      (pharmacy_id, pharmacy_name, location_id))
        conn.commit()
        print(f"✓ Pharmacy '{pharmacy_name}' added successfully!")
        return True
    except sqlite3.IntegrityError as e:
        print(f"✗ Error: {e}")
        return False
    finally:
        conn.close()

def display_pharmacies():
    """Display all pharmacies with location details"""
    conn = get_connection()
    cursor = conn.cursor()
    query = '''
        SELECT p.pharmacy_id, p.pharmacy_name, l.location_name 
        FROM pharmacy p
        LEFT JOIN location l ON p.location_id = l.location_id
    '''
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("No pharmacies found.")
    else:
        print("\n=== All Pharmacies ===")
        print(f"{'Pharmacy ID':<15} {'Pharmacy Name':<20} {'Location'}")
        print("-" * 60)
        for row in rows:
            print(f"{row[0]:<15} {row[1]:<20} {row[2]}")
    return rows

def update_pharmacy(pharmacy_id, pharmacy_name=None, location_id=None):
    """Update pharmacy details"""
    conn = get_connection()
    cursor = conn.cursor()
    updates = []
    values = []
    
    if pharmacy_name:
        updates.append("pharmacy_name = ?")
        values.append(pharmacy_name)
    if location_id:
        updates.append("location_id = ?")
        values.append(location_id)
    
    if updates:
        values.append(pharmacy_id)
        query = f"UPDATE pharmacy SET {', '.join(updates)} WHERE pharmacy_id = ?"
        cursor.execute(query, values)
        if cursor.rowcount > 0:
            conn.commit()
            print(f"✓ Pharmacy '{pharmacy_id}' updated successfully!")
        else:
            print(f"✗ Error: Pharmacy '{pharmacy_id}' not found!")
    conn.close()

def delete_pharmacy(pharmacy_id):
    """Delete a pharmacy from the database"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pharmacy WHERE pharmacy_id = ?", (pharmacy_id,))
    if cursor.rowcount > 0:
        conn.commit()
        print(f"✓ Pharmacy '{pharmacy_id}' deleted successfully!")
    else:
        print(f"✗ Error: Pharmacy '{pharmacy_id}' not found!")
    conn.close()

# ==================== MEDICINE MANAGEMENT ====================

def add_medicine(med_id, med_name, cost, dosage_mg):
    """Add a new medicine to the database"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO medicine VALUES (?, ?, ?, ?)", 
                      (med_id, med_name, float(cost), int(dosage_mg)))
        conn.commit()
        print(f"✓ Medicine '{med_name}' added successfully!")
        return True
    except sqlite3.IntegrityError:
        print(f"✗ Error: Medicine ID '{med_id}' already exists!")
        return False
    finally:
        conn.close()

def display_medicines():
    """Display all medicines"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicine")
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("No medicines found.")
    else:
        print("\n=== All Medicines ===")
        print(f"{'Med ID':<10} {'Medicine Name':<20} {'Cost':<10} {'Dosage (mg)'}")
        print("-" * 60)
        for row in rows:
            print(f"{row[0]:<10} {row[1]:<20} ${row[2]:<9.2f} {row[3]}")
    return rows

def update_medicine(med_id, med_name=None, cost=None, dosage_mg=None):
    """Update medicine details"""
    conn = get_connection()
    cursor = conn.cursor()
    updates = []
    values = []
    
    if med_name:
        updates.append("med_name = ?")
        values.append(med_name)
    if cost:
        updates.append("cost = ?")
        values.append(float(cost))
    if dosage_mg:
        updates.append("dosage_mg = ?")
        values.append(int(dosage_mg))
    
    if updates:
        values.append(med_id)
        query = f"UPDATE medicine SET {', '.join(updates)} WHERE med_id = ?"
        cursor.execute(query, values)
        if cursor.rowcount > 0:
            conn.commit()
            print(f"✓ Medicine '{med_id}' updated successfully!")
        else:
            print(f"✗ Error: Medicine '{med_id}' not found!")
    conn.close()

def delete_medicine(med_id):
    """Delete a medicine from the database"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM medicine WHERE med_id = ?", (med_id,))
    if cursor.rowcount > 0:
        conn.commit()
        print(f"✓ Medicine '{med_id}' deleted successfully!")
    else:
        print(f"✗ Error: Medicine '{med_id}' not found!")
    conn.close()

# ==================== CUSTOMER MANAGEMENT ====================

def add_customer(cust_id, name, age, address, phone, pharmacy_id):
    """Add a new customer to the database"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO customer VALUES (?, ?, ?, ?, ?, ?)", 
                      (cust_id, name, int(age), address, phone, pharmacy_id))
        conn.commit()
        print(f"✓ Customer '{name}' added successfully!")
        return True
    except sqlite3.IntegrityError:
        print(f"✗ Error: Customer ID '{cust_id}' already exists!")
        return False
    finally:
        conn.close()

def display_customers():
    """Display all customers with pharmacy details"""
    conn = get_connection()
    cursor = conn.cursor()
    query = '''
        SELECT c.cust_id, c.name, c.age, c.address, c.phone, p.pharmacy_name
        FROM customer c
        LEFT JOIN pharmacy p ON c.pharmacy_id = p.pharmacy_id
    '''
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("No customers found.")
    else:
        print("\n=== All Customers ===")
        print(f"{'Cust ID':<10} {'Name':<15} {'Age':<5} {'Phone':<12} {'Pharmacy'}")
        print("-" * 70)
        for row in rows:
            print(f"{row[0]:<10} {row[1]:<15} {row[2]:<5} {row[4]:<12} {row[5]}")
    return rows

def update_customer(cust_id, name=None, age=None, address=None, phone=None, pharmacy_id=None):
    """Update customer details"""
    conn = get_connection()
    cursor = conn.cursor()
    updates = []
    values = []
    
    if name:
        updates.append("name = ?")
        values.append(name)
    if age:
        updates.append("age = ?")
        values.append(int(age))
    if address:
        updates.append("address = ?")
        values.append(address)
    if phone:
        updates.append("phone = ?")
        values.append(phone)
    if pharmacy_id:
        updates.append("pharmacy_id = ?")
        values.append(pharmacy_id)
    
    if updates:
        values.append(cust_id)
        query = f"UPDATE customer SET {', '.join(updates)} WHERE cust_id = ?"
        cursor.execute(query, values)
        if cursor.rowcount > 0:
            conn.commit()
            print(f"✓ Customer '{cust_id}' updated successfully!")
        else:
            print(f"✗ Error: Customer '{cust_id}' not found!")
    conn.close()

def delete_customer(cust_id):
    """Delete a customer from the database"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customer WHERE cust_id = ?", (cust_id,))
    if cursor.rowcount > 0:
        conn.commit()
        print(f"✓ Customer '{cust_id}' deleted successfully!")
    else:
        print(f"✗ Error: Customer '{cust_id}' not found!")
    conn.close()

# ==================== AVAILABLE MEDICINES ====================

def add_available(med_id, pharmacy_id):
    """Add medicine availability at a pharmacy"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO available VALUES (?, ?)", (med_id, pharmacy_id))
        conn.commit()
        print(f"✓ Medicine '{med_id}' is now available at pharmacy '{pharmacy_id}'!")
        return True
    except sqlite3.IntegrityError:
        print(f"✗ Error: This availability record already exists!")
        return False
    finally:
        conn.close()

def display_available():
    """Display all available medicines at pharmacies"""
    conn = get_connection()
    cursor = conn.cursor()
    query = '''
        SELECT a.med_id, m.med_name, a.pharmacy_id, p.pharmacy_name
        FROM available a
        JOIN medicine m ON a.med_id = m.med_id
        JOIN pharmacy p ON a.pharmacy_id = p.pharmacy_id
    '''
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("No availability records found.")
    else:
        print("\n=== Available Medicines at Pharmacies ===")
        print(f"{'Med ID':<10} {'Medicine Name':<20} {'Pharmacy ID':<12} {'Pharmacy Name'}")
        print("-" * 70)
        for row in rows:
            print(f"{row[0]:<10} {row[1]:<20} {row[2]:<12} {row[3]}")
    return rows

def delete_available(med_id, pharmacy_id):
    """Remove medicine availability from a pharmacy"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM available WHERE med_id = ? AND pharmacy_id = ?", 
                   (med_id, pharmacy_id))
    if cursor.rowcount > 0:
        conn.commit()
        print(f"✓ Availability record deleted successfully!")
    else:
        print(f"✗ Error: Availability record not found!")
    conn.close()

# ==================== PURCHASE MANAGEMENT ====================

def add_purchase(med_id, cust_id):
    """Record a medicine purchase by a customer"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO purchase VALUES (?, ?)", (med_id, cust_id))
        conn.commit()
        print(f"✓ Purchase recorded: Medicine '{med_id}' by Customer '{cust_id}'!")
        return True
    except sqlite3.IntegrityError:
        print(f"✗ Error: This purchase record already exists!")
        return False
    finally:
        conn.close()

def display_purchases():
    """Display all purchase details"""
    conn = get_connection()
    cursor = conn.cursor()
    query = '''
        SELECT p.med_id, m.med_name, p.cust_id, c.name as customer_name, 
               m.cost as purchase_amount
        FROM purchase p
        JOIN medicine m ON p.med_id = m.med_id
        JOIN customer c ON p.cust_id = c.cust_id
    '''
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("No purchase records found.")
    else:
        print("\n=== All Purchase Details ===")
        print(f"{'Med ID':<10} {'Medicine':<15} {'Cust ID':<10} {'Customer':<15} {'Amount'}")
        print("-" * 70)
        for row in rows:
            print(f"{row[0]:<10} {row[1]:<15} {row[2]:<10} {row[3]:<15} ${row[4]:.2f}")
    return rows

def delete_purchase(med_id, cust_id):
    """Delete a purchase record"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM purchase WHERE med_id = ? AND cust_id = ?", 
                   (med_id, cust_id))
    if cursor.rowcount > 0:
        conn.commit()
        print(f"✓ Purchase record deleted successfully!")
    else:
        print(f"✗ Error: Purchase record not found!")
    conn.close()

# ==================== ADVANCED QUERIES ====================

def search_medicine_by_name(name_pattern):
    """Search medicines by name pattern"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicine WHERE med_name LIKE ?", (f"%{name_pattern}%",))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print(f"No medicines found matching '{name_pattern}'")
    else:
        print(f"\n=== Medicines matching '{name_pattern}' ===")
        print(f"{'Med ID':<10} {'Medicine Name':<20} {'Cost':<10} {'Dosage (mg)'}")
        print("-" * 60)
        for row in rows:
            print(f"{row[0]:<10} {row[1]:<20} ${row[2]:<9.2f} {row[3]}")
    return rows

def get_customer_purchase_history(cust_id):
    """Get purchase history for a specific customer"""
    conn = get_connection()
    cursor = conn.cursor()
    query = '''
        SELECT p.med_id, m.med_name, m.cost, m.dosage_mg
        FROM purchase p
        JOIN medicine m ON p.med_id = m.med_id
        WHERE p.cust_id = ?
    '''
    cursor.execute(query, (cust_id,))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print(f"No purchase history found for customer '{cust_id}'")
    else:
        print(f"\n=== Purchase History for Customer '{cust_id}' ===")
        print(f"{'Med ID':<10} {'Medicine Name':<20} {'Cost':<10} {'Dosage (mg)'}")
        print("-" * 60)
        total = 0
        for row in rows:
            print(f"{row[0]:<10} {row[1]:<20} ${row[2]:<9.2f} {row[3]}")
            total += row[2]
        print("-" * 60)
        print(f"Total spent: ${total:.2f}")
    return rows

def get_pharmacy_inventory(pharmacy_id):
    """Get all medicines available at a specific pharmacy"""
    conn = get_connection()
    cursor = conn.cursor()
    query = '''
        SELECT a.med_id, m.med_name, m.cost, m.dosage_mg
        FROM available a
        JOIN medicine m ON a.med_id = m.med_id
        WHERE a.pharmacy_id = ?
    '''
    cursor.execute(query, (pharmacy_id,))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print(f"No inventory found for pharmacy '{pharmacy_id}'")
    else:
        print(f"\n=== Inventory for Pharmacy '{pharmacy_id}' ===")
        print(f"{'Med ID':<10} {'Medicine Name':<20} {'Cost':<10} {'Dosage (mg)'}")
        print("-" * 60)
        for row in rows:
            print(f"{row[0]:<10} {row[1]:<20} ${row[2]:<9.2f} {row[3]}")
    return rows

def get_total_sales_report():
    """Generate a total sales report"""
    conn = get_connection()
    cursor = conn.cursor()
    query = '''
        SELECT COUNT(*) as total_purchases, SUM(m.cost) as total_revenue
        FROM purchase p
        JOIN medicine m ON p.med_id = m.med_id
    '''
    cursor.execute(query)
    row = cursor.fetchone()
    conn.close()
    
    print("\n=== Sales Report ===")
    print(f"Total Purchases: {row[0]}")
    print(f"Total Revenue: ${row[1] if row[1] else 0:.2f}")
    return row

def get_most_popular_medicines():
    """Get the most purchased medicines"""
    conn = get_connection()
    cursor = conn.cursor()
    query = '''
        SELECT m.med_id, m.med_name, COUNT(*) as purchase_count
        FROM purchase p
        JOIN medicine m ON p.med_id = m.med_id
        GROUP BY m.med_id, m.med_name
        ORDER BY purchase_count DESC
    '''
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("No purchase data available.")
    else:
        print("\n=== Most Popular Medicines ===")
        print(f"{'Med ID':<10} {'Medicine Name':<20} {'Purchase Count'}")
        print("-" * 50)
        for row in rows:
            print(f"{row[0]:<10} {row[1]:<20} {row[2]}")
    return rows

# ==================== DEMO DATA ====================

def run_demo():
    """Run a complete demo with sample data"""
    print("=" * 60)
    print("PHARMACY DATABASE MANAGEMENT SYSTEM - DEMO")
    print("=" * 60)
    
    # 1. Add Locations
    print("\n\n1. ADDING LOCATIONS")
    print("-" * 40)
    add_location("LOC001", "New York")
    add_location("LOC002", "Los Angeles")
    add_location("LOC003", "Chicago")
    
    # 2. Add Pharmacies
    print("\n\n2. ADDING PHARMACIES")
    print("-" * 40)
    add_pharmacy("PH001", "City Pharmacy", "LOC001")
    add_pharmacy("PH002", "Health Plus", "LOC002")
    add_pharmacy("PH003", "MediCare", "LOC003")
    
    # 3. Add Medicines
    print("\n\n3. ADDING MEDICINES")
    print("-" * 40)
    add_medicine("MED001", "Paracetamol", 5.99, 500)
    add_medicine("MED002", "Ibuprofen", 7.50, 200)
    add_medicine("MED003", "Amoxicillin", 12.00, 250)
    add_medicine("MED004", "Aspirin", 4.25, 100)
    add_medicine("MED005", "Cetirizine", 8.75, 10)
    
    # 4. Add Customers
    print("\n\n4. ADDING CUSTOMERS")
    print("-" * 40)
    add_customer("CUST001", "John Doe", 30, "123 Main St, NY", "555-0101", "PH001")
    add_customer("CUST002", "Jane Smith", 25, "456 Oak Ave, LA", "555-0102", "PH002")
    add_customer("CUST003", "Bob Johnson", 45, "789 Pine Rd, Chicago", "555-0103", "PH003")
    
    # 5. Add Available Medicines
    print("\n\n5. ADDING MEDICINE AVAILABILITY")
    print("-" * 40)
    add_available("MED001", "PH001")
    add_available("MED002", "PH001")
    add_available("MED003", "PH002")
    add_available("MED004", "PH002")
    add_available("MED005", "PH003")
    
    # 6. Record Purchases
    print("\n\n6. RECORDING PURCHASES")
    print("-" * 40)
    add_purchase("MED001", "CUST001")
    add_purchase("MED002", "CUST001")
    add_purchase("MED003", "CUST002")
    add_purchase("MED004", "CUST002")
    add_purchase("MED005", "CUST003")
    
    print("\n\n" + "=" * 60)
    print("DEMO DATA INSERTED SUCCESSFULLY!")
    print("=" * 60)

def display_all_data():
    """Display all data in the database"""
    print("\n" + "=" * 60)
    display_locations()
    
    print("\n" + "=" * 60)
    display_pharmacies()
    
    print("\n" + "=" * 60)
    display_medicines()
    
    print("\n" + "=" * 60)
    display_customers()
    
    print("\n" + "=" * 60)
    display_available()
    
    print("\n" + "=" * 60)
    display_purchases()

def generate_reports():
    """Generate various reports"""
    print("\n" + "=" * 60)
    get_total_sales_report()
    
    print("\n" + "=" * 60)
    get_most_popular_medicines()
    
    print("\n" + "=" * 60)
    get_customer_purchase_history("CUST001")
    
    print("\n" + "=" * 60)
    get_pharmacy_inventory("PH001")
    
    print("\n" + "=" * 60)
    search_medicine_by_name("Par")

# ==================== INTERACTIVE MENU ====================

def show_menu():
    """Display interactive menu for the pharmacy database"""
    while True:
        print("\n" + "=" * 50)
        print("PHARMACY DATABASE MANAGEMENT SYSTEM")
        print("=" * 50)
        print("1. Location Management")
        print("2. Pharmacy Management")
        print("3. Medicine Management")
        print("4. Customer Management")
        print("5. Available Medicines")
        print("6. Purchase Management")
        print("7. Reports & Queries")
        print("8. Run Demo")
        print("9. Display All Data")
        print("10. Exit")
        
        choice = input("\nEnter your choice (1-10): ")
        
        if choice == '1':
            print("\n--- Location Management ---")
            print("1. Add Location")
            print("2. Display Locations")
            print("3. Delete Location")
            sub = input("Choose option: ")
            if sub == '1':
                loc_id = input("Enter Location ID: ")
                loc_name = input("Enter Location Name: ")
                add_location(loc_id, loc_name)
            elif sub == '2':
                display_locations()
            elif sub == '3':
                loc_id = input("Enter Location ID to delete: ")
                delete_location(loc_id)
                
        elif choice == '2':
            print("\n--- Pharmacy Management ---")
            print("1. Add Pharmacy")
            print("2. Display Pharmacies")
            print("3. Update Pharmacy")
            print("4. Delete Pharmacy")
            sub = input("Choose option: ")
            if sub == '1':
                ph_id = input("Enter Pharmacy ID: ")
                ph_name = input("Enter Pharmacy Name: ")
                loc_id = input("Enter Location ID: ")
                add_pharmacy(ph_id, ph_name, loc_id)
            elif sub == '2':
                display_pharmacies()
            elif sub == '3':
                ph_id = input("Enter Pharmacy ID: ")
                ph_name = input("Enter new Pharmacy Name (press Enter to skip): ")
                loc_id = input("Enter new Location ID (press Enter to skip): ")
                update_pharmacy(ph_id, ph_name or None, loc_id or None)
            elif sub == '4':
                ph_id = input("Enter Pharmacy ID to delete: ")
                delete_pharmacy(ph_id)
                
        elif choice == '3':
            print("\n--- Medicine Management ---")
            print("1. Add Medicine")
            print("2. Display Medicines")
            print("3. Update Medicine")
            print("4. Delete Medicine")
            sub = input("Choose option: ")
            if sub == '1':
                med_id = input("Enter Medicine ID: ")
                med_name = input("Enter Medicine Name: ")
                cost = input("Enter Cost: ")
                dosage = input("Enter Dosage (mg): ")
                add_medicine(med_id, med_name, cost, dosage)
            elif sub == '2':
                display_medicines()
            elif sub == '3':
                med_id = input("Enter Medicine ID: ")
                med_name = input("Enter new Medicine Name (press Enter to skip): ")
                cost = input("Enter new Cost (press Enter to skip): ")
                dosage = input("Enter new Dosage (press Enter to skip): ")
                update_medicine(med_id, med_name or None, cost or None, dosage or None)
            elif sub == '4':
                med_id = input("Enter Medicine ID to delete: ")
                delete_medicine(med_id)
                
        elif choice == '4':
            print("\n--- Customer Management ---")
            print("1. Add Customer")
            print("2. Display Customers")
            print("3. Update Customer")
            print("4. Delete Customer")
            sub = input("Choose option: ")
            if sub == '1':
                cust_id = input("Enter Customer ID: ")
                name = input("Enter Name: ")
                age = input("Enter Age: ")
                address = input("Enter Address: ")
                phone = input("Enter Phone: ")
                ph_id = input("Enter Pharmacy ID: ")
                add_customer(cust_id, name, age, address, phone, ph_id)
            elif sub == '2':
                display_customers()
            elif sub == '3':
                cust_id = input("Enter Customer ID: ")
                name = input("Enter new Name (press Enter to skip): ")
                age = input("Enter new Age (press Enter to skip): ")
                address = input("Enter new Address (press Enter to skip): ")
                phone = input("Enter new Phone (press Enter to skip): ")
                ph_id = input("Enter new Pharmacy ID (press Enter to skip): ")
                update_customer(cust_id, name or None, age or None, address or None, phone or None, ph_id or None)
            elif sub == '4':
                cust_id = input("Enter Customer ID to delete: ")
                delete_customer(cust_id)
                
        elif choice == '5':
            print("\n--- Available Medicines ---")
            print("1. Add Availability")
            print("2. Display Available Medicines")
            print("3. Delete Availability")
            sub = input("Choose option: ")
            if sub == '1':
                med_id = input("Enter Medicine ID: ")
                ph_id = input("Enter Pharmacy ID: ")
                add_available(med_id, ph_id)
            elif sub == '2':
                display_available()
            elif sub == '3':
                med_id = input("Enter Medicine ID: ")
                ph_id = input("Enter Pharmacy ID: ")
                delete_available(med_id, ph_id)
                
        elif choice == '6':
            print("\n--- Purchase Management ---")
            print("1. Add Purchase")
            print("2. Display Purchases")
            print("3. Delete Purchase")
            sub = input("Choose option: ")
            if sub == '1':
                med_id = input("Enter Medicine ID: ")
                cust_id = input("Enter Customer ID: ")
                add_purchase(med_id, cust_id)
            elif sub == '2':
                display_purchases()
            elif sub == '3':
                med_id = input("Enter Medicine ID: ")
                cust_id = input("Enter Customer ID: ")
                delete_purchase(med_id, cust_id)
                
        elif choice == '7':
            print("\n--- Reports & Queries ---")
            print("1. Search Medicine by Name")
            print("2. Customer Purchase History")
            print("3. Pharmacy Inventory")
            print("4. Total Sales Report")
            print("5. Most Popular Medicines")
            sub = input("Choose option: ")
            if sub == '1':
                name = input("Enter medicine name to search: ")
                search_medicine_by_name(name)
            elif sub == '2':
                cust_id = input("Enter Customer ID: ")
                get_customer_purchase_history(cust_id)
            elif sub == '3':
                ph_id = input("Enter Pharmacy ID: ")
                get_pharmacy_inventory(ph_id)
            elif sub == '4':
                get_total_sales_report()
            elif sub == '5':
                get_most_popular_medicines()
        
        elif choice == '8':
            run_demo()
        
        elif choice == '9':
            display_all_data()
                
        elif choice == '10':
            print("\nThank you for using Pharmacy Database Management System!")
            break
        else:
            print("Invalid choice! Please try again.")

# ==================== MAIN ====================

if __name__ == "__main__":
    # Initialize database
    init_database()

    # Show database connection information
    show_database_info()
    
    # Run demo automatically
    run_demo()
    
    # Display all data
    display_all_data()
    
    # Generate reports
    generate_reports()
    
    # Show final database info
    print("\n")
    show_database_info()
    
    # Optionally show interactive menu
    # show_menu()
