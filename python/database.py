# database.py
# All database operations for Banking App

import mysql.connector
from config import DB_CONFIG

# =============================================================
# CONNECTION
# =============================================================
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


# =============================================================
# ACCOUNT OPERATIONS
# =============================================================
def get_account_info(account_id: int):
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT c.CustomerName, c.Phone, a.AccountID,
               a.AccountType, a.Balance, a.Status,
               a.OpenDate, b.BranchName
        FROM   Accounts  a
        JOIN   Customers c ON a.CustomerID = c.CustomerID
        JOIN   Branches  b ON a.BranchID   = b.BranchID
        WHERE  a.AccountID = %s
    """, (account_id,))
    result = cur.fetchone()
    cur.close(); conn.close()
    return result


def get_all_active_accounts():
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT AccountID, CustomerName, FORMAT(Balance,0) AS Balance,
               AccountType, Status, BranchName
        FROM   vw_CustomerBalance
        WHERE  Status = 'Active'
        ORDER  BY Balance DESC
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows


def open_account(customer_id: int, branch_id: int,
                 account_type: str, initial_balance: float):
    from datetime import date
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        INSERT INTO Accounts (CustomerID, BranchID, AccountType, Balance, OpenDate)
        VALUES (%s, %s, %s, %s, %s)
    """, (customer_id, branch_id, account_type,
          initial_balance, date.today()))
    conn.commit()
    new_id = cur.lastrowid
    cur.close(); conn.close()
    return new_id


# =============================================================
# TRANSACTIONS  (via Stored Procedures)
# =============================================================
def deposit(account_id: int, amount: float, description: str):
    conn = get_connection()
    cur  = conn.cursor()
    try:
        cur.callproc('sp_Deposit', [account_id, amount, description])
        for _ in cur.stored_results(): pass
        conn.commit()
        return True, "Deposit successful"
    except mysql.connector.Error as e:
        return False, e.msg
    finally:
        cur.close(); conn.close()


def withdrawal(account_id: int, amount: float, description: str):
    conn = get_connection()
    cur  = conn.cursor()
    try:
        cur.callproc('sp_Withdrawal', [account_id, amount, description])
        for _ in cur.stored_results(): pass
        conn.commit()
        return True, "Withdrawal successful"
    except mysql.connector.Error as e:
        return False, e.msg
    finally:
        cur.close(); conn.close()


def transfer(from_id: int, to_id: int, amount: float, description: str):
    conn = get_connection()
    cur  = conn.cursor()
    try:
        cur.callproc('sp_Transfer', [from_id, to_id, amount, description])
        for _ in cur.stored_results(): pass
        conn.commit()
        return True, "Transfer successful"
    except mysql.connector.Error as e:
        return False, e.msg
    finally:
        cur.close(); conn.close()


def close_account(account_id: int):
    conn = get_connection()
    cur  = conn.cursor()
    try:
        cur.callproc('sp_CloseAccount', [account_id])
        for _ in cur.stored_results(): pass
        conn.commit()
        return True, "Account closed successfully"
    except mysql.connector.Error as e:
        return False, e.msg
    finally:
        cur.close(); conn.close()


# =============================================================
# REPORTS
# =============================================================
def get_transaction_history(account_id: int, limit: int = 50):
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT TransactionID,
               TransactionType,
               FORMAT(Amount, 0)  AS Amount,
               TransactionDate,
               Description
        FROM   Transactions
        WHERE  FromAccountID = %s OR ToAccountID = %s
        ORDER  BY TransactionDate DESC
        LIMIT  %s
    """, (account_id, account_id, limit))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows


def get_daily_report(date_str: str):
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT TransactionType,
               COUNT(*)           AS TotalCount,
               FORMAT(SUM(Amount),0) AS TotalAmount
        FROM   Transactions
        WHERE  DATE(TransactionDate) = %s
        GROUP  BY TransactionType
    """, (date_str,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows


def get_customer_balances():
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT CustomerName,
               AccountType,
               FORMAT(Balance,0) AS Balance_VND,
               Status,
               BranchName
        FROM   vw_CustomerBalance
        ORDER  BY Balance DESC
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows


def get_transaction_summary():
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT CustomerName,
               TotalTransactions,
               FORMAT(TotalDeposit,    0) AS Total_In_VND,
               FORMAT(TotalWithdrawal, 0) AS Total_Out_VND
        FROM   vw_TransactionSummary
        ORDER  BY TotalTransactions DESC
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows


def get_vip_customers():
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT CustomerName, Phone,
               FORMAT(SUM(Balance),0) AS Total_Assets_VND,
               COUNT(AccountID)       AS Total_Accounts,
               CASE
                   WHEN SUM(Balance) >  100000000 THEN 'PLATINUM'
                   WHEN SUM(Balance) >= 10000000  THEN 'GOLD'
                   ELSE 'SILVER'
               END AS Tier
        FROM   vw_CustomerBalance
        WHERE  Status = 'Active'
        GROUP  BY CustomerID, CustomerName, Phone
        ORDER  BY SUM(Balance) DESC
        LIMIT  10
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows


def get_audit_logs(severity: str = None, limit: int = 100):
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    if severity:
        cur.execute("""
            SELECT LogDate, Severity, Message
            FROM   AuditLogs
            WHERE  Severity = %s
            ORDER  BY LogDate DESC LIMIT %s
        """, (severity, limit))
    else:
        cur.execute("""
            SELECT LogDate, Severity, Message
            FROM   AuditLogs
            ORDER  BY LogDate DESC LIMIT %s
        """, (limit,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows


def get_db_stats():
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT
            (SELECT COUNT(*) FROM Customers)                          AS customers,
            (SELECT COUNT(*) FROM Accounts WHERE Status='Active')     AS active_accounts,
            (SELECT COUNT(*) FROM Transactions)                       AS transactions,
            (SELECT FORMAT(SUM(Balance),0) FROM Accounts
             WHERE  Status='Active')                                  AS total_balance,
            (SELECT COUNT(*) FROM AuditLogs WHERE Severity='HIGH')    AS high_alerts
    """)
    row = cur.fetchone()
    cur.close(); conn.close()
    return row


def get_all_customers():
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT CustomerID, CustomerName, Phone FROM Customers ORDER BY CustomerName")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows


def get_all_branches():
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT BranchID, BranchName FROM Branches ORDER BY BranchName")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows
