-- =============================================================
--  BANKING MANAGEMENT SYSTEM
--  Security & User Administration
-- =============================================================

USE BankingDB;

-- =============================================================
-- 1. TẠO USERS
-- =============================================================
DROP USER IF EXISTS 'bank_manager'@'localhost';
DROP USER IF EXISTS 'bank_teller'@'localhost';
DROP USER IF EXISTS 'bank_auditor'@'localhost';

CREATE USER 'bank_manager'@'localhost' IDENTIFIED BY 'Manager@2024!';
CREATE USER 'bank_teller'@'localhost'  IDENTIFIED BY 'Teller@2024!';
CREATE USER 'bank_auditor'@'localhost' IDENTIFIED BY 'Auditor@2024!';


-- =============================================================
-- 2. PHÂN QUYỀN
-- =============================================================

-- MANAGER: toàn quyền
GRANT ALL PRIVILEGES ON BankingDB.* TO 'bank_manager'@'localhost';

-- TELLER: thao tác giao dịch hàng ngày
GRANT SELECT ON BankingDB.Customers       TO 'bank_teller'@'localhost';
GRANT SELECT ON BankingDB.Accounts        TO 'bank_teller'@'localhost';
GRANT SELECT ON BankingDB.Branches        TO 'bank_teller'@'localhost';
GRANT SELECT, INSERT ON BankingDB.Transactions TO 'bank_teller'@'localhost';
GRANT SELECT ON BankingDB.AuditLogs       TO 'bank_teller'@'localhost';
GRANT EXECUTE ON PROCEDURE BankingDB.sp_Deposit    TO 'bank_teller'@'localhost';
GRANT EXECUTE ON PROCEDURE BankingDB.sp_Withdrawal TO 'bank_teller'@'localhost';
GRANT EXECUTE ON PROCEDURE BankingDB.sp_Transfer   TO 'bank_teller'@'localhost';

-- AUDITOR: chỉ đọc
GRANT SELECT ON BankingDB.Customers       TO 'bank_auditor'@'localhost';
GRANT SELECT ON BankingDB.Accounts        TO 'bank_auditor'@'localhost';
GRANT SELECT ON BankingDB.Transactions    TO 'bank_auditor'@'localhost';
GRANT SELECT ON BankingDB.AuditLogs       TO 'bank_auditor'@'localhost';
GRANT SELECT ON BankingDB.Branches        TO 'bank_auditor'@'localhost';
GRANT SELECT ON BankingDB.Employees       TO 'bank_auditor'@'localhost';
GRANT SELECT ON BankingDB.Roles           TO 'bank_auditor'@'localhost';
GRANT SELECT ON BankingDB.EmployeeRoles   TO 'bank_auditor'@'localhost';
GRANT SELECT ON BankingDB.vw_CustomerBalance    TO 'bank_auditor'@'localhost';
GRANT SELECT ON BankingDB.vw_TransactionSummary TO 'bank_auditor'@'localhost';
GRANT SELECT ON BankingDB.vw_EmployeeRoles      TO 'bank_auditor'@'localhost';

FLUSH PRIVILEGES;


-- =============================================================
-- 3. MÃ HÓA DỮ LIỆU NHẠY CẢM
-- =============================================================


SET @col_exists = (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = 'BankingDB'
      AND TABLE_NAME   = 'Accounts'
      AND COLUMN_NAME  = 'BalanceEncrypted'
);

SET @sql = IF(@col_exists = 0,
    'ALTER TABLE Accounts ADD COLUMN BalanceEncrypted VARBINARY(256) NULL',
    'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Mã hóa Balance
UPDATE Accounts
SET    BalanceEncrypted = AES_ENCRYPT(CAST(Balance AS CHAR), 'BankSecretKey2024')
WHERE  AccountID > 0;

-- Verify giải mã
SELECT
    AccountID,
    Balance                                                                      AS BalancePlain,
    CAST(AES_DECRYPT(BalanceEncrypted, 'BankSecretKey2024') AS DECIMAL(18,2))   AS BalanceDecrypted
FROM Accounts
LIMIT 5;


-- =============================================================
-- 4. BACKUP INFO PROCEDURE
-- =============================================================
DELIMITER //

DROP PROCEDURE IF EXISTS sp_BackupInfo //
CREATE PROCEDURE sp_BackupInfo()
BEGIN
    SELECT
        'BankingDB'                         AS DatabaseName,
        NOW()                               AS BackupTime,
        (SELECT COUNT(*) FROM Customers)    AS TotalCustomers,
        (SELECT COUNT(*) FROM Accounts)     AS TotalAccounts,
        (SELECT COUNT(*) FROM Transactions) AS TotalTransactions,
        (SELECT SUM(Balance) FROM Accounts
         WHERE  Status = 'Active')          AS TotalActiveBalance;
END //

DELIMITER ;


-- =============================================================
-- 5. PERFORMANCE INDEXES
-- =============================================================
DELIMITER //

DROP PROCEDURE IF EXISTS sp_CreateIndexSafe //
CREATE PROCEDURE sp_CreateIndexSafe(
    IN p_table VARCHAR(64),
    IN p_index VARCHAR(64),
    IN p_sql   TEXT
)
BEGIN
    DECLARE v_exists INT DEFAULT 0;
    SELECT COUNT(*) INTO v_exists
    FROM   information_schema.STATISTICS
    WHERE  TABLE_SCHEMA = 'BankingDB'
      AND  TABLE_NAME   = p_table
      AND  INDEX_NAME   = p_index;

    IF v_exists = 0 THEN
        SET @ddl = p_sql;
        PREPARE s FROM @ddl;
        EXECUTE s;
        DEALLOCATE PREPARE s;
        SELECT CONCAT('Created: ', p_index) AS Result;
    ELSE
        SELECT CONCAT('Already exists: ', p_index) AS Result;
    END IF;
END //

DELIMITER ;

CALL sp_CreateIndexSafe('Accounts',     'idx_acc_status',
    'CREATE INDEX idx_acc_status ON Accounts(Status)');

CALL sp_CreateIndexSafe('Transactions', 'idx_trans_type',
    'CREATE INDEX idx_trans_type ON Transactions(TransactionType)');

CALL sp_CreateIndexSafe('AuditLogs',    'idx_audit_severity',
    'CREATE INDEX idx_audit_severity ON AuditLogs(Severity)');

CALL sp_CreateIndexSafe('Transactions', 'idx_trans_from_date',
    'CREATE INDEX idx_trans_from_date ON Transactions(FromAccountID, TransactionDate)');

CALL sp_CreateIndexSafe('Transactions', 'idx_trans_to_date',
    'CREATE INDEX idx_trans_to_date ON Transactions(ToAccountID, TransactionDate)');


-- =============================================================
-- 6. VERIFY
-- =============================================================
SELECT User AS Username, Host, account_locked, password_expired
FROM   mysql.user
WHERE  User IN ('bank_manager','bank_teller','bank_auditor')
ORDER  BY User;

SELECT TABLE_NAME, INDEX_NAME, COLUMN_NAME
FROM   information_schema.STATISTICS
WHERE  TABLE_SCHEMA = 'BankingDB'
  AND  INDEX_NAME LIKE 'idx_%'
ORDER  BY TABLE_NAME, INDEX_NAME;