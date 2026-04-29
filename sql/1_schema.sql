-- =============================================================
--  BANKING MANAGEMENT SYSTEM
-- =============================================================

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS,        UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- =============================================================
-- 0. DATABASE
-- =============================================================
CREATE DATABASE IF NOT EXISTS bankingdb
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE BankingDB;


-- =============================================================
-- 1. BRANCHES
-- =============================================================
DROP TABLE IF EXISTS `Branches`;

CREATE TABLE `Branches` (
  `BranchID`   INT          NOT NULL AUTO_INCREMENT,
  `BranchName` VARCHAR(100) NOT NULL,
  `Address`    TEXT         NOT NULL,
  `Phone`      VARCHAR(15)  NULL,
  `CreatedAt`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`BranchID`)
) ENGINE = InnoDB COMMENT = 'Bank branch locations';


-- =============================================================
-- 2. ROLES
-- =============================================================
DROP TABLE IF EXISTS `Roles`;

CREATE TABLE `Roles` (
  `RoleID`      INT          NOT NULL AUTO_INCREMENT,
  `RoleName`    VARCHAR(50)  NOT NULL,
  `Description` VARCHAR(255) NULL,
  PRIMARY KEY (`RoleID`),
  UNIQUE INDEX `uq_RoleName` (`RoleName`)
) ENGINE = InnoDB COMMENT = 'Employee role definitions';


-- =============================================================
-- 3. EMPLOYEES  
-- =============================================================
DROP TABLE IF EXISTS `Employees`;

CREATE TABLE `Employees` (
  `EmployeeID`   INT          NOT NULL AUTO_INCREMENT,
  `EmployeeName` VARCHAR(100) NOT NULL,
  `BranchID`     INT          NOT NULL,
  `Email`        VARCHAR(100) NULL,
  `CreatedAt`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`EmployeeID`),
  INDEX `idx_emp_branch` (`BranchID`),
  INDEX `idx_emp_email`  (`Email`),
  CONSTRAINT `fk_emp_branch`
    FOREIGN KEY (`BranchID`) REFERENCES `Branches` (`BranchID`)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT = 'Bank employees';


-- =============================================================
-- 4. EMPLOYEE ↔ ROLES  (N-N)
-- =============================================================
DROP TABLE IF EXISTS `EmployeeRoles`;

CREATE TABLE `EmployeeRoles` (
  `EmployeeID` INT      NOT NULL,
  `RoleID`     INT      NOT NULL,
  `AssignedAt` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`EmployeeID`, `RoleID`),
  INDEX `idx_emproles_role` (`RoleID`),
  CONSTRAINT `fk_emproles_employee`
    FOREIGN KEY (`EmployeeID`) REFERENCES `Employees` (`EmployeeID`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_emproles_role`
    FOREIGN KEY (`RoleID`) REFERENCES `Roles` (`RoleID`)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT = 'Many-to-many: Employee <-> Role';


-- =============================================================
-- 5. CUSTOMERS
-- =============================================================
DROP TABLE IF EXISTS `Customers`;

CREATE TABLE `Customers` (
  `CustomerID`   INT          NOT NULL AUTO_INCREMENT,
  `CustomerName` VARCHAR(100) NOT NULL,
  `Phone`        VARCHAR(15)  NOT NULL,
  `Address`      TEXT         NULL,
  `Email`        VARCHAR(100) NULL,
  `DateOfBirth`  DATE         NULL,
  `CreatedAt`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`CustomerID`),
  UNIQUE INDEX `uq_Customer_Phone` (`Phone`),
  INDEX `idx_customer_phone` (`Phone`),
  INDEX `idx_customer_name`  (`CustomerName`)
) ENGINE = InnoDB COMMENT = 'Bank customers';


-- =============================================================
-- 6. ACCOUNTS
-- =============================================================
DROP TABLE IF EXISTS `Accounts`;

CREATE TABLE `Accounts` (
  `AccountID`   INT           NOT NULL AUTO_INCREMENT,
  `CustomerID`  INT           NOT NULL,
  `BranchID`    INT           NOT NULL,
  `AccountType` ENUM('Saving','Current')                    NOT NULL,
  `Balance`     DECIMAL(18,2) NOT NULL DEFAULT 0.00,
  `Status`      ENUM('Active','Closed','Frozen')            NOT NULL DEFAULT 'Active',
  `OpenDate`    DATE          NOT NULL DEFAULT (CURRENT_DATE),
  `CloseDate`   DATE          NULL,
  `CreatedAt`   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`AccountID`),
  INDEX `idx_acc_customer` (`CustomerID`),
  INDEX `idx_acc_branch`   (`BranchID`),
  CONSTRAINT `fk_acc_customer`
    FOREIGN KEY (`CustomerID`) REFERENCES `Customers` (`CustomerID`)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_acc_branch`
    FOREIGN KEY (`BranchID`)   REFERENCES `Branches`  (`BranchID`)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `chk_balance_non_negative`
    CHECK (`Balance` >= 0),
  CONSTRAINT `chk_close_after_open`
    CHECK (`CloseDate` IS NULL OR `CloseDate` >= `OpenDate`)
) ENGINE = InnoDB COMMENT = 'Customer bank accounts';


-- =============================================================
-- 7. TRANSACTIONS
-- =============================================================
DROP TABLE IF EXISTS `Transactions`;

CREATE TABLE `Transactions` (
  `TransactionID`   INT           NOT NULL AUTO_INCREMENT,
  `FromAccountID`   INT           NULL,
  `ToAccountID`     INT           NULL,
  `TransactionType` ENUM('Deposit','Withdrawal','Transfer') NOT NULL,
  `Amount`          DECIMAL(18,2) NOT NULL,
  `TransactionDate` DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Description`     VARCHAR(255)  NULL,
  PRIMARY KEY (`TransactionID`),
  INDEX `idx_trans_from` (`FromAccountID`),
  INDEX `idx_trans_to`   (`ToAccountID`),
  INDEX `idx_trans_date` (`TransactionDate`),
  CONSTRAINT `fk_trans_from`
    FOREIGN KEY (`FromAccountID`) REFERENCES `Accounts` (`AccountID`)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_trans_to`
    FOREIGN KEY (`ToAccountID`)   REFERENCES `Accounts` (`AccountID`)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `chk_amount_positive`
    CHECK (`Amount` > 0)
) ENGINE = InnoDB COMMENT = 'All financial transactions';


-- =============================================================
-- 8. AUDIT LOGS
-- =============================================================
DROP TABLE IF EXISTS `AuditLogs`;

CREATE TABLE `AuditLogs` (
  `LogID`         INT      NOT NULL AUTO_INCREMENT,
  `TransactionID` INT      NULL,
  `LogDate`       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Severity`      ENUM('LOW','MEDIUM','HIGH') NOT NULL DEFAULT 'LOW',
  `Message`       TEXT     NOT NULL,
  PRIMARY KEY (`LogID`),
  INDEX `idx_audit_transaction` (`TransactionID`),
  INDEX `idx_audit_date`        (`LogDate`),
  CONSTRAINT `fk_audit_transaction`
    FOREIGN KEY (`TransactionID`) REFERENCES `Transactions` (`TransactionID`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT = 'Security and activity audit trail';


-- =============================================================
-- 9. VIEWS
-- =============================================================

-- View: số dư hiện tại theo khách hàng
CREATE OR REPLACE VIEW `vw_CustomerBalance` AS
SELECT
    c.CustomerID,
    c.CustomerName,
    c.Phone,
    a.AccountID,
    a.AccountType,
    a.Balance,
    a.Status,
    b.BranchName
FROM Customers c
JOIN Accounts  a ON c.CustomerID = a.CustomerID
JOIN Branches  b ON a.BranchID   = b.BranchID;

-- View: tổng hợp giao dịch theo tài khoản 
CREATE OR REPLACE VIEW `vw_TransactionSummary` AS
SELECT
    a.AccountID,
    c.CustomerName,
    COUNT(t.TransactionID)                                             AS TotalTransactions,
    SUM(CASE WHEN t.TransactionType = 'Deposit'    THEN t.Amount ELSE 0 END) AS TotalDeposit,
    SUM(CASE WHEN t.TransactionType = 'Withdrawal' THEN t.Amount ELSE 0 END) AS TotalWithdrawal,
    SUM(CASE WHEN t.TransactionType = 'Transfer'   THEN t.Amount ELSE 0 END) AS TotalTransferOut,
    MAX(t.TransactionDate)                                             AS LastTransactionDate
FROM Accounts a
JOIN Customers c ON a.CustomerID = c.CustomerID
LEFT JOIN (
    -- Chỉ lấy giao dịch mà account là bên GỬI (Withdrawal / Transfer out)
    SELECT TransactionID, FromAccountID AS AccountID, TransactionType, Amount, TransactionDate
    FROM Transactions
    WHERE FromAccountID IS NOT NULL
    UNION ALL
    -- Chỉ lấy giao dịch mà account là bên NHẬN (Deposit)
    SELECT TransactionID, ToAccountID AS AccountID, TransactionType, Amount, TransactionDate
    FROM Transactions
    WHERE ToAccountID IS NOT NULL AND TransactionType = 'Deposit'
) t ON t.AccountID = a.AccountID
GROUP BY a.AccountID, c.CustomerName;

-- View: nhân viên và vai trò
CREATE OR REPLACE VIEW `vw_EmployeeRoles` AS
SELECT
    e.EmployeeID,
    e.EmployeeName,
    b.BranchName,
    GROUP_CONCAT(r.RoleName ORDER BY r.RoleName SEPARATOR ', ') AS Roles
FROM Employees    e
JOIN Branches     b  ON e.BranchID  = b.BranchID
LEFT JOIN EmployeeRoles er ON e.EmployeeID = er.EmployeeID
LEFT JOIN Roles         r  ON er.RoleID    = r.RoleID
GROUP BY e.EmployeeID, e.EmployeeName, b.BranchName;


-- =============================================================
-- 10. STORED PROCEDURES
-- =============================================================
DELIMITER //

-- ----------------------------------------------------------
-- sp_Deposit: nạp tiền vào tài khoản
-- ----------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_Deposit //
CREATE PROCEDURE sp_Deposit(
    IN p_AccountID  INT,
    IN p_Amount     DECIMAL(18,2),
    IN p_Desc       VARCHAR(255)
)
BEGIN
    DECLARE v_Status VARCHAR(10);

    SELECT Status INTO v_Status
    FROM   Accounts WHERE AccountID = p_AccountID;

    IF v_Status IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'ERROR: Account not found';
    ELSEIF v_Status != 'Active' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'ERROR: Account is not Active';
    ELSEIF p_Amount <= 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'ERROR: Amount must be greater than 0';
    ELSE
        START TRANSACTION;
            UPDATE Accounts
               SET Balance = Balance + p_Amount
             WHERE AccountID = p_AccountID;

            INSERT INTO Transactions
                   (ToAccountID, TransactionType, Amount, Description)
            VALUES (p_AccountID, 'Deposit', p_Amount, p_Desc);
        COMMIT;
        SELECT CONCAT('Deposit successful. AccountID=', p_AccountID,
                      ', Amount=', p_Amount) AS Result;
    END IF;
END //


-- ----------------------------------------------------------
-- sp_Withdrawal: rút tiền
-- ----------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_Withdrawal //
CREATE PROCEDURE sp_Withdrawal(
    IN p_AccountID  INT,
    IN p_Amount     DECIMAL(18,2),
    IN p_Desc       VARCHAR(255)
)
BEGIN
    DECLARE v_Status  VARCHAR(10);
    DECLARE v_Balance DECIMAL(18,2);

    SELECT Status, Balance INTO v_Status, v_Balance
    FROM   Accounts WHERE AccountID = p_AccountID;

    IF v_Status IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'ERROR: Account not found';
    ELSEIF v_Status != 'Active' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'ERROR: Account is not Active';
    ELSEIF p_Amount <= 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'ERROR: Amount must be greater than 0';
    ELSEIF v_Balance < p_Amount THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'ERROR: Insufficient balance';
    ELSE
        START TRANSACTION;
            UPDATE Accounts
               SET Balance = Balance - p_Amount
             WHERE AccountID = p_AccountID;

            INSERT INTO Transactions
                   (FromAccountID, TransactionType, Amount, Description)
            VALUES (p_AccountID, 'Withdrawal', p_Amount, p_Desc);
        COMMIT;
        SELECT CONCAT('Withdrawal successful. AccountID=', p_AccountID,
                      ', Amount=', p_Amount) AS Result;
    END IF;
END //


-- ----------------------------------------------------------
-- sp_Transfer: chuyển khoản 
-- ----------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_Transfer //
CREATE PROCEDURE sp_Transfer(
    IN p_FromID  INT,
    IN p_ToID    INT,
    IN p_Amount  DECIMAL(18,2),
    IN p_Desc    VARCHAR(255)
)
BEGIN
    DECLARE v_FromStatus  VARCHAR(10);
    DECLARE v_ToStatus    VARCHAR(10);
    DECLARE v_FromBalance DECIMAL(18,2);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    IF p_FromID = p_ToID THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'ERROR: Cannot transfer to the same account';
    END IF;

    SELECT Status, Balance INTO v_FromStatus, v_FromBalance
    FROM   Accounts WHERE AccountID = p_FromID FOR UPDATE;

    SELECT Status INTO v_ToStatus
    FROM   Accounts WHERE AccountID = p_ToID FOR UPDATE;

    IF v_FromStatus IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ERROR: Source account not found';
    ELSEIF v_ToStatus IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ERROR: Destination account not found';
    ELSEIF v_FromStatus != 'Active' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ERROR: Source account is not Active';
    ELSEIF v_ToStatus != 'Active' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ERROR: Destination account is not Active';
    ELSEIF p_Amount <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ERROR: Amount must be greater than 0';
    ELSEIF v_FromBalance < p_Amount THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ERROR: Insufficient balance';
    ELSE
        START TRANSACTION;
            UPDATE Accounts SET Balance = Balance - p_Amount WHERE AccountID = p_FromID;
            UPDATE Accounts SET Balance = Balance + p_Amount WHERE AccountID = p_ToID;

            INSERT INTO Transactions
                   (FromAccountID, ToAccountID, TransactionType, Amount, Description)
            VALUES (p_FromID, p_ToID, 'Transfer', p_Amount, p_Desc);
        COMMIT;
        SELECT CONCAT('Transfer successful. From=', p_FromID,
                      ' To=', p_ToID, ', Amount=', p_Amount) AS Result;
    END IF;
END //


-- ----------------------------------------------------------
-- sp_CloseAccount: đóng tài khoản
-- ----------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_CloseAccount //
CREATE PROCEDURE sp_CloseAccount(
    IN p_AccountID INT
)
BEGIN
    DECLARE v_Balance DECIMAL(18,2);
    DECLARE v_Status  VARCHAR(10);

    SELECT Balance, Status INTO v_Balance, v_Status
    FROM   Accounts WHERE AccountID = p_AccountID;

    IF v_Status IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ERROR: Account not found';
    ELSEIF v_Status = 'Closed' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ERROR: Account already closed';
    ELSEIF v_Balance > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'ERROR: Cannot close account with remaining balance';
    ELSE
        UPDATE Accounts
           SET Status    = 'Closed',
               CloseDate = CURRENT_DATE
         WHERE AccountID = p_AccountID;
        SELECT CONCAT('Account ', p_AccountID, ' closed successfully') AS Result;
    END IF;
END //

DELIMITER ;


-- =============================================================
-- 11. TRIGGERS
-- =============================================================
DELIMITER //

-- ----------------------------------------------------------
-- TRIGGER 1: Kiểm tra logic Deposit / Withdrawal / Transfer
-- ----------------------------------------------------------
DROP TRIGGER IF EXISTS trg_CheckTransactionLogic //
CREATE TRIGGER trg_CheckTransactionLogic
BEFORE INSERT ON Transactions
FOR EACH ROW
BEGIN
    IF NEW.TransactionType = 'Deposit' THEN
        IF NEW.ToAccountID IS NULL OR NEW.FromAccountID IS NOT NULL THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'TRIGGER ERROR: Deposit requires ToAccountID only';
        END IF;
    ELSEIF NEW.TransactionType = 'Withdrawal' THEN
        IF NEW.FromAccountID IS NULL OR NEW.ToAccountID IS NOT NULL THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'TRIGGER ERROR: Withdrawal requires FromAccountID only';
        END IF;
    ELSEIF NEW.TransactionType = 'Transfer' THEN
        IF NEW.FromAccountID IS NULL OR NEW.ToAccountID IS NULL THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'TRIGGER ERROR: Transfer requires both FromAccountID and ToAccountID';
        END IF;
        IF NEW.FromAccountID = NEW.ToAccountID THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'TRIGGER ERROR: Cannot transfer to the same account';
        END IF;
    END IF;
END //


-- ----------------------------------------------------------
-- TRIGGER 2: Chặn rút/chuyển khoản khi số dư không đủ
-- ----------------------------------------------------------
DROP TRIGGER IF EXISTS trg_PreventOverdraft //
CREATE TRIGGER trg_PreventOverdraft
BEFORE INSERT ON Transactions
FOR EACH ROW
BEGIN
    DECLARE v_Balance DECIMAL(18,2);

    IF NEW.TransactionType IN ('Withdrawal', 'Transfer') THEN
        SELECT Balance INTO v_Balance
        FROM   Accounts
        WHERE  AccountID = NEW.FromAccountID FOR UPDATE;

        IF v_Balance < NEW.Amount THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'TRIGGER ERROR: Insufficient balance — overdraft not allowed';
        END IF;
    END IF;
END //


-- ----------------------------------------------------------
-- TRIGGER 3: Tự động ghi AuditLog sau mỗi giao dịch
-- ----------------------------------------------------------
DROP TRIGGER IF EXISTS trg_AutoAuditLog //
CREATE TRIGGER trg_AutoAuditLog
AFTER INSERT ON Transactions
FOR EACH ROW
BEGIN
    DECLARE v_Severity ENUM('LOW','MEDIUM','HIGH');
    DECLARE v_Message  VARCHAR(500);

    -- Xác định mức độ nghiêm trọng theo số tiền
    IF NEW.Amount >= 100000000 THEN          -- >= 100 triệu
        SET v_Severity = 'HIGH';
    ELSEIF NEW.Amount >= 10000000 THEN       -- >= 10 triệu
        SET v_Severity = 'MEDIUM';
    ELSE
        SET v_Severity = 'LOW';
    END IF;

    SET v_Message = CONCAT(
        '[', NEW.TransactionType, '] ',
        'TransactionID=', NEW.TransactionID,
        ' | Amount=',     NEW.Amount,
        ' | From=',       IFNULL(NEW.FromAccountID, 'N/A'),
        ' | To=',         IFNULL(NEW.ToAccountID,   'N/A'),
        ' | ', IFNULL(NEW.Description, '')
    );

    INSERT INTO AuditLogs (TransactionID, Severity, Message)
    VALUES (NEW.TransactionID, v_Severity, v_Message);
END //


-- ----------------------------------------------------------
-- TRIGGER 4: Chặn giao dịch trên tài khoản đã đóng/đóng băng
-- ----------------------------------------------------------
DROP TRIGGER IF EXISTS trg_BlockInactiveAccount //
CREATE TRIGGER trg_BlockInactiveAccount
BEFORE INSERT ON Transactions
FOR EACH ROW
BEGIN
    DECLARE v_FromStatus VARCHAR(10);
    DECLARE v_ToStatus   VARCHAR(10);

    IF NEW.FromAccountID IS NOT NULL THEN
        SELECT Status INTO v_FromStatus
        FROM   Accounts WHERE AccountID = NEW.FromAccountID;
        IF v_FromStatus != 'Active' THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'TRIGGER ERROR: Source account is not Active';
        END IF;
    END IF;

    IF NEW.ToAccountID IS NOT NULL THEN
        SELECT Status INTO v_ToStatus
        FROM   Accounts WHERE AccountID = NEW.ToAccountID;
        IF v_ToStatus != 'Active' THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'TRIGGER ERROR: Destination account is not Active';
        END IF;
    END IF;
END //

DELIMITER ;


-- =============================================================
-- 12. USER DEFINED FUNCTIONS
-- =============================================================
DELIMITER //

-- Tính lãi suất đơn giản
DROP FUNCTION IF EXISTS fn_CalcInterest //
CREATE FUNCTION fn_CalcInterest(
    p_Balance DECIMAL(18,2),
    p_Rate    DECIMAL(6,4),    
    p_Days    INT
) RETURNS DECIMAL(18,2)
DETERMINISTIC
BEGIN
    RETURN ROUND(p_Balance * p_Rate * p_Days / 365, 2);
END //

-- Kiểm tra số dư tối thiểu
DROP FUNCTION IF EXISTS fn_CheckMinBalance //
CREATE FUNCTION fn_CheckMinBalance(
    p_AccountID INT,
    p_MinAmount DECIMAL(18,2)
) RETURNS BOOLEAN
READS SQL DATA
BEGIN
    DECLARE v_Balance DECIMAL(18,2);
    SELECT Balance INTO v_Balance
    FROM   Accounts WHERE AccountID = p_AccountID;
    RETURN v_Balance >= p_MinAmount;
END //

DELIMITER ;


-- =============================================================
-- RESET
-- =============================================================
SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;



