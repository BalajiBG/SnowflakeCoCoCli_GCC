-- =============================================================
-- CoCoIceberg — Scale to 500 Customers with Realistic Data
-- Run this ENTIRE script in Snowsight as ACCOUNTADMIN
-- =============================================================
USE ROLE ACCOUNTADMIN;
USE SCHEMA RISK_COPILOT_DB.RISK_COPILOT;

-- =====================================================
-- STEP 1: Clear existing data
-- =====================================================
TRUNCATE TABLE COMPLIANCE_TICKETS;
TRUNCATE TABLE ALERTS;
TRUNCATE TABLE TRANSACTIONS;
TRUNCATE TABLE ACCOUNTS;
TRUNCATE TABLE CUSTOMERS;

-- =====================================================
-- STEP 2: Generate 500 Customers
-- =====================================================
INSERT INTO CUSTOMERS
SELECT
    'CUST' || LPAD(SEQ4()+1, 4, '0') AS CUSTOMER_ID,
    -- Realistic Indian names
    CASE MOD(SEQ4(), 50)
        WHEN 0 THEN 'Rajesh Mehta' WHEN 1 THEN 'Priya Sharma' WHEN 2 THEN 'Amit Patel' WHEN 3 THEN 'Sunita Reddy'
        WHEN 4 THEN 'Vikram Singh' WHEN 5 THEN 'Meera Nair' WHEN 6 THEN 'Arjun Kapoor' WHEN 7 THEN 'Anita Desai'
        WHEN 8 THEN 'Sanjay Gupta' WHEN 9 THEN 'Kavita Iyer' WHEN 10 THEN 'Rohit Joshi' WHEN 11 THEN 'Deepa Menon'
        WHEN 12 THEN 'Suresh Kumar' WHEN 13 THEN 'Lakshmi Rao' WHEN 14 THEN 'Manish Agarwal' WHEN 15 THEN 'Pooja Verma'
        WHEN 16 THEN 'Kiran Bhatt' WHEN 17 THEN 'Nisha Chopra' WHEN 18 THEN 'Arun Pillai' WHEN 19 THEN 'Ritu Saxena'
        WHEN 20 THEN 'Venkat Raman' WHEN 21 THEN 'Swati Mishra' WHEN 22 THEN 'Harish Shetty' WHEN 23 THEN 'Anjali Tiwari'
        WHEN 24 THEN 'Prakash Nambiar' WHEN 25 THEN 'Divya Bhat' WHEN 26 THEN 'Gaurav Malhotra' WHEN 27 THEN 'Rekha Jain'
        WHEN 28 THEN 'Nitin Kulkarni' WHEN 29 THEN 'Sneha Parekh' WHEN 30 THEN 'Ashok Banerjee' WHEN 31 THEN 'Bhavna Shah'
        WHEN 32 THEN 'Ramesh Hegde' WHEN 33 THEN 'Usha Pandey' WHEN 34 THEN 'Vivek Chandra' WHEN 35 THEN 'Seema Ahuja'
        WHEN 36 THEN 'Gopal Krishnan' WHEN 37 THEN 'Asha Mathur' WHEN 38 THEN 'Dinesh Bose' WHEN 39 THEN 'Manju Goel'
        WHEN 40 THEN 'Ravi Shankar' WHEN 41 THEN 'Pallavi Das' WHEN 42 THEN 'Ajay Thakur' WHEN 43 THEN 'Shobha Murthy'
        WHEN 44 THEN 'Manoj Sinha' WHEN 45 THEN 'Geeta Reddy' WHEN 46 THEN 'Pramod Yadav' WHEN 47 THEN 'Vandana Dutta'
        WHEN 48 THEN 'Satish Mohan' ELSE 'Lata Mangeshkar'
    END || ' ' || LPAD(SEQ4()+1, 3, '0') AS FULL_NAME,
    -- Customer type distribution: 70% Individual, 20% Corporate, 10% HNI
    CASE WHEN MOD(SEQ4(), 10) < 7 THEN 'INDIVIDUAL'
         WHEN MOD(SEQ4(), 10) < 9 THEN 'CORPORATE'
         ELSE 'HNI' END AS CUSTOMER_TYPE,
    -- KYC risk: 40% LOW, 25% MEDIUM, 20% HIGH, 15% VERY_HIGH
    CASE WHEN UNIFORM(1, 100, RANDOM()) <= 40 THEN 'LOW'
         WHEN UNIFORM(1, 100, RANDOM()) <= 65 THEN 'MEDIUM'
         WHEN UNIFORM(1, 100, RANDOM()) <= 85 THEN 'HIGH'
         ELSE 'VERY_HIGH' END AS KYC_RISK_TIER,
    -- PEP: ~5%
    CASE WHEN UNIFORM(1, 100, RANDOM()) <= 5 THEN TRUE ELSE FALSE END AS IS_PEP,
    -- Jurisdictions
    CASE MOD(SEQ4(), 12)
        WHEN 0 THEN 'Mumbai' WHEN 1 THEN 'Delhi' WHEN 2 THEN 'Chennai' WHEN 3 THEN 'Bangalore'
        WHEN 4 THEN 'Hyderabad' WHEN 5 THEN 'Kolkata' WHEN 6 THEN 'Ahmedabad' WHEN 7 THEN 'Pune'
        WHEN 8 THEN 'Jaipur' WHEN 9 THEN 'Kochi' WHEN 10 THEN 'Dubai' ELSE 'Singapore'
    END AS JURISDICTION,
    CASE MOD(SEQ4(), 15)
        WHEN 0 THEN 'Software Engineer' WHEN 1 THEN 'Doctor' WHEN 2 THEN 'Teacher' WHEN 3 THEN 'Businessman'
        WHEN 4 THEN 'Politician' WHEN 5 THEN 'Jeweler' WHEN 6 THEN 'Real Estate Developer' WHEN 7 THEN 'Film Producer'
        WHEN 8 THEN 'Import/Export' WHEN 9 THEN 'Retired' WHEN 10 THEN 'Lawyer' WHEN 11 THEN 'Chartered Accountant'
        WHEN 12 THEN 'Fintech Founder' WHEN 13 THEN 'Shell Company' ELSE 'Consultant'
    END AS OCCUPATION,
    CASE MOD(SEQ4(), 8)
        WHEN 0 THEN 'Salary' WHEN 1 THEN 'Business income' WHEN 2 THEN 'Professional income'
        WHEN 3 THEN 'Property sales' WHEN 4 THEN 'Trade finance' WHEN 5 THEN 'Venture capital'
        WHEN 6 THEN 'Political donations' ELSE 'Unknown'
    END AS SOURCE_OF_FUNDS,
    -- Sanctions: ~3%
    CASE WHEN UNIFORM(1, 100, RANDOM()) <= 3 THEN TRUE ELSE FALSE END AS SANCTIONS_MATCH,
    -- Adverse media: ~8%
    CASE WHEN UNIFORM(1, 100, RANDOM()) <= 8 THEN TRUE ELSE FALSE END AS ADVERSE_MEDIA_FLAG,
    ROUND(UNIFORM(500000, 100000000, RANDOM()), 2) AS ANNUAL_INCOME,
    DATEADD('DAY', -UNIFORM(365, 2500, RANDOM()), CURRENT_DATE()) AS ONBOARDING_DATE,
    DATEADD('DAY', -UNIFORM(1, 400, RANDOM()), CURRENT_DATE()) AS LAST_KYC_REVIEW
FROM TABLE(GENERATOR(ROWCOUNT => 500));

-- =====================================================
-- STEP 3: Generate ~1500 Accounts (avg 3 per customer)
-- =====================================================
INSERT INTO ACCOUNTS
SELECT
    'ACC' || LPAD(SEQ4()+1, 5, '0') AS ACCOUNT_ID,
    'CUST' || LPAD(MOD(SEQ4(), 500)+1, 4, '0') AS CUSTOMER_ID,
    CASE MOD(SEQ4(), 7)
        WHEN 0 THEN 'SAVINGS' WHEN 1 THEN 'CURRENT' WHEN 2 THEN 'SAVINGS'
        WHEN 3 THEN 'FIXED_DEPOSIT' WHEN 4 THEN 'CURRENT' WHEN 5 THEN 'TRADE_FINANCE'
        ELSE 'NOSTRO'
    END AS ACCOUNT_TYPE,
    CASE WHEN MOD(SEQ4(), 8) = 0 THEN 'USD' ELSE 'INR' END AS CURRENCY,
    ROUND(UNIFORM(10000, 50000000, RANDOM()), 2) AS CURRENT_BALANCE,
    CASE WHEN MOD(SEQ4(), 3) = 0 THEN ROUND(UNIFORM(100000, 25000000, RANDOM()), 2) ELSE 0 END AS CREDIT_LIMIT,
    CASE WHEN UNIFORM(1, 100, RANDOM()) <= 92 THEN 'ACTIVE'
         WHEN UNIFORM(1, 100, RANDOM()) <= 96 THEN 'DORMANT'
         ELSE 'CLOSED' END AS ACCOUNT_STATUS,
    -- NPA: ~8% non-standard
    CASE WHEN UNIFORM(1, 100, RANDOM()) <= 92 THEN 'STANDARD'
         WHEN UNIFORM(1, 100, RANDOM()) <= 96 THEN 'SUBSTANDARD'
         WHEN UNIFORM(1, 100, RANDOM()) <= 99 THEN 'DOUBTFUL'
         ELSE 'LOSS' END AS NPA_STATUS,
    CASE MOD(SEQ4(), 15)
        WHEN 0 THEN 'MUM001' WHEN 1 THEN 'MUM002' WHEN 2 THEN 'DEL001' WHEN 3 THEN 'CHE001'
        WHEN 4 THEN 'BLR001' WHEN 5 THEN 'HYD001' WHEN 6 THEN 'KOL001' WHEN 7 THEN 'AHM001'
        WHEN 8 THEN 'PUN001' WHEN 9 THEN 'JAI001' WHEN 10 THEN 'KOC001' WHEN 11 THEN 'DUB001'
        WHEN 12 THEN 'SGP001' WHEN 13 THEN 'MUM003' ELSE 'DEL002'
    END AS BRANCH_CODE,
    CASE WHEN UNIFORM(1, 100, RANDOM()) <= 5 THEN TRUE ELSE FALSE END AS IS_DORMANT,
    DATEADD('DAY', -UNIFORM(100, 2000, RANDOM()), CURRENT_DATE()) AS OPENED_DATE
FROM TABLE(GENERATOR(ROWCOUNT => 1500));

-- =====================================================
-- STEP 4: Generate ~20000 Transactions
-- =====================================================
INSERT INTO TRANSACTIONS
SELECT
    'TXN' || LPAD(SEQ4()+1, 6, '0') AS TXN_ID,
    'ACC' || LPAD(MOD(SEQ4(), 1500)+1, 5, '0') AS ACCOUNT_ID,
    CASE MOD(SEQ4(), 10)
        WHEN 0 THEN 'CASH_DEPOSIT' WHEN 1 THEN 'WIRE_TRANSFER' WHEN 2 THEN 'WIRE_INCOMING'
        WHEN 3 THEN 'UPI_TRANSFER' WHEN 4 THEN 'EMI_DEBIT' WHEN 5 THEN 'SALARY_CREDIT'
        WHEN 6 THEN 'CHEQUE_BOUNCE' WHEN 7 THEN 'WIRE_TRANSFER' WHEN 8 THEN 'CASH_DEPOSIT'
        ELSE 'WIRE_INCOMING'
    END AS TXN_TYPE,
    DATEADD('MINUTE', -UNIFORM(1, 90*24*60, RANDOM()), CURRENT_TIMESTAMP()) AS TXN_DATE,
    ROUND(UNIFORM(1000, 20000000, RANDOM()), 2) AS AMOUNT,
    CASE WHEN MOD(SEQ4(), 7) = 0 THEN 'USD' ELSE 'INR' END AS CURRENCY,
    CASE MOD(SEQ4(), 20)
        WHEN 0 THEN 'Self' WHEN 1 THEN 'ABC Trading' WHEN 2 THEN 'Global Finance Ltd'
        WHEN 3 THEN 'Metro Bank' WHEN 4 THEN 'Delta Exports' WHEN 5 THEN 'TechCorp India'
        WHEN 6 THEN 'Patel Jewellers' WHEN 7 THEN 'City Hospital' WHEN 8 THEN 'Vendor Payments'
        WHEN 9 THEN 'Panama Trade LLC' WHEN 10 THEN 'Swiss Bank AG' WHEN 11 THEN 'Dubai Gold Souk'
        WHEN 12 THEN 'Hong Kong Metals' WHEN 13 THEN 'BVI Investment Corp' WHEN 14 THEN 'Mauritius Fund LP'
        WHEN 15 THEN 'Cyprus Investments' WHEN 16 THEN 'Lagos Export Ltd' WHEN 17 THEN 'Myanmar Exports'
        WHEN 18 THEN 'Bermuda Reinsurance' ELSE 'Labuan Offshore'
    END AS COUNTERPARTY_NAME,
    CASE MOD(SEQ4(), 15)
        WHEN 0 THEN 'India' WHEN 1 THEN 'India' WHEN 2 THEN 'India' WHEN 3 THEN 'India'
        WHEN 4 THEN 'India' WHEN 5 THEN 'UAE' WHEN 6 THEN 'Singapore' WHEN 7 THEN 'Hong Kong'
        WHEN 8 THEN 'Mauritius' WHEN 9 THEN 'Cayman Islands' WHEN 10 THEN 'Panama'
        WHEN 11 THEN 'BVI' WHEN 12 THEN 'Switzerland' WHEN 13 THEN 'Nigeria' ELSE 'Myanmar'
    END AS COUNTERPARTY_COUNTRY,
    CASE MOD(SEQ4(), 7)
        WHEN 0 THEN 'BRANCH' WHEN 1 THEN 'ONLINE' WHEN 2 THEN 'SWIFT' WHEN 3 THEN 'UPI'
        WHEN 4 THEN 'RTGS' WHEN 5 THEN 'NEFT' ELSE 'NACH'
    END AS CHANNEL,
    CASE MOD(SEQ4(), 6)
        WHEN 0 THEN 'Business' WHEN 1 THEN 'Personal' WHEN 2 THEN 'Trade'
        WHEN 3 THEN 'Investment' WHEN 4 THEN 'Settlement' ELSE 'Salary'
    END AS PURPOSE,
    CASE WHEN MOD(SEQ4(), 10) IN (0, 8) THEN TRUE ELSE FALSE END AS IS_CASH,
    ROUND(UNIFORM(1, 99, RANDOM()), 2) AS RISK_SCORE
FROM TABLE(GENERATOR(ROWCOUNT => 20000));

-- Add structuring-pattern transactions (just below INR 10L threshold) for ~30 suspicious customers
INSERT INTO TRANSACTIONS
SELECT
    'TXNS' || LPAD(SEQ4()+1, 5, '0') AS TXN_ID,
    'ACC' || LPAD(UNIFORM(1, 100, RANDOM()), 5, '0') AS ACCOUNT_ID,
    'CASH_DEPOSIT' AS TXN_TYPE,
    DATEADD('HOUR', -UNIFORM(1, 720, RANDOM()), CURRENT_TIMESTAMP()) AS TXN_DATE,
    ROUND(UNIFORM(900000, 999000, RANDOM()), 2) AS AMOUNT,
    'INR' AS CURRENCY,
    'Self' AS COUNTERPARTY_NAME,
    'India' AS COUNTERPARTY_COUNTRY,
    'BRANCH' AS CHANNEL,
    'Business deposit' AS PURPOSE,
    TRUE AS IS_CASH,
    ROUND(UNIFORM(70, 95, RANDOM()), 2) AS RISK_SCORE
FROM TABLE(GENERATOR(ROWCOUNT => 500));

-- Add velocity burst transactions for ~20 accounts
INSERT INTO TRANSACTIONS
SELECT
    'TXNV' || LPAD(SEQ4()+1, 5, '0') AS TXN_ID,
    'ACC' || LPAD(UNIFORM(1, 50, RANDOM()), 5, '0') AS ACCOUNT_ID,
    CASE WHEN MOD(SEQ4(), 2) = 0 THEN 'WIRE_TRANSFER' ELSE 'WIRE_INCOMING' END AS TXN_TYPE,
    -- Cluster in same hours for velocity detection
    DATEADD('MINUTE', MOD(SEQ4(), 55), DATEADD('HOUR', -UNIFORM(1, 48, RANDOM()), CURRENT_TIMESTAMP())) AS TXN_DATE,
    ROUND(UNIFORM(1000000, 15000000, RANDOM()), 2) AS AMOUNT,
    CASE WHEN MOD(SEQ4(), 3) = 0 THEN 'USD' ELSE 'INR' END AS CURRENCY,
    CASE MOD(SEQ4(), 6)
        WHEN 0 THEN 'Shell Corp Alpha' WHEN 1 THEN 'Offshore Fund Beta' WHEN 2 THEN 'Dubai Trading FZE'
        WHEN 3 THEN 'Singapore Holdings' WHEN 4 THEN 'Cyprus Entity Ltd' ELSE 'BVI Capital Group'
    END AS COUNTERPARTY_NAME,
    CASE MOD(SEQ4(), 6)
        WHEN 0 THEN 'Cayman Islands' WHEN 1 THEN 'BVI' WHEN 2 THEN 'UAE'
        WHEN 3 THEN 'Singapore' WHEN 4 THEN 'Cyprus' ELSE 'Panama'
    END AS COUNTERPARTY_COUNTRY,
    'SWIFT' AS CHANNEL,
    'Trade' AS PURPOSE,
    FALSE AS IS_CASH,
    ROUND(UNIFORM(80, 99, RANDOM()), 2) AS RISK_SCORE
FROM TABLE(GENERATOR(ROWCOUNT => 300));

-- =====================================================
-- STEP 5: Generate ~200 Alerts
-- =====================================================
INSERT INTO ALERTS
SELECT
    'ALT' || LPAD(SEQ4()+1, 4, '0') AS ALERT_ID,
    'CUST' || LPAD(UNIFORM(1, 500, RANDOM()), 4, '0') AS CUSTOMER_ID,
    'ACC' || LPAD(UNIFORM(1, 1500, RANDOM()), 5, '0') AS ACCOUNT_ID,
    CASE MOD(SEQ4(), 8)
        WHEN 0 THEN 'STRUCTURING' WHEN 1 THEN 'ROUND_TRIPPING' WHEN 2 THEN 'RAPID_MOVEMENT'
        WHEN 3 THEN 'PEP_UNUSUAL_ACTIVITY' WHEN 4 THEN 'CONSECUTIVE_BOUNCES'
        WHEN 5 THEN 'LIQUIDITY_STRESS' WHEN 6 THEN 'TRADE_MISPRICING' ELSE 'HAWALA_INDICATORS'
    END AS ALERT_TYPE,
    CASE MOD(SEQ4(), 8)
        WHEN 0 THEN 'AML' WHEN 1 THEN 'AML' WHEN 2 THEN 'AML' WHEN 3 THEN 'AML'
        WHEN 4 THEN 'CREDIT' WHEN 5 THEN 'LIQUIDITY' WHEN 6 THEN 'FRAUD' ELSE 'AML'
    END AS ALERT_CATEGORY,
    CASE WHEN UNIFORM(1, 100, RANDOM()) <= 25 THEN 'CRITICAL'
         WHEN UNIFORM(1, 100, RANDOM()) <= 55 THEN 'HIGH'
         WHEN UNIFORM(1, 100, RANDOM()) <= 80 THEN 'MEDIUM'
         ELSE 'LOW' END AS SEVERITY,
    CASE WHEN UNIFORM(1, 100, RANDOM()) <= 40 THEN 'OPEN'
         WHEN UNIFORM(1, 100, RANDOM()) <= 60 THEN 'UNDER_REVIEW'
         WHEN UNIFORM(1, 100, RANDOM()) <= 75 THEN 'ESCALATED'
         ELSE 'CLOSED' END AS STATUS,
    CASE MOD(SEQ4(), 8)
        WHEN 0 THEN 'Multiple cash deposits just below INR 10 lakh threshold detected. Pattern consistent with structuring.'
        WHEN 1 THEN 'Funds received from offshore jurisdiction routed to another within 48 hours. Round-tripping pattern.'
        WHEN 2 THEN 'Large volumes moved through multiple jurisdictions in under 72 hours. Rapid fund movement detected.'
        WHEN 3 THEN 'PEP customer showing unusual transaction patterns inconsistent with declared income.'
        WHEN 4 THEN 'Multiple consecutive cheque bounces indicating cash flow stress and potential NPA.'
        WHEN 5 THEN 'Daily outflows exceeding 40% of account balance. Liquidity stress indicator triggered.'
        WHEN 6 THEN 'Trade finance invoice amounts significantly deviate from market rates. Potential TBML.'
        ELSE 'Transfer patterns match known hawala network indicators. No clear business purpose.'
    END AS DESCRIPTION,
    CASE MOD(SEQ4(), 8)
        WHEN 0 THEN 'Multiple cash deposits between INR 9L-10L in single day. Structuring to avoid CTR threshold.'
        WHEN 1 THEN 'Cross-border wire pattern: funds in from one jurisdiction, out to another within 48hrs.'
        WHEN 2 THEN 'Wires across 3+ jurisdictions in 72 hours through shell entities. Layering suspected.'
        WHEN 3 THEN 'Transaction volume 5x declared monthly income. PEP with adverse media flags.'
        WHEN 4 THEN 'Consecutive EMI bounces over 3+ months. Account trending toward NPA classification.'
        WHEN 5 THEN 'Outflow-to-balance ratio exceeding 50%. Treasury intervention recommended.'
        WHEN 6 THEN 'Invoice amounts 200-400% above market rates for commodities. Over-invoicing pattern.'
        ELSE 'Transfers to jurisdictions with weak AML controls. No service agreement on file.'
    END AS EVIDENCE_SUMMARY,
    CASE MOD(SEQ4(), 4)
        WHEN 0 THEN 'AML Team' WHEN 1 THEN 'Senior Compliance'
        WHEN 2 THEN 'Credit Team' ELSE 'Treasury'
    END AS ASSIGNED_TO,
    DATEADD('DAY', -UNIFORM(1, 90, RANDOM()), CURRENT_TIMESTAMP()) AS ALERT_DATE,
    CASE WHEN UNIFORM(1, 100, RANDOM()) <= 25
        THEN DATEADD('DAY', -UNIFORM(1, 30, RANDOM()), CURRENT_TIMESTAMP())
        ELSE NULL END AS RESOLVED_DATE
FROM TABLE(GENERATOR(ROWCOUNT => 200));

-- =====================================================
-- STEP 6: Expand Regulatory Policies to 25 docs
-- =====================================================
TRUNCATE TABLE REGULATORY_POLICIES;
INSERT INTO REGULATORY_POLICIES (REGULATION_NAME, SECTION_TITLE, CATEGORY, CONTENT) VALUES
('PMLA 2002','Section 12 - Reporting Requirements','AML','Every banking company shall maintain records of all transactions exceeding INR 10 lakh in cash. Suspicious Transaction Reports (STR) must be filed with FIU-IND within 7 days of identifying suspicious activity. Cash Transaction Reports (CTR) for transactions exceeding INR 10 lakh must be filed monthly by the 15th of the following month.'),
('PMLA 2002','Section 3 - Offence of Money Laundering','AML','Whosoever directly or indirectly attempts to indulge or knowingly assists or is a party to any activity connected with the proceeds of crime and projecting it as untainted property shall be guilty of offence of money laundering. Structuring transactions to avoid reporting thresholds is a specific indicator.'),
('PMLA 2002','Section 66 - Tipping Off Prohibition','AML','No person including banking company, financial institution or intermediary shall disclose to any person including the owner of the property or depositor or client that information relating to such person has been reported to the Director under section 12. Violation carries imprisonment up to 3 years.'),
('RBI Master Direction on KYC','Chapter IV - Customer Due Diligence','KYC','Banks shall apply enhanced due diligence for high risk customers including PEPs, customers from high-risk jurisdictions, and complex ownership structures. KYC review: annual for high-risk, biannual for medium-risk, every 5 years for low-risk.'),
('RBI Master Direction on KYC','Chapter V - Enhanced Due Diligence','KYC','For customers with VERY_HIGH risk classification, banks must obtain senior management approval for establishing business relationship, take reasonable measures to establish source of wealth and funds, and conduct enhanced ongoing monitoring.'),
('RBI Master Direction on KYC','Chapter III - Risk Assessment','KYC','Banks shall carry out risk assessment to identify, assess and take effective measures to mitigate its money laundering and terrorist financing risk. Risk categories: LOW, MEDIUM, HIGH, VERY_HIGH based on customer type, geography, product, and channel.'),
('RBI Circular on Fraud Reporting','Fraud Classification and Reporting','FRAUD','Banks must report all frauds of INR 1 lakh and above to RBI within 3 weeks of detection. Frauds of INR 100 crore and above must be reported immediately. Trade-based money laundering through mispricing must be specifically monitored.'),
('RBI Circular on Fraud Reporting','Early Warning Signals','FRAUD','Banks should maintain early warning signal (EWS) systems covering: unusual transaction patterns, frequent changes in authorized signatories, sudden change in business activity, frequent change of accounts, and deviation from expected transaction volumes.'),
('Basel III LCR Framework','Liquidity Coverage Ratio','LIQUIDITY','Banks must maintain HQLA to meet 30-day net cash outflow under stress. LCR = Stock of HQLA / Total net cash outflows over 30 days >= 100%. Daily monitoring required when ratio falls below 110%.'),
('Basel III NSFR Framework','Net Stable Funding Ratio','LIQUIDITY','NSFR requires banks to maintain a stable funding profile in relation to their assets and off-balance sheet activities. NSFR = Available Stable Funding / Required Stable Funding >= 100%. Addresses funding risk over a one-year time horizon.'),
('RBI Master Direction on NPA','Income Recognition and Asset Classification','CREDIT','An asset is NPA if interest/principal overdue > 90 days. NPA classification: Substandard (up to 12 months), Doubtful (beyond 12 months), Loss (identified but not written off). Provisioning: 15% Substandard, 25-100% Doubtful, 100% Loss.'),
('RBI Master Direction on NPA','Restructuring of Advances','CREDIT','Restructured accounts shall be classified as substandard for a minimum period of 12 months from the date of restructuring. In case of accounts where the restructuring is done more than once, the account shall be classified as NPA.'),
('FATF Recommendation 20','Reporting of Suspicious Transactions','AML','Financial institutions should file STR with FIU if they suspect funds are proceeds of criminal activity or related to terrorist financing, regardless of amount. Round-tripping through multiple jurisdictions is a key red flag.'),
('FATF Recommendation 10','Customer Due Diligence','AML','Financial institutions should identify and verify the identity of the customer. When performing CDD, institutions should identify the beneficial owner and take reasonable measures to verify identity. Ongoing due diligence includes scrutiny of transactions.'),
('FATF Recommendation 16','Wire Transfers','AML','Countries should ensure that financial institutions include required and accurate originator and beneficiary information on wire transfers. The ordering institution should obtain and maintain information on the originator and the beneficiary.'),
('RBI Guidelines on Hawala','Unauthorized Foreign Exchange Transactions','AML','Hawala transactions bypass formal banking channels and are illegal under FEMA. Indicators: transfers to jurisdictions with weak AML controls, no economic purpose, shell companies, rapid multi-account movement.'),
('Companies Act 2013','Section 90 - Beneficial Ownership','COMPLIANCE','Every company shall maintain register of significant beneficial owners. Shell companies with opaque ownership, especially offshore, must undergo enhanced scrutiny. Beneficial owners holding >25% must be identified and verified.'),
('SEBI Insider Trading Regulations','Prevention of Insider Trading','FRAUD','No insider shall trade in securities when in possession of unpublished price sensitive information. Unusual trading patterns around corporate announcements warrant investigation.'),
('RBI Prompt Corrective Action','Framework for Stressed Banks','CREDIT','RBI may invoke PCA framework if bank breaches thresholds on: Capital to risk-weighted assets ratio below 10.25%, NPA ratio above 6%, Return on Assets below 0.25% for two consecutive years. Actions include restriction on dividend, branch expansion, and management compensation.'),
('Indian Penal Code','Section 420 - Cheating and Dishonesty','FRAUD','Whoever cheats and thereby dishonestly induces the person deceived to deliver any property shall be punished with imprisonment up to 7 years and fine. Applicable to trade-based money laundering and invoice fraud schemes.'),
('FEMA 1999','Section 3 - Dealing in Foreign Exchange','AML','No person shall deal in or transfer any foreign exchange or foreign security to any person not being an authorised dealer or authorised money changer. Violations attract penalties up to thrice the sum involved.'),
('RBI Circular on Digital Lending','Guidelines on Digital Lending','COMPLIANCE','All digital lending must be done through regulated entities. Customer data protection, fair practices code compliance, and transparent disclosure of terms are mandatory. UPI and online lending platforms must follow these guidelines.'),
('IRDAI AML Guidelines','Anti-Money Laundering Guidelines for Insurers','AML','Insurance companies shall verify identity of all customers and maintain records. Suspicious transactions in insurance sector include: unusually large cash premium payments, frequent policy lapses and reissuances, and assignments to unrelated third parties.'),
('RBI on Trade Finance','Guidelines on Trade Based Money Laundering','FRAUD','Banks must exercise due diligence in trade finance transactions. Red flags include: over/under invoicing, multiple invoicing, over/short shipment, phantom shipments, and transfer pricing abuse. Trade finance departments should have dedicated TBML monitoring.'),
('Basel Committee','Principles for Sound Management of Operational Risk','COMPLIANCE','Banks should have a well documented assessment methodology to assess operational risks across all material products, activities, processes and systems. Internal controls should address identified risks including fraud, AML compliance failures, and unauthorized trading.');

-- =====================================================
-- STEP 7: Refresh the Dynamic Table
-- =====================================================
ALTER DYNAMIC TABLE RISK_COPILOT_DB.RISK_COPILOT.DT_TXN_VELOCITY_MONITOR REFRESH;

-- =====================================================
-- STEP 8: Verify counts
-- =====================================================
SELECT 'CUSTOMERS' AS TBL, COUNT(*) AS CNT FROM CUSTOMERS
UNION ALL SELECT 'ACCOUNTS', COUNT(*) FROM ACCOUNTS
UNION ALL SELECT 'TRANSACTIONS', COUNT(*) FROM TRANSACTIONS
UNION ALL SELECT 'ALERTS', COUNT(*) FROM ALERTS
UNION ALL SELECT 'REGULATORY_POLICIES', COUNT(*) FROM REGULATORY_POLICIES
UNION ALL SELECT 'V_AML_SCORING', COUNT(*) FROM V_AML_SCORING
UNION ALL SELECT 'V_FRAUD_SIGNALS', COUNT(*) FROM V_FRAUD_SIGNALS
UNION ALL SELECT 'V_CREDIT_RISK', COUNT(*) FROM V_CREDIT_RISK
UNION ALL SELECT 'V_LIQUIDITY_RISK', COUNT(*) FROM V_LIQUIDITY_RISK
UNION ALL SELECT 'DT_VELOCITY_ANOMALIES', COUNT(*) FROM DT_TXN_VELOCITY_MONITOR WHERE VELOCITY_FLAG != 'NORMAL'
ORDER BY TBL;
