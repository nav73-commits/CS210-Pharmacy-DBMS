# Pharmacy Database Management System

A full-stack web application designed for managing pharmacy operations with integrated data science analytics.

## 🚀 Overview

This project provides a comprehensive solution for pharmacies to track locations, medicines, customers, and purchase history. Beyond basic CRUD operations, it features an **Advanced Analytics Dashboard** that provides data-driven insights into revenue trends, customer segmentation, and inventory performance.

## 📊 Key Features

- **Full CRUD Management**: Handle Locations, Pharmacies, Medicines, and Customers.
- **Inventory Tracking**: Monitor medicine availability across different pharmacy branches.
- **Advanced Analytics Dashboard**: 
    - **Revenue Analysis**: Track which pharmacies lead in sales.
    - **Sales Trends**: Visualize monthly growth and unit sales.
    - **Customer Segmentation**: Categorize customers into High, Medium, and Low-value tiers based on spending.
    - **Price-Demand Correlation**: Analyze if price impacts purchase frequency using bubble charts.
    - **Inventory Coverage**: Monitor how much of the medicine catalog each pharmacy carries.
- **Dual Interface**: Fully functional Web UI (Flask) and a command-line interface (CLI).

## 🛠️ Tech Stack

- **Backend**: Python 3.11 + Flask
- **Database**: SQLite3 (Relational)
- **Frontend**: HTML5, CSS3, Jinja2 Templates
- **Data Visualization**: Chart.js
- **Environment**: Windows/MacOS/Linux

## ⚙️ Installation & Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize Database**:
   ```bash
   python pharmacy_database.py
   ```

3. **Run Database Migration (for analytics data)**:
   ```bash
   python migrate_db.py
   ```

4. **Run the Application**:
   ```bash
   python app.py
   ```
   Open your browser and navigate to `http://127.0.0.1:5000`

## 📂 Project Structure

- `app.py`: Main Flask application and analytical routes.
- `pharmacy_database.py`: Database schema definition and CLI module.
- `migrate_db.py`: Migration script for enhanced analytical fields.
- `templates/`: HTML templates for the web interface.
- `pharmacy_database.db`: The SQLite database file.

## 🎓 Academic Alignment (CS 210)

This project aligns with CS 210 (Data Management for Data Science) criteria by implementing:
- **Relational Integrity**: 3rd Normal Form (3NF) normalization.
- **Junction Tables**: Resolving Many-to-Many relationships between Customers/Medicines and Pharmacies/Medicines.
- **Analytical Insights**: Using SQL aggregation, JOINs, and subqueries to drive business intelligence.
- **Visualization**: Clear communication of data patterns through interactive charts.
