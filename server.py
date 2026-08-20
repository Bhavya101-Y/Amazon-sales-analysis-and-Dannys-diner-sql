import os
import sqlite3
import pandas as pd
from flask import Flask, jsonify, request, send_from_directory, render_template_string

app = Flask(__name__, template_folder='templates')

# Paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
AMAZON_CSV_PATH = os.path.join(BASE_DIR, 'Analyzing Amazon Sales data', 'Amazon Sales data.csv')
AMAZON_HTML_PATH = os.path.join(BASE_DIR, 'Analyzing Amazon Sales data', 'Analyzing Amazon Sales data.html')
DANNY_HTML_PATH = os.path.join(BASE_DIR, 'Case Study #1 - Danny\'s Diner', 'Case Study #1 - Danny\'s Diner.html')

# In-memory SQLite setup for Danny's Diner
def get_db_connection():
    conn = sqlite3.connect('file::memory:?cache=shared', uri=True, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_dannys_diner_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
    CREATE TABLE sales (
      customer_id VARCHAR(1),
      order_date DATE,
      product_id INTEGER
    );
    """)
    
    cursor.execute("""
    CREATE TABLE menu (
      product_id INTEGER,
      product_name VARCHAR(5),
      price INTEGER
    );
    """)
    
    cursor.execute("""
    CREATE TABLE members (
      customer_id VARCHAR(1),
      join_date DATE
    );
    """)
    
    # Insert data
    cursor.executemany("""
    INSERT INTO sales (customer_id, order_date, product_id) VALUES (?, ?, ?);
    """, [
      ('A', '2021-01-01', 1),
      ('A', '2021-01-01', 2),
      ('A', '2021-01-07', 2),
      ('A', '2021-01-10', 3),
      ('A', '2021-01-11', 3),
      ('A', '2021-01-11', 3),
      ('B', '2021-01-01', 2),
      ('B', '2021-01-02', 2),
      ('B', '2021-01-04', 1),
      ('B', '2021-01-11', 1),
      ('B', '2021-01-16', 3),
      ('B', '2021-02-01', 3),
      ('C', '2021-01-01', 3),
      ('C', '2021-01-01', 3),
      ('C', '2021-01-07', 3)
    ])
    
    cursor.executemany("""
    INSERT INTO menu (product_id, product_name, price) VALUES (?, ?, ?);
    """, [
      (1, 'sushi', 10),
      (2, 'curry', 15),
      (3, 'ramen', 12)
    ])
    
    cursor.executemany("""
    INSERT INTO members (customer_id, join_date) VALUES (?, ?);
    """, [
      ('A', '2021-01-07'),
      ('B', '2021-01-09')
    ])
    
    conn.commit()
    return conn

# Cache connection in memory
db_conn = init_dannys_diner_db()

@app.route('/')
def index():
    try:
        with open(os.path.join(BASE_DIR, 'templates', 'index.html'), 'r', encoding='utf-8') as f:
            content = f.read()
        return render_template_string(content)
    except Exception as e:
        return f"Error loading index template: {str(e)}", 500

@app.route('/notebooks/amazon')
def view_amazon_notebook():
    directory = os.path.dirname(AMAZON_HTML_PATH)
    filename = os.path.basename(AMAZON_HTML_PATH)
    return send_from_directory(directory, filename)

@app.route('/notebooks/dannys_diner')
def view_danny_notebook():
    directory = os.path.dirname(DANNY_HTML_PATH)
    filename = os.path.basename(DANNY_HTML_PATH)
    return send_from_directory(directory, filename)

@app.route('/api/amazon_sales')
def get_amazon_sales_data():
    try:
        if not os.path.exists(AMAZON_CSV_PATH):
            return jsonify({'error': 'Amazon Sales CSV file not found'}), 404
        
        df = pd.read_csv(AMAZON_CSV_PATH)
        
        # Clean numeric cols
        df['Units Sold'] = pd.to_numeric(df['Units Sold'], errors='coerce')
        df['Total Revenue'] = pd.to_numeric(df['Total Revenue'], errors='coerce')
        df['Total Profit'] = pd.to_numeric(df['Total Profit'], errors='coerce')
        df['Total Cost'] = pd.to_numeric(df['Total Cost'], errors='coerce')
        
        # Parse Dates
        df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
        df = df.dropna(subset=['Total Revenue', 'Total Profit', 'Order Date'])
        
        # Calculate Key Metrics
        total_revenue = float(df['Total Revenue'].sum())
        total_profit = float(df['Total Profit'].sum())
        total_cost = float(df['Total Cost'].sum())
        units_sold = int(df['Units Sold'].sum())
        avg_order_value = float(df['Total Revenue'].mean())
        profit_margin = (total_profit / total_revenue) * 100 if total_revenue > 0 else 0
        
        # Sales Channel Comparison
        channel_data = df.groupby('Sales Channel')['Total Revenue'].sum().to_dict()
        channel_list = [{'channel': k, 'revenue': float(v)} for k, v in channel_data.items()]
        
        # Sales by Region
        region_data = df.groupby('Region')['Total Revenue'].sum().sort_values(ascending=False).to_dict()
        region_list = [{'region': k, 'revenue': float(v)} for k, v in region_data.items()]
        
        # Sales by Item Type
        item_data = df.groupby('Item Type')['Total Revenue'].sum().sort_values(ascending=False).to_dict()
        item_list = [{'item_type': k, 'revenue': float(v)} for k, v in item_data.items()]
        
        # Monthly Sales Trend
        df_sorted = df.sort_values('Order Date')
        df_sorted['YearMonth'] = df_sorted['Order Date'].dt.to_period('M').astype(str)
        monthly_data = df_sorted.groupby('YearMonth').agg({
            'Total Revenue': 'sum',
            'Total Profit': 'sum'
        }).reset_index()
        
        monthly_list = []
        for _, row in monthly_data.iterrows():
            monthly_list.append({
                'month': row['YearMonth'],
                'revenue': float(row['Total Revenue']),
                'profit': float(row['Total Profit'])
            })
            
        return jsonify({
            'metrics': {
                'total_revenue': total_revenue,
                'total_profit': total_profit,
                'total_cost': total_cost,
                'units_sold': units_sold,
                'avg_order_value': avg_order_value,
                'profit_margin': profit_margin
            },
            'channels': channel_list,
            'regions': region_list,
            'item_types': item_list,
            'monthly_trend': monthly_list
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dannys_diner/query', methods=['POST'])
def run_danny_query():
    data = request.json or {}
    sql_query = data.get('query', '')
    
    if not sql_query:
        return jsonify({'error': 'No query provided'}), 400
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        row_dicts = [dict(row) for row in rows]
        conn.close()
        
        return jsonify({
            'columns': columns,
            'rows': row_dicts
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/dannys_diner/questions')
def get_danny_questions():
    questions = [
        {
            'id': 1,
            'title': '1. Total Amount Spent',
            'desc': 'What is the total amount each customer spent at the restaurant?',
            'sql': '-- 1. What is the total amount each customer spent at the restaurant?\\nSELECT s.customer_id, SUM(m.price) as total_amount_spent\\nFROM sales as s\\nJOIN menu as m ON s.product_id = m.product_id\\nGROUP BY s.customer_id;'
        },
        {
            'id': 2,
            'title': '2. Visitor Days',
            'desc': 'How many days has each customer visited the restaurant?',
            'sql': '-- 2. How many days has each customer visited the restaurant?\\nSELECT customer_id, COUNT(DISTINCT order_date) as visit_days\\nFROM sales\\nGROUP BY customer_id;'
        },
        {
            'id': 3,
            'title': '3. First Purchased Item',
            'desc': 'What was the first item from the menu purchased by each customer?',
            'sql': '-- 3. What was the first item from the menu purchased by each customer?\\nWITH ranked_sales AS (\\n  SELECT s.customer_id, s.order_date, m.product_name,\\n         ROW_NUMBER() OVER (PARTITION BY s.customer_id ORDER BY s.order_date ASC) as rn\\n  FROM sales s\\n  JOIN menu m ON s.product_id = m.product_id\\n)\\nSELECT customer_id, order_date, product_name \\nFROM ranked_sales \\nWHERE rn = 1;'
        },
        {
            'id': 4,
            'title': '4. Most Purchased Item',
            'desc': 'What is the most purchased item on the menu and how many times was it purchased by all customers?',
            'sql': '-- 4. What is the most purchased item on the menu and how many times was it purchased?\\nSELECT m.product_name, COUNT(*) as purchase_count\\nFROM sales as s\\nJOIN menu as m ON s.product_id = m.product_id\\nGROUP BY m.product_name\\nORDER BY purchase_count DESC\\nLIMIT 1;'
        },
        {
            'id': 5,
            'title': '5. Most Popular Item per Customer',
            'desc': 'Which item was the most popular for each customer?',
            'sql': '-- 5. Which item was the most popular for each customer?\\nWITH customer_popularity AS (\\n  SELECT s.customer_id, m.product_name, COUNT(*) as order_count,\\n         DENSE_RANK() OVER (PARTITION BY s.customer_id ORDER BY COUNT(*) DESC) as rank\\n  FROM sales s\\n  JOIN menu m ON s.product_id = m.product_id\\n  GROUP BY s.customer_id, m.product_name\\n)\\nSELECT customer_id, product_name, order_count \\nFROM customer_popularity \\nWHERE rank = 1;'
        },
        {
            'id': 6,
            'title': '6. First Purchase as Member',
            'desc': 'Which item was purchased first by the customer after they became a member?',
            'sql': '-- 6. Which item was purchased first by the customer after they became a member?\\nWITH member_purchases AS (\\n  SELECT s.customer_id, s.order_date, m.product_name,\\n         ROW_NUMBER() OVER (PARTITION BY s.customer_id ORDER BY s.order_date ASC) as rn\\n  FROM sales s\\n  JOIN menu m ON s.product_id = m.product_id\\n  JOIN members mem ON s.customer_id = mem.customer_id\\n  WHERE s.order_date >= mem.join_date\\n)\\nSELECT customer_id, order_date, product_name \\nFROM member_purchases \\nWHERE rn = 1;'
        },
        {
            'id': 7,
            'title': '7. Purchase Just Before Membership',
            'desc': 'Which item was purchased just before the customer became a member?',
            'sql': '-- 7. Which item was purchased just before the customer became a member?\\nWITH pre_member_purchases AS (\\n  SELECT s.customer_id, s.order_date, m.product_name,\\n         ROW_NUMBER() OVER (PARTITION BY s.customer_id ORDER BY s.order_date DESC) as rn\\n  FROM sales s\\n  JOIN menu m ON s.product_id = m.product_id\\n  JOIN members mem ON s.customer_id = mem.customer_id\\n  WHERE s.order_date < mem.join_date\\n)\\nSELECT customer_id, order_date, product_name \\nFROM pre_member_purchases \\nWHERE rn = 1;'
        },
        {
            'id': 8,
            'title': '8. Pre-membership Spending',
            'desc': 'What is the total items and amount spent for each member before they became a member?',
            'sql': '-- 8. What is the total items and amount spent for each member before they became a member?\\nSELECT s.customer_id, COUNT(s.product_id) AS total_items, SUM(m.price) AS total_amount_spent\\nFROM sales AS s\\nJOIN menu AS m ON s.product_id = m.product_id\\nJOIN members AS mem ON s.customer_id = mem.customer_id\\nWHERE s.order_date < mem.join_date\\nGROUP BY s.customer_id;'
        },
        {
            'id': 9,
            'title': '9. Customer Points Calculations',
            'desc': 'If each $1 spent equates to 10 points and sushi has a 2x points multiplier - how many points would each customer have?',
            'sql': '-- 9. Points system: $1 spent = 10 pts, sushi = 20 pts per $1\\nSELECT s.customer_id,\\n       SUM(CASE WHEN m.product_name = \'sushi\' THEN m.price * 20 ELSE m.price * 10 END) as total_points\\nFROM sales AS s\\nJOIN menu AS m ON s.product_id = m.product_id\\nGROUP BY s.customer_id;'
        },
        {
            'id': 10,
            'title': '10. First Week Double Points Promo',
            'desc': 'In the first week after a customer joins the program (including their join date) they earn 2x points on all items, not just sushi - how many points do customer A and B have at the end of January?',
            'sql': '-- 10. First week promo: 2x points on all items, valid through Jan 2021\\nSELECT s.customer_id,\\n       SUM(CASE \\n             WHEN s.order_date BETWEEN mem.join_date AND date(mem.join_date, \'+6 days\') THEN m.price * 20\\n             WHEN m.product_name = \'sushi\' THEN m.price * 20\\n             ELSE m.price * 10\\n           END) as total_points\\nFROM sales AS s\\nJOIN menu AS m ON s.product_id = m.product_id\\nJOIN members AS mem ON s.customer_id = mem.customer_id\\nWHERE s.order_date <= \'2021-01-31\'\\nGROUP BY s.customer_id;'
        }
    ]
    return jsonify(questions)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
