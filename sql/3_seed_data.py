import random
import mysql.connector
from faker import Faker
from datetime import date, timedelta

fake = Faker('vi_VN')  
Faker.seed(42)
random.seed(42)

# =============================================================
# CONFIG
# =============================================================
DB_CONFIG = {
    'host':     'localhost',
    'port':     3306,
    'user':     'root',
    'password': '123456',   
    'database': 'bankingdb'
}

N = 510  

# =============================================================
# HELPERS
# =============================================================
def rand_date(start='2018-01-01', end='2023-12-31'):
    s = date.fromisoformat(start)
    e = date.fromisoformat(end)
    return s + timedelta(days=random.randint(0, (e - s).days))

def rand_phone():
    prefix = random.choice(['090','091','092','093','094','096','097','098','032','033','034','035','036','037','038','039'])
    return prefix + ''.join([str(random.randint(0,9)) for _ in range(7)])

def rand_balance():
    return round(random.uniform(100000, 500000000), 2)

def batch_insert(cursor, sql, data, batch_size=100):
    for i in range(0, len(data), batch_size):
        cursor.executemany(sql, data[i:i+batch_size])

# =============================================================
# 1. BRANCHES — 510 rows
# =============================================================
def seed_branches(cursor):
    cities = [
        'Hanoi','Ho Chi Minh','Da Nang','Hue','Can Tho',
        'Hai Phong','Nha Trang','Vung Tau','Bien Hoa','Quy Nhon',
        'Vinh','Thai Nguyen','Nam Dinh','Ninh Binh','Thanh Hoa',
        'Buon Ma Thuot','Pleiku','Da Lat','Phan Thiet','Long Xuyen'
    ]
    data = []
    for i in range(N):
        city = cities[i % len(cities)]
        data.append((
            f'{city} Branch {i+1}',
            fake.address()[:200],
            rand_phone()
        ))
    batch_insert(cursor, """
        INSERT INTO Branches (BranchName, Address, Phone) VALUES (%s, %s, %s)
    """, data)
    print(f"  ✅ Branches:      {len(data)} rows")
    return len(data)

# =============================================================
# 2. ROLES — 510 rows
# =============================================================
def seed_roles(cursor):
    base_roles = ['Manager','Teller','Auditor','Supervisor','IT Admin',
                  'Loan Officer','Customer Service','Security','Analyst','Trainer']
    data = []
    for i in range(N):
        role_name = f"{base_roles[i % len(base_roles)]} L{i//len(base_roles)+1}"
        data.append((
            role_name,
            f'Role description for {role_name}'
        ))
    batch_insert(cursor, """
        INSERT INTO Roles (RoleName, Description) VALUES (%s, %s)
    """, data)
    print(f"  ✅ Roles:         {len(data)} rows")
    return len(data)

# =============================================================
# 3. CUSTOMERS — 510 rows
# =============================================================
def seed_customers(cursor):
    data = []
    used_phones = set()
    for i in range(N):
        phone = rand_phone()
        while phone in used_phones:
            phone = rand_phone()
        used_phones.add(phone)

        dob = rand_date('1960-01-01', '2000-12-31')
        data.append((
            fake.name(),
            phone,
            fake.address()[:200],
            f'customer{i+1}@email.com',
            str(dob)
        ))
    batch_insert(cursor, """
        INSERT INTO Customers (CustomerName, Phone, Address, Email, DateOfBirth)
        VALUES (%s, %s, %s, %s, %s)
    """, data)
    print(f"  ✅ Customers:     {len(data)} rows")
    return len(data)

# =============================================================
# 4. EMPLOYEES — 510 rows
# =============================================================
def seed_employees(cursor, branch_count):
    data = []
    used_emails = set()
    for i in range(N):
        branch_id = (i % branch_count) + 1
        email = f'emp{i+1}@bank.com'
        while email in used_emails:
            email = f'emp{i+1}_{random.randint(0,999)}@bank.com'
        used_emails.add(email)
        data.append((
            fake.name(),
            branch_id,
            email
        ))
    batch_insert(cursor, """
        INSERT INTO Employees (EmployeeName, BranchID, Email) VALUES (%s, %s, %s)
    """, data)
    print(f"  ✅ Employees:     {len(data)} rows")
    return len(data)

# =============================================================
# 5. EMPLOYEE ROLES — 510 rows (bridge table)
# =============================================================
def seed_employee_roles(cursor, emp_count, role_count):
    used = set()
    data = []
    attempts = 0
    while len(data) < N and attempts < N * 10:
        emp_id  = random.randint(1, emp_count)
        role_id = random.randint(1, role_count)
        if (emp_id, role_id) not in used:
            used.add((emp_id, role_id))
            data.append((emp_id, role_id))
        attempts += 1

    batch_insert(cursor, """
        INSERT IGNORE INTO EmployeeRoles (EmployeeID, RoleID) VALUES (%s, %s)
    """, data)
    print(f"  ✅ EmployeeRoles: {len(data)} rows")
    return len(data)

# =============================================================
# 6. ACCOUNTS — 510 rows
# =============================================================
def seed_accounts(cursor, customer_count, branch_count):
    account_types = ['Saving', 'Current']
    data = []
    for i in range(N):
        customer_id = (i % customer_count) + 1
        branch_id   = (i % branch_count)   + 1
        open_date   = rand_date('2018-01-01', '2023-06-30')
        data.append((
            customer_id,
            branch_id,
            random.choice(account_types),
            rand_balance(),
            'Active',
            str(open_date)
        ))
    batch_insert(cursor, """
        INSERT INTO Accounts (CustomerID, BranchID, AccountType, Balance, Status, OpenDate)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, data)
    print(f"  ✅ Accounts:      {len(data)} rows")
    return len(data)

# =============================================================
# 7. TRANSACTIONS — 510 rows (qua stored procedures)
# =============================================================
def seed_transactions(cursor, conn, account_count):
    tx_types = ['Deposit', 'Withdrawal', 'Transfer']
    descriptions = [
        'Salary credit', 'ATM withdrawal', 'Bill payment',
        'Online transfer', 'Cash deposit', 'Business income',
        'Investment return', 'Personal expense', 'Loan repayment',
        'Utility payment', 'Shopping', 'Medical expense',
        'Education fee', 'Rent payment', 'Tax payment'
    ]

    success = 0
    fail    = 0
    target  = N

    cursor.execute("SELECT AccountID, Balance FROM Accounts WHERE Status='Active'")
    balances = {row[0]: float(row[1]) for row in cursor.fetchall()}
    active_ids = list(balances.keys())

    if not active_ids:
        print("  ❌ Không có active account!")
        return 0

    i = 0
    while success < target:
        tx_type = random.choice(tx_types)
        amount  = round(random.uniform(100000, 50000000), 2)
        desc    = random.choice(descriptions)

        try:
            if tx_type == 'Deposit':
                to_id = random.choice(active_ids)
                cursor.callproc('sp_Deposit', [to_id, amount, desc])
                balances[to_id] = balances.get(to_id, 0) + amount

            elif tx_type == 'Withdrawal':
                # Chỉ rút từ account có đủ tiền
                eligible = [aid for aid, bal in balances.items() if bal >= amount]
                if not eligible:
                    fail += 1
                    i += 1
                    if i > target * 3:
                        break
                    continue
                from_id = random.choice(eligible)
                cursor.callproc('sp_Withdrawal', [from_id, amount, desc])
                balances[from_id] -= amount

            elif tx_type == 'Transfer':
                eligible = [aid for aid, bal in balances.items() if bal >= amount]
                if len(eligible) < 2:
                    fail += 1
                    i += 1
                    if i > target * 3:
                        break
                    continue
                from_id = random.choice(eligible)
                to_id   = random.choice([a for a in active_ids if a != from_id])
                cursor.callproc('sp_Transfer', [from_id, to_id, amount, desc])
                balances[from_id] -= amount
                balances[to_id]    = balances.get(to_id, 0) + amount

            # Consume stored procedure results
            for _ in cursor.stored_results():
                pass

            success += 1

            # Commit mỗi 50 transactions
            if success % 50 == 0:
                conn.commit()
                print(f"    → {success}/{target} transactions inserted...")

        except mysql.connector.Error as e:
            fail += 1

        i += 1
        if i > target * 5:
            break

    conn.commit()
    print(f"  ✅ Transactions:  {success} rows inserted, {fail} skipped")

    # Đếm AuditLogs được tạo tự động
    cursor.execute("SELECT COUNT(*) FROM AuditLogs")
    audit_count = cursor.fetchone()[0]
    print(f"  ✅ AuditLogs:     {audit_count} rows (auto by trigger)")

    return success

# =============================================================
# MAIN
# =============================================================
def main():
    print("=" * 55)
    print(f"  BankingDB — Seed {N} rows per table")
    print("=" * 55)

    try:
        conn   = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print(f"✅ Connected to MySQL\n")
    except mysql.connector.Error as e:
        print(f"❌ Connection failed: {e}")
        print("   Kiểm tra lại DB_CONFIG (password)")
        return

    try:
        print("📦 Inserting data (this may take 1-2 minutes)...\n")

        # Thứ tự QUAN TRỌNG theo FK dependency
        b = seed_branches(cursor);         conn.commit()
        r = seed_roles(cursor);            conn.commit()
        c = seed_customers(cursor);        conn.commit()
        e = seed_employees(cursor, b);     conn.commit()
        seed_employee_roles(cursor, e, r); conn.commit()
        a = seed_accounts(cursor, c, b);   conn.commit()
        seed_transactions(cursor, conn, a)

        # ── Summary ──────────────────────────────────────────
        print("\n" + "=" * 55)
        print("📊 Final row counts:")
        tables = ['Branches','Roles','Customers','Employees',
                  'EmployeeRoles','Accounts','Transactions','AuditLogs']
        total = 0
        for t in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {t}")
            count = cursor.fetchone()[0]
            total += count
            status = "✅" if count >= N else "⚠️ "
            print(f"  {status} {t:<20}: {count:>5} rows")

        print(f"\n  {'TOTAL':<22}: {total:>5} rows")
        print("\n🎉 Seed completed!")

    except mysql.connector.Error as e:
        conn.rollback()
        print(f"\n❌ Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    main()