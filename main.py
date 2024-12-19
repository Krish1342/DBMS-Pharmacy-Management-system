import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from datetime import datetime

# MySQL Database Configuration
host = "localhost"
user = "root"
password = "Password"
database = "drugdatabase"

# Connect to the MySQL database
try:
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    c = conn.cursor()
except mysql.connector.Error as err:
    print(f"Error connecting to database: {err}")
    exit(1)

# Global variable to store current user
current_user = None

# Function to validate login credentials
def validate_login():
    global current_user
    username = entry_username.get()
    password = entry_password.get()

    # Fetch credentials and admin flag
    c.execute('SELECT uid, pass, is_admin FROM customer WHERE uid = %s AND pass = %s', (username, password))
    result = c.fetchone()

    if result:
        current_user = {"uid": result[0], "type": "admin" if result[2] else "user"}
        messagebox.showinfo("Login", f"{'Admin' if result[2] else 'User'} Login Successful")
        show_main_interface()
    else:
        messagebox.showerror("Login", "Invalid credentials")

# Function to show the main interface after login
def show_main_interface():
    login_frame.pack_forget()  # Hide login frame
    main_frame.pack(padx=20, pady=20)  # Show main frame

    for widget in main_frame.winfo_children():
        widget.destroy()

    heading = tk.Label(main_frame, text="Pharmacy Management", font=("Helvetica", 20))
    heading.pack(pady=10)

    label_welcome = tk.Label(main_frame, text=f"Welcome, {'Admin' if current_user['type'] == 'admin' else 'User'}", font=("Helvetica", 16))
    label_welcome.pack(pady=10)

    if current_user['type'] == 'admin':
        tk.Button(main_frame, text="Add Customer", command=add_customer).pack(pady=5)
        tk.Button(main_frame, text="View Customers", command=view_customers).pack(pady=5)
        tk.Button(main_frame, text="Add Product", command=add_product).pack(pady=5)
        tk.Button(main_frame, text="Update Product", command=update_product).pack(pady=5)
        tk.Button(main_frame, text="Check Inventory", command=check_inventory).pack(pady=5)
        tk.Button(main_frame, text="View All Orders", command=view_all_orders).pack(pady=5)
        tk.Button(main_frame, text="Generate Low Stock Report", command=generate_low_stock_report).pack(pady=5)
    else:
        tk.Button(main_frame, text="Add Order", command=lambda: add_order_for_user(current_user['uid'])).pack(pady=5)
        tk.Button(main_frame, text="View My Orders", command=view_my_orders).pack(pady=5)

    tk.Button(main_frame, text="Logout", command=logout).pack(pady=5)
def update_product():
    def save_updated_product():
        product_id = entry_product_id.get()
        new_price = entry_price.get()

        if not product_id or not new_price:
            messagebox.showerror("Error", "Product ID and Price must be filled out.")
            return
        

        try:
            # Fetch the current price to log in price_history
            c.execute("SELECT price FROM product WHERE pid = %s", (product_id,))
            current_price = c.fetchone()

            if current_price:
                current_price = current_price[0]
                # Update the product price
                c.execute("UPDATE product SET price = %s WHERE pid = %s", (new_price, product_id))
                conn.commit()
                
             
                c.execute("""
                    INSERT INTO price_history (pid, old_price, new_price)
                    VALUES (%s, %s, %s)
                """, (product_id, current_price, new_price))
                conn.commit()

                messagebox.showinfo("Success", "Product updated successfully!")
                update_product_window.destroy()
            else:
                messagebox.showerror("Error", "Product not found.")

        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to update product: {err}")

    # Create a new window for updating a product
    update_product_window = tk.Toplevel(root)
    update_product_window.title("Update Product")
    update_product_window.geometry("400x300")

    tk.Label(update_product_window, text="Product ID:").pack(pady=5)
    entry_product_id = tk.Entry(update_product_window)
    entry_product_id.pack(pady=5)

    tk.Label(update_product_window, text="New Price:").pack(pady=5)
    entry_price = tk.Entry(update_product_window)
    entry_price.pack(pady=5)

    tk.Button(update_product_window, text="Update Product", command=save_updated_product).pack(pady=10)


# Function to add a customer (admin only)
def add_customer():
    def save_customer():
        uid = entry_uid.get()
        password = entry_password.get()
        fname = entry_fname.get()
        lname = entry_lname.get()
        email = entry_email.get()
        address = entry_address.get()
        phno = entry_phno.get()
        is_admin = var_is_admin.get()

        if not all([uid, password, fname, lname, email, address, phno]):
            messagebox.showerror("Error", "All fields must be filled out.")
            return

        try:
            c.execute("""
                INSERT INTO customer (uid, pass, fname, lname, email, address, phno, is_admin) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (uid, password, fname, lname, email, address, phno, is_admin))
            conn.commit()
            messagebox.showinfo("Success", "Customer added successfully!")
            add_customer_window.destroy()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to add customer: {err}")

    add_customer_window = tk.Toplevel(root)
    add_customer_window.title("Add Customer")
    add_customer_window.geometry("400x600")

    tk.Label(add_customer_window, text="Pharmacy Management", font=("Helvetica", 20)).pack(pady=10)
    tk.Label(add_customer_window, text="User ID:").pack(pady=5)
    entry_uid = tk.Entry(add_customer_window)
    entry_uid.pack(pady=5)

    tk.Label(add_customer_window, text="Password:").pack(pady=5)
    entry_password = tk.Entry(add_customer_window, show="*")
    entry_password.pack(pady=5)

    tk.Label(add_customer_window, text="First Name:").pack(pady=5)
    entry_fname = tk.Entry(add_customer_window)
    entry_fname.pack(pady=5)

    tk.Label(add_customer_window, text="Last Name:").pack(pady=5)
    entry_lname = tk.Entry(add_customer_window)
    entry_lname.pack(pady=5)

    tk.Label(add_customer_window, text="Email:").pack(pady=5)
    entry_email = tk.Entry(add_customer_window)
    entry_email.pack(pady=5)

    tk.Label(add_customer_window, text="Address:").pack(pady=5)
    entry_address = tk.Entry(add_customer_window)
    entry_address.pack(pady=5)

    tk.Label(add_customer_window, text="Phone No:").pack(pady=5)
    entry_phno = tk.Entry(add_customer_window)
    entry_phno.pack(pady=5)

    var_is_admin = tk.BooleanVar()
    tk.Checkbutton(add_customer_window, text="Is Admin", variable=var_is_admin).pack(pady=5)

    tk.Button(add_customer_window, text="Save", command=save_customer).pack(pady=10)

# Function to view all customers (admin only)
def view_customers():
    view_window = tk.Toplevel(root)
    view_window.title("View Customers")
    view_window.geometry("1000x400")

    tk.Label(view_window, text="Pharmacy Management", font=("Helvetica", 20)).pack(pady=10)

    columns = ("User ID", "First Name", "Last Name", "Email", "Address", "Phone No", "Is Admin")
    tree = ttk.Treeview(view_window, columns=columns, show='headings')

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=140)

    tree.pack(fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(view_window, orient=tk.VERTICAL, command=tree.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.configure(yscrollcommand=scrollbar.set)

    try:
        c.execute("SELECT uid, fname, lname, email, address, phno, is_admin FROM customer")
        for row in c.fetchall():
            tree.insert("", tk.END, values=row)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Failed to fetch customers: {err}")
def generate_low_stock_report():
    report_window = tk.Toplevel(root)
    report_window.title("Low Stock Report")
    report_window.geometry("800x400")

    columns = ("Product ID", "Product Name", "Quantity", "Threshold")
    tree = ttk.Treeview(report_window, columns=columns, show='headings')

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=140)

    tree.pack(fill=tk.BOTH, expand=True)

    # Fetch products with low stock
    try:
        threshold = 10  # Example threshold
        c.execute("SELECT pid, pname, quantity FROM product WHERE quantity < %s", (threshold,))
        for row in c.fetchall():
            tree.insert("", tk.END, values=(row[0], row[1], row[2], threshold))
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Failed to fetch low stock products: {err}")


# Function to add a product (admin only)
def add_product():
    add_product_window = tk.Toplevel(root)
    add_product_window.title("Add Product")
    add_product_window.geometry("400x500")

    tk.Label(add_product_window, text="Pharmacy Management", font=("Helvetica", 20)).pack(pady=10)

    fields = [
        ("Product ID:", None),
        ("Product Name:", None),
        ("Manufacturer:", None),
        ("Manufacturing Date (YYYY-MM-DD):", None),
        ("Expiry Date (YYYY-MM-DD):", None),
        ("Price:", None),
        ("Quantity:", None)
    ]

    entries = {}
    for label_text, _ in fields:
        tk.Label(add_product_window, text=label_text).pack(pady=5)
        entry = tk.Entry(add_product_window)
        entry.pack(pady=5)
        entries[label_text] = entry

    def submit_product():
        try:
            values = [entry.get() for entry in entries.values()]
            if not all(values):
                messagebox.showerror("Error", "All fields must be filled out.")
                return

            c.execute("""
                INSERT INTO product (pid, pname, manufacturer, mfg_date, exp_date, price, quantity)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, values)
            conn.commit()
            messagebox.showinfo("Success", "Product added successfully!")
            add_product_window.destroy()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to add product: {err}")

    tk.Button(add_product_window, text="Add Product", command=submit_product).pack(pady=10)

# Function to check inventory (admin only)
def check_inventory():
    check_window = tk.Toplevel(root)
    check_window.title("Check Inventory")
    check_window.geometry("1000x400")

    tk.Label(check_window, text="Pharmacy Management", font=("Helvetica", 20)).pack(pady=10)

    columns = ("Product ID", "Product Name", "Manufacturer", "Mfg Date", "Exp Date", "Price", "Quantity")
    tree = ttk.Treeview(check_window, columns=columns, show='headings')

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=140)

    tree.pack(fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(check_window, orient=tk.VERTICAL, command=tree.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.configure(yscrollcommand=scrollbar.set)

    try:
        c.execute("SELECT pid, pname, manufacturer, mfg_date, exp_date, price, quantity FROM product")
        for row in c.fetchall():
            tree.insert("", tk.END, values=row)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Failed to fetch inventory: {err}")
        def generate_low_stock_report():
            report_window = tk.Toplevel(root)
            report_window.title("Low Stock Report")
            report_window.geometry("800x400")

        columns = ("Product ID", "Product Name", "Quantity", "Threshold")
        tree = ttk.Treeview(report_window, columns=columns, show='headings')

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=140)

    tree.pack(fill=tk.BOTH, expand=True)

    # Fetch products with low stock
    try:
        threshold = 10  # Example threshold
        c.execute("SELECT pid, pname, quantity FROM product WHERE quantity < %s", (threshold,))
        for row in c.fetchall():
            tree.insert("", tk.END, values=(row[0], row[1], row[2], threshold))
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Failed to fetch low stock products: {err}")

# Function to view all orders (admin only)
def view_all_orders():
    view_window = tk.Toplevel(root)
    view_window.title("View All Orders")
    view_window.geometry("800x400")

    columns = ("Order ID", "User ID", "Product ID", "Order Date", "Quantity")
    tree = ttk.Treeview(view_window, columns=columns, show='headings')

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=140)

    tree.pack(fill=tk.BOTH, expand=True)

    # Fetch all orders
    try:
        c.execute("SELECT * FROM orders")
        for row in c.fetchall():
            tree.insert("", tk.END, values=row)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Failed to fetch orders: {err}")

# Function to add an order for a user
def add_order_for_user(uid):
    def submit_order():
        product_id = entry_product_id.get()
        quantity = entry_quantity.get()

        if not all([product_id, quantity]):
            messagebox.showerror("Error", "All fields must be filled out.")
            return

        try:
            order_date = datetime.now().strftime('%Y-%m-%d')
            c.execute("""
                INSERT INTO orders (uid, pid, orderdatetime, quantity)
                VALUES (%s, %s, %s, %s)
            """, (uid, product_id, order_date, quantity))
            conn.commit()
            messagebox.showinfo("Success", "Order placed successfully!")
            add_order_window.destroy()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to place order: {err}")

    add_order_window = tk.Toplevel(root)
    add_order_window.title("Place Order")
    add_order_window.geometry("400x300")

    tk.Label(add_order_window, text="Product ID:").pack(pady=5)
    entry_product_id = tk.Entry(add_order_window)
    entry_product_id.pack(pady=5)

    tk.Label(add_order_window, text="Quantity:").pack(pady=5)
    entry_quantity = tk.Entry(add_order_window)
    entry_quantity.pack(pady=5)

    tk.Button(add_order_window, text="Submit Order", command=submit_order).pack(pady=10)

# Function to view user's own orders
def view_my_orders():
    view_window = tk.Toplevel(root)
    view_window.title("View My Orders")
    view_window.geometry("800x400")

    columns = ("Order ID", "Product ID", "Order Date", "Quantity")
    tree = ttk.Treeview(view_window, columns=columns, show='headings')

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=140)

    tree.pack(fill=tk.BOTH, expand=True)

    # Fetch orders for the current user
    try:
        c.execute("SELECT oid, pid, orderdatetime, quantity FROM orders WHERE uid = %s", (current_user['uid'],))
        for row in c.fetchall():
            tree.insert("", tk.END, values=row)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Failed to fetch orders: {err}")



# Function to logout
def logout():
    global current_user
    current_user = None
    main_frame.pack_forget()
    login_frame.pack(padx=20, pady=20)

# Main window setup
root = tk.Tk()
root.title("Pharmacy Manager")
root.geometry("600x400")

# Login Frame
login_frame = tk.Frame(root)
login_frame.pack(padx=20, pady=20)

tk.Label(login_frame, text="Pharmacy Management", font=("Helvetica", 20)).pack(pady=10)

tk.Label(login_frame, text="Username:").pack(pady=5)
entry_username = tk.Entry(login_frame)
entry_username.pack(pady=5)

tk.Label(login_frame, text="Password:").pack(pady=5)
entry_password = tk.Entry(login_frame, show="*")
entry_password.pack(pady=5)

tk.Button(login_frame, text="Login", command=validate_login).pack(pady=10)

# Main Frame (Initially hidden)
main_frame = tk.Frame(root)
root.mainloop()
