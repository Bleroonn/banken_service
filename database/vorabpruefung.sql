
USE bank;

SELECT VERSION() AS mysql_version;

SELECT COUNT(*) AS buchungen_betrag_ungueltig
FROM TRANSACTION_RECORD
WHERE AMOUNT <= 0;

SELECT COUNT(*) AS buchungen_typ_ungueltig
FROM TRANSACTION_RECORD
WHERE TYPE NOT IN ('C', 'D') OR TYPE IS NULL;

SELECT COUNT(*) AS konten_unter_limit
FROM ACCOUNT
WHERE BALANCE < -OVERDRAFT;

SELECT
    (SELECT COUNT(*) FROM CUSTOMER)           AS anzahl_kunden,
    (SELECT COUNT(*) FROM ACCOUNT)            AS anzahl_konten,
    (SELECT COUNT(*) FROM TRANSACTION_RECORD) AS anzahl_buchungen;
