USE bankingdb;


-- =============================================================
-- NHÓM 1-4: BASIC REPORTING 
-- =============================================================

-- Query 1:
SELECT
    CustomerName,
    AccountType,
    FORMAT(Balance, 0)  AS Balance_VND,
    Status,
    BranchName
FROM vw_CustomerBalance
ORDER BY Balance DESC;


-- Query 2: Thống kê nhân viên và vai trò đảm nhiệm
SELECT
    EmployeeName,
    BranchName,
    Roles
FROM vw_EmployeeRoles;


-- Query 3: Tìm các tài khoản đang bị khóa hoặc đóng băng
SELECT
    AccountID,
    CustomerName,
    Status,
    BranchName
FROM vw_CustomerBalance
WHERE Status IN ('Frozen', 'Closed');


-- Query 4: Tổng quan dòng tiền của từng tài khoản
SELECT
    CustomerName,
    TotalTransactions,
    FORMAT(TotalDeposit,    0)  AS Total_In_VND,
    FORMAT(TotalWithdrawal, 0)  AS Total_Out_VND
FROM vw_TransactionSummary
ORDER BY TotalTransactions DESC;


-- =============================================================
-- NHÓM 5-8: BUSINESS INSIGHT
-- =============================================================

-- Query 5: Top 5 chi nhánh có tổng tiền gửi cao nhất
SELECT
    BranchName,
    COUNT(AccountID)        AS Active_Accounts,
    FORMAT(SUM(Balance), 0) AS Total_Vault_Value_VND
FROM vw_CustomerBalance
WHERE Status = 'Active'
GROUP BY BranchName
ORDER BY SUM(Balance) DESC
LIMIT 5;


-- Query 6: Phân tích tỷ trọng loại tài khoản (Market Share)
SELECT
    AccountType,
    COUNT(*)                                                        AS Quantity,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Accounts), 2)   AS Percentage
FROM Accounts
GROUP BY AccountType;


-- Query 7: Nhận diện khách hàng VIP (Top 5 tổng tài sản lớn nhất)
SELECT
    CustomerName,
    Phone,
    FORMAT(SUM(Balance), 0) AS Total_Assets_VND,
    COUNT(AccountID)        AS Total_Accounts
FROM vw_CustomerBalance
WHERE Status = 'Active'
GROUP BY CustomerID, CustomerName, Phone
ORDER BY SUM(Balance) DESC
LIMIT 5;


-- Query 8: Nhật ký Audit các giao dịch rủi ro cao
SELECT
    LogDate,
    Severity,
    Message
FROM AuditLogs
WHERE Severity = 'HIGH'
ORDER BY LogDate DESC
LIMIT 20;


-- =============================================================
-- NHÓM 9-11: ADVANCED ANALYTICS
-- =============================================================

-- Query 9: Phân hạng khách hàng (Customer Tiering)
SELECT
    CustomerName,
    FORMAT(SUM(Balance), 0) AS Total_Balance_VND,
    CASE
        WHEN SUM(Balance) >  100000000 THEN 'PLATINUM (VIP)'
        WHEN SUM(Balance) >= 10000000  THEN 'GOLD'
        ELSE                                'SILVER'
    END AS Membership_Tier
FROM vw_CustomerBalance
WHERE Status = 'Active'
GROUP BY CustomerID, CustomerName
ORDER BY SUM(Balance) DESC;


-- Query 10: Tính lãi suất dự kiến 30 ngày cho tài khoản Saving
SELECT
    CustomerName,
    FORMAT(Balance, 0)                          AS Principal_VND,
    FORMAT(fn_CalcInterest(Balance, 0.065, 30), 0) AS Interest_30days_VND
FROM vw_CustomerBalance
WHERE AccountType = 'Saving'
  AND Status      = 'Active';


-- Query 11: Giao dịch chuyển khoản liên chi nhánh
SELECT
    t.TransactionID,
    FORMAT(t.Amount, 0)     AS Amount_VND,
    t.TransactionDate,
    b1.BranchName           AS From_Branch,
    b2.BranchName           AS To_Branch
FROM Transactions t
JOIN Accounts a1 ON t.FromAccountID = a1.AccountID
JOIN Branches b1 ON a1.BranchID    = b1.BranchID
JOIN Accounts a2 ON t.ToAccountID  = a2.AccountID
JOIN Branches b2 ON a2.BranchID    = b2.BranchID
WHERE t.TransactionType = 'Transfer'
ORDER BY t.TransactionDate DESC;
