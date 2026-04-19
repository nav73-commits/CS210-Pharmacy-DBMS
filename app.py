#!/usr/bin/env python3
"""
Pharmacy Database - Web Frontend
Flask-based web application for managing pharmacy data
"""

from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'pharmacy_secret_key'

DB_PATH = 'pharmacy_database.db'

def get_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ==================== HOME ====================
@app.route('/')
def home():
    """Home page with dashboard"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get counts
    stats = {}
    cursor.execute("SELECT COUNT(*) FROM location")
    stats['locations'] = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM pharmacy")
    stats['pharmacies'] = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM medicine")
    stats['medicines'] = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM customer")
    stats['customers'] = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM purchase")
    stats['purchases'] = cursor.fetchone()[0]
    
    # Get total revenue
    cursor.execute("SELECT SUM(m.cost) FROM purchase p JOIN medicine m ON p.med_id = m.med_id")
    result = cursor.fetchone()[0]
    stats['revenue'] = result if result else 0
    # Get low stock count
    cursor.execute("SELECT COUNT(*) FROM available WHERE stock_quantity < 20")
    stats['low_stock'] = cursor.fetchone()[0]
    
    conn.close()
    return render_template('index.html', stats=stats)

# ==================== LOCATIONS ====================
@app.route('/locations')
def locations():
    """Display all locations"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM location")
    locations = cursor.fetchall()
    conn.close()
    return render_template('locations.html', locations=locations)

@app.route('/locations/add', methods=['POST'])
def add_location():
    """Add a new location"""
    location_id = request.form['location_id']
    location_name = request.form['location_name']
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO location VALUES (?, ?)", (location_id, location_name))
        conn.commit()
        flash('Location added successfully!', 'success')
    except sqlite3.IntegrityError:
        flash('Location ID already exists!', 'error')
    finally:
        conn.close()
    return redirect(url_for('locations'))

@app.route('/locations/delete/<location_id>')
def delete_location(location_id):
    """Delete a location"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM location WHERE location_id = ?", (location_id,))
    conn.commit()
    conn.close()
    flash('Location deleted successfully!', 'success')
    return redirect(url_for('locations'))

# ==================== PHARMACIES ====================
@app.route('/pharmacies')
def pharmacies():
    """Display all pharmacies"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.*, l.location_name 
        FROM pharmacy p 
        LEFT JOIN location l ON p.location_id = l.location_id
    ''')
    pharmacies = cursor.fetchall()
    cursor.execute("SELECT * FROM location")
    locations = cursor.fetchall()
    conn.close()
    return render_template('pharmacies.html', pharmacies=pharmacies, locations=locations)

@app.route('/pharmacies/add', methods=['POST'])
def add_pharmacy():
    """Add a new pharmacy"""
    pharmacy_id = request.form['pharmacy_id']
    pharmacy_name = request.form['pharmacy_name']
    location_id = request.form['location_id']
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO pharmacy VALUES (?, ?, ?)", 
                      (pharmacy_id, pharmacy_name, location_id))
        conn.commit()
        flash('Pharmacy added successfully!', 'success')
    except sqlite3.IntegrityError:
        flash('Pharmacy ID already exists!', 'error')
    finally:
        conn.close()
    return redirect(url_for('pharmacies'))

@app.route('/pharmacies/delete/<pharmacy_id>')
def delete_pharmacy(pharmacy_id):
    """Delete a pharmacy"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pharmacy WHERE pharmacy_id = ?", (pharmacy_id,))
    conn.commit()
    conn.close()
    flash('Pharmacy deleted successfully!', 'success')
    return redirect(url_for('pharmacies'))

@app.route('/pharmacies/update/<pharmacy_id>', methods=['POST'])
def update_pharmacy(pharmacy_id):
    """Update a pharmacy"""
    pharmacy_name = request.form.get('pharmacy_name')
    location_id = request.form.get('location_id')
    
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
        cursor.execute(f"UPDATE pharmacy SET {', '.join(updates)} WHERE pharmacy_id = ?", values)
        conn.commit()
        flash('Pharmacy updated successfully!', 'success')
    conn.close()
    return redirect(url_for('pharmacies'))

# ==================== MEDICINES ====================
@app.route('/medicines')
def medicines():
    """Display all medicines"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicine")
    medicines = cursor.fetchall()
    conn.close()
    return render_template('medicines.html', medicines=medicines)

@app.route('/medicines/add', methods=['POST'])
def add_medicine():
    """Add a new medicine"""
    med_id = request.form['med_id']
    med_name = request.form['med_name']
    cost = request.form['cost']
    dosage_mg = request.form['dosage_mg']
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO medicine VALUES (?, ?, ?, ?)", 
                      (med_id, med_name, float(cost), int(dosage_mg)))
        conn.commit()
        flash('Medicine added successfully!', 'success')
    except sqlite3.IntegrityError:
        flash('Medicine ID already exists!', 'error')
    finally:
        conn.close()
    return redirect(url_for('medicines'))

@app.route('/medicines/delete/<med_id>')
def delete_medicine(med_id):
    """Delete a medicine"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM medicine WHERE med_id = ?", (med_id,))
    conn.commit()
    conn.close()
    flash('Medicine deleted successfully!', 'success')
    return redirect(url_for('medicines'))

@app.route('/medicines/update/<med_id>', methods=['POST'])
def update_medicine(med_id):
    """Update a medicine"""
    med_name = request.form.get('med_name')
    cost = request.form.get('cost')
    dosage_mg = request.form.get('dosage_mg')
    
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
        cursor.execute(f"UPDATE medicine SET {', '.join(updates)} WHERE med_id = ?", values)
        conn.commit()
        flash('Medicine updated successfully!', 'success')
    conn.close()
    return redirect(url_for('medicines'))

# ==================== CUSTOMERS ====================
@app.route('/customers')
def customers():
    """Display all customers"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.*, p.pharmacy_name 
        FROM customer c 
        LEFT JOIN pharmacy p ON c.pharmacy_id = p.pharmacy_id
    ''')
    customers = cursor.fetchall()
    cursor.execute("SELECT * FROM pharmacy")
    pharmacies = cursor.fetchall()
    conn.close()
    return render_template('customers.html', customers=customers, pharmacies=pharmacies)

@app.route('/customers/add', methods=['POST'])
def add_customer():
    """Add a new customer"""
    cust_id = request.form['cust_id']
    name = request.form['name']
    age = request.form['age']
    address = request.form['address']
    phone = request.form['phone']
    pharmacy_id = request.form['pharmacy_id']
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO customer VALUES (?, ?, ?, ?, ?, ?)", 
                      (cust_id, name, int(age), address, phone, pharmacy_id))
        conn.commit()
        flash('Customer added successfully!', 'success')
    except sqlite3.IntegrityError:
        flash('Customer ID already exists!', 'error')
    finally:
        conn.close()
    return redirect(url_for('customers'))

@app.route('/customers/delete/<cust_id>')
def delete_customer(cust_id):
    """Delete a customer"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customer WHERE cust_id = ?", (cust_id,))
    conn.commit()
    conn.close()
    flash('Customer deleted successfully!', 'success')
    return redirect(url_for('customers'))

@app.route('/customers/update/<cust_id>', methods=['POST'])
def update_customer(cust_id):
    """Update a customer"""
    name = request.form.get('name')
    age = request.form.get('age')
    address = request.form.get('address')
    phone = request.form.get('phone')
    pharmacy_id = request.form.get('pharmacy_id')
    
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
        cursor.execute(f"UPDATE customer SET {', '.join(updates)} WHERE cust_id = ?", values)
        conn.commit()
        flash('Customer updated successfully!', 'success')
    conn.close()
    return redirect(url_for('customers'))

# ==================== AVAILABLE MEDICINES ====================
@app.route('/available')
def available():
    """Display available medicines at pharmacies"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.*, m.med_name, p.pharmacy_name
        FROM available a
        JOIN medicine m ON a.med_id = m.med_id
        JOIN pharmacy p ON a.pharmacy_id = p.pharmacy_id
    ''')
    available = cursor.fetchall()
    cursor.execute("SELECT * FROM medicine")
    medicines = cursor.fetchall()
    cursor.execute("SELECT * FROM pharmacy")
    pharmacies = cursor.fetchall()
    conn.close()
    return render_template('available.html', available=available, medicines=medicines, pharmacies=pharmacies)

@app.route('/available/add', methods=['POST'])
def add_available():
    """Add medicine availability"""
    med_id = request.form['med_id']
    pharmacy_id = request.form['pharmacy_id']
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO available VALUES (?, ?)", (med_id, pharmacy_id))
        conn.commit()
        flash('Availability added successfully!', 'success')
    except sqlite3.IntegrityError:
        flash('This availability record already exists!', 'error')
    finally:
        conn.close()
    return redirect(url_for('available'))

@app.route('/available/delete/<med_id>/<pharmacy_id>')
def delete_available(med_id, pharmacy_id):
    """Delete availability"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM available WHERE med_id = ? AND pharmacy_id = ?", 
                   (med_id, pharmacy_id))
    conn.commit()
    conn.close()
    flash('Availability deleted successfully!', 'success')
    return redirect(url_for('available'))

# ==================== PURCHASES ====================
@app.route('/purchases')
def purchases():
    """Display all purchases"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.*, m.med_name, m.cost, c.name as customer_name
        FROM purchase p
        JOIN medicine m ON p.med_id = m.med_id
        JOIN customer c ON p.cust_id = c.cust_id
    ''')
    purchases = cursor.fetchall()
    cursor.execute("SELECT * FROM medicine")
    medicines = cursor.fetchall()
    cursor.execute("SELECT * FROM customer")
    customers = cursor.fetchall()
    conn.close()
    return render_template('purchases.html', purchases=purchases, medicines=medicines, customers=customers)

@app.route('/purchases/add', methods=['POST'])
def add_purchase():
    """Add a purchase"""
    med_id = request.form['med_id']
    cust_id = request.form['cust_id']
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO purchase VALUES (?, ?)", (med_id, cust_id))
        conn.commit()
        flash('Purchase recorded successfully!', 'success')
    except sqlite3.IntegrityError:
        flash('This purchase record already exists!', 'error')
    finally:
        conn.close()
    return redirect(url_for('purchases'))

@app.route('/purchases/delete/<med_id>/<cust_id>')
def delete_purchase(med_id, cust_id):
    """Delete a purchase"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM purchase WHERE med_id = ? AND cust_id = ?", 
                   (med_id, cust_id))
    conn.commit()
    conn.close()
    flash('Purchase deleted successfully!', 'success')
    return redirect(url_for('purchases'))

# ==================== REPORTS ====================
@app.route('/reports')
def reports():
    """Display reports"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Sales report
    cursor.execute('''
        SELECT COUNT(*) as total_purchases, SUM(m.cost) as total_revenue
        FROM purchase p
        JOIN medicine m ON p.med_id = m.med_id
    ''')
    sales = cursor.fetchone()
    
    # Popular medicines
    cursor.execute('''
        SELECT m.med_id, m.med_name, COUNT(*) as purchase_count
        FROM purchase p
        JOIN medicine m ON p.med_id = m.med_id
        GROUP BY m.med_id, m.med_name
        ORDER BY purchase_count DESC
    ''')
    popular = cursor.fetchall()
    
    # Customer spending
    cursor.execute('''
        SELECT c.cust_id, c.name, COUNT(*) as purchase_count, SUM(m.cost) as total_spent
        FROM purchase p
        JOIN customer c ON p.cust_id = c.cust_id
        JOIN medicine m ON p.med_id = m.med_id
        GROUP BY c.cust_id, c.name
        ORDER BY total_spent DESC
    ''')
    customer_spending = cursor.fetchall()
    
    conn.close()
    return render_template('reports.html', sales=sales, popular=popular, customer_spending=customer_spending)

# ==================== ANALYTICS DASHBOARD ====================
@app.route('/analytics')
def analytics():
    """Advanced analytics dashboard with data-driven insights"""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Revenue by Pharmacy
    cursor.execute('''
        SELECT ph.pharmacy_name, 
               COALESCE(SUM(p.total_cost), 0) as revenue,
               COUNT(p.purchase_id) as purchase_count
        FROM pharmacy ph
        LEFT JOIN customer c ON c.pharmacy_id = ph.pharmacy_id
        LEFT JOIN purchase p ON p.cust_id = c.cust_id
        GROUP BY ph.pharmacy_id, ph.pharmacy_name
        ORDER BY revenue DESC
    ''')
    revenue_by_pharmacy = [dict(row) for row in cursor.fetchall()]

    total_revenue = sum(r['revenue'] for r in revenue_by_pharmacy)
    for r in revenue_by_pharmacy:
        r['pct'] = round((r['revenue'] / total_revenue * 100), 1) if total_revenue > 0 else 0

    # 2. Top Medicines by Sales Volume (quantity sold)
    cursor.execute('''
        SELECT m.med_name, m.cost, 
               SUM(p.quantity) as units_sold,
               SUM(p.total_cost) as total_revenue
        FROM purchase p
        JOIN medicine m ON p.med_id = m.med_id
        GROUP BY m.med_id, m.med_name, m.cost
        ORDER BY units_sold DESC
    ''')
    medicine_sales = [dict(row) for row in cursor.fetchall()]

    # 3. Customer Segmentation by Spending
    cursor.execute('''
        SELECT c.cust_id, c.name, c.age,
               COUNT(p.purchase_id) as purchase_count,
               COALESCE(SUM(p.total_cost), 0) as total_spent,
               COALESCE(AVG(p.total_cost), 0) as avg_order_value
        FROM customer c
        LEFT JOIN purchase p ON c.cust_id = p.cust_id
        GROUP BY c.cust_id, c.name, c.age
        ORDER BY total_spent DESC
    ''')
    customer_data = [dict(row) for row in cursor.fetchall()]
    
    # Assign spending tiers
    if customer_data:
        max_spent = max(c['total_spent'] for c in customer_data) if customer_data else 1
        for c in customer_data:
            ratio = c['total_spent'] / max_spent if max_spent > 0 else 0
            if ratio >= 0.66:
                c['tier'] = 'High Value'
            elif ratio >= 0.33:
                c['tier'] = 'Medium Value'
            else:
                c['tier'] = 'Low Value'
            c['avg_order_value'] = round(c['avg_order_value'], 2)

    # 4. Monthly Purchase Trends
    cursor.execute('''
        SELECT strftime('%Y-%m', purchase_date) as month,
               COUNT(*) as num_purchases,
               SUM(quantity) as units_sold,
               SUM(total_cost) as monthly_revenue
        FROM purchase
        WHERE purchase_date IS NOT NULL
        GROUP BY month
        ORDER BY month
    ''')
    monthly_trends = [dict(row) for row in cursor.fetchall()]

    # Calculate month-over-month growth
    for i in range(1, len(monthly_trends)):
        prev = monthly_trends[i-1]['monthly_revenue']
        curr = monthly_trends[i]['monthly_revenue']
        if prev > 0:
            monthly_trends[i]['growth_pct'] = round(((curr - prev) / prev) * 100, 1)
        else:
            monthly_trends[i]['growth_pct'] = 0
    if monthly_trends:
        monthly_trends[0]['growth_pct'] = 0

    # 5. Medicine Price vs Purchase Frequency (for scatter plot)
    cursor.execute('''
        SELECT m.med_id, m.med_name, m.cost, m.dosage_mg,
               COUNT(p.purchase_id) as times_purchased,
               SUM(p.quantity) as total_units
        FROM medicine m
        LEFT JOIN purchase p ON m.med_id = p.med_id
        GROUP BY m.med_id, m.med_name, m.cost, m.dosage_mg
    ''')
    price_vs_demand = [dict(row) for row in cursor.fetchall()]

    # 6. Pharmacy Inventory Coverage
    cursor.execute('SELECT COUNT(*) FROM medicine')
    total_medicines = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT ph.pharmacy_name,
               COUNT(a.med_id) as medicines_stocked,
               COALESCE(SUM(a.stock_quantity), 0) as total_stock
        FROM pharmacy ph
        LEFT JOIN available a ON ph.pharmacy_id = a.pharmacy_id
        GROUP BY ph.pharmacy_id, ph.pharmacy_name
    ''')
    inventory_coverage = [dict(row) for row in cursor.fetchall()]
    for item in inventory_coverage:
        item['coverage_pct'] = round((item['medicines_stocked'] / total_medicines * 100), 1) if total_medicines > 0 else 0
        item['not_stocked'] = total_medicines - item['medicines_stocked']

    # 7. Key Summary Metrics
    cursor.execute('SELECT COUNT(*) FROM purchase')
    total_purchases = cursor.fetchone()[0]
    cursor.execute('SELECT SUM(total_cost) FROM purchase')
    total_rev = cursor.fetchone()[0] or 0
    cursor.execute('SELECT AVG(total_cost) FROM purchase')
    avg_order = cursor.fetchone()[0] or 0
    cursor.execute('SELECT SUM(quantity) FROM purchase')
    total_units = cursor.fetchone()[0] or 0

    summary = {
        'total_purchases': total_purchases,
        'total_revenue': round(total_rev, 2),
        'avg_order_value': round(avg_order, 2),
        'total_units_sold': total_units,
        'total_medicines': total_medicines,
        'total_customers': len(customer_data),
    }

    # 8. Auto-generated Insights
    insights = []
    if medicine_sales:
        top_med = medicine_sales[0]
        insights.append(f"{top_med['med_name']} is the best-selling medicine with {top_med['units_sold']} units sold, generating ${top_med['total_revenue']:.2f} in revenue.")
    if revenue_by_pharmacy:
        top_ph = revenue_by_pharmacy[0]
        insights.append(f"{top_ph['pharmacy_name']} leads in revenue at ${top_ph['revenue']:.2f} ({top_ph['pct']}% of total).")
    if customer_data:
        top_cust = customer_data[0]
        insights.append(f"{top_cust['name']} is the highest-spending customer at ${top_cust['total_spent']:.2f} across {top_cust['purchase_count']} purchases.")
    if monthly_trends and len(monthly_trends) >= 2:
        latest = monthly_trends[-1]
        insights.append(f"Latest month ({latest['month']}) saw ${latest['monthly_revenue']:.2f} in revenue with {latest['growth_pct']:+.1f}% growth.")
    
    # 9. Low Stock Alerts
    cursor.execute('''
        SELECT m.med_name, ph.pharmacy_name, a.stock_quantity
        FROM available a
        JOIN medicine m ON a.med_id = m.med_id
        JOIN pharmacy ph ON a.pharmacy_id = ph.pharmacy_id
        WHERE a.stock_quantity < 20
        ORDER BY a.stock_quantity ASC
    ''')
    low_stock_alerts = [dict(row) for row in cursor.fetchall()]
    if low_stock_alerts:
        insights.append(f"INVENTORY ALERT: {len(low_stock_alerts)} items are below the safety threshold (20 units).")

    conn.close()

    return render_template('analytics.html',
        revenue_by_pharmacy=revenue_by_pharmacy,
        medicine_sales=medicine_sales,
        customer_data=customer_data,
        monthly_trends=monthly_trends,
        price_vs_demand=price_vs_demand,
        inventory_coverage=inventory_coverage,
        summary=summary,
        insights=insights,
        low_stock_alerts=low_stock_alerts
    )

if __name__ == '__main__':
    print("Starting Pharmacy Database Web Application...")
    print("Open your browser and go to: http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)

