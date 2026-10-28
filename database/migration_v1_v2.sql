
USE bank;

ALTER TABLE TRANSACTION_RECORD
    ADD CONSTRAINT chk_transaction_amount CHECK (AMOUNT > 0),
    ADD CONSTRAINT chk_transaction_type CHECK (TYPE IN ('C', 'D'));

ALTER TABLE ACCOUNT
    ADD CONSTRAINT chk_account_overdraft CHECK (BALANCE >= -OVERDRAFT);

CREATE INDEX idx_transaction_account_time
    ON TRANSACTION_RECORD (ACCOUNT_ID, TRANSACTION_TIME);

CREATE USER 'bank_app'@'localhost' IDENTIFIED BY 'HIER_PASSWORT_EINSETZEN';
GRANT SELECT ON bank.CUSTOMER TO 'bank_app'@'localhost';
GRANT SELECT, UPDATE ON bank.ACCOUNT TO 'bank_app'@'localhost';
GRANT SELECT, INSERT ON bank.TRANSACTION_RECORD TO 'bank_app'@'localhost';
