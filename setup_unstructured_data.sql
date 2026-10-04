-- =============================================================
-- SETUP UNSTRUCTURED DATA: Upload PDFs, Parse, Insert into Search
-- Run this ENTIRE script in Snowsight (Snowflake UI)
-- =============================================================

USE ROLE ACCOUNTADMIN;
USE DATABASE RISK_COPILOT_DB;
USE SCHEMA RISK_COPILOT;
USE WAREHOUSE COMPUTE_WH;

-- Step 1: Add SOURCE_FILE column to track PDF origin
ALTER TABLE REGULATORY_POLICIES ADD COLUMN IF NOT EXISTS SOURCE_FILE VARCHAR(200);

-- Step 2: Create internal stage for regulatory documents
CREATE STAGE IF NOT EXISTS REGULATORY_DOCS_STAGE
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Stage for regulatory PDF documents used by Cortex Search';

-- Step 3: Upload PDFs using PUT (run each separately in Snowsight SQL worksheet)
-- NOTE: In Snowsight, use the upload button on the stage, or run these PUT commands:
PUT 'file://C:/Users/balun/risk-copilot/regulatory_docs/PMLA_2002_Guidelines.pdf' @REGULATORY_DOCS_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT 'file://C:/Users/balun/risk-copilot/regulatory_docs/RBI_KYC_Master_Direction_2016.pdf' @REGULATORY_DOCS_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT 'file://C:/Users/balun/risk-copilot/regulatory_docs/FATF_Recommendations_2023.pdf' @REGULATORY_DOCS_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT 'file://C:/Users/balun/risk-copilot/regulatory_docs/Basel_III_Liquidity_Framework.pdf' @REGULATORY_DOCS_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT 'file://C:/Users/balun/risk-copilot/regulatory_docs/RBI_Fraud_Reporting_Framework.pdf' @REGULATORY_DOCS_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;

-- Step 4: Verify uploads
LIST @REGULATORY_DOCS_STAGE;

-- Step 5: Parse PDFs using AI_PARSE_DOCUMENT and insert into REGULATORY_POLICIES
-- This extracts text from each PDF and inserts as new rows with SOURCE_FILE reference

-- PMLA 2002
INSERT INTO REGULATORY_POLICIES (REGULATION_NAME, SECTION_TITLE, CATEGORY, CONTENT, SOURCE_FILE)
SELECT 
    'PMLA 2002 (Parsed from PDF)' AS REGULATION_NAME,
    'Full Document Text' AS SECTION_TITLE,
    'AML' AS CATEGORY,
    SNOWFLAKE.CORTEX.AI_PARSE_DOCUMENT(
        @REGULATORY_DOCS_STAGE, 
        'PMLA_2002_Guidelines.pdf',
        {'mode': 'LAYOUT'}
    ):content::VARCHAR AS CONTENT,
    'PMLA_2002_Guidelines.pdf' AS SOURCE_FILE;

-- RBI KYC Master Direction
INSERT INTO REGULATORY_POLICIES (REGULATION_NAME, SECTION_TITLE, CATEGORY, CONTENT, SOURCE_FILE)
SELECT 
    'RBI KYC Master Direction 2016 (Parsed from PDF)' AS REGULATION_NAME,
    'Full Document Text' AS SECTION_TITLE,
    'KYC' AS CATEGORY,
    SNOWFLAKE.CORTEX.AI_PARSE_DOCUMENT(
        @REGULATORY_DOCS_STAGE, 
        'RBI_KYC_Master_Direction_2016.pdf',
        {'mode': 'LAYOUT'}
    ):content::VARCHAR AS CONTENT,
    'RBI_KYC_Master_Direction_2016.pdf' AS SOURCE_FILE;

-- FATF Recommendations
INSERT INTO REGULATORY_POLICIES (REGULATION_NAME, SECTION_TITLE, CATEGORY, CONTENT, SOURCE_FILE)
SELECT 
    'FATF Recommendations 2023 (Parsed from PDF)' AS REGULATION_NAME,
    'Full Document Text' AS SECTION_TITLE,
    'AML' AS CATEGORY,
    SNOWFLAKE.CORTEX.AI_PARSE_DOCUMENT(
        @REGULATORY_DOCS_STAGE, 
        'FATF_Recommendations_2023.pdf',
        {'mode': 'LAYOUT'}
    ):content::VARCHAR AS CONTENT,
    'FATF_Recommendations_2023.pdf' AS SOURCE_FILE;

-- Basel III Liquidity Framework
INSERT INTO REGULATORY_POLICIES (REGULATION_NAME, SECTION_TITLE, CATEGORY, CONTENT, SOURCE_FILE)
SELECT 
    'Basel III Liquidity Coverage Ratio (Parsed from PDF)' AS REGULATION_NAME,
    'Full Document Text' AS SECTION_TITLE,
    'LIQUIDITY' AS CATEGORY,
    SNOWFLAKE.CORTEX.AI_PARSE_DOCUMENT(
        @REGULATORY_DOCS_STAGE, 
        'Basel_III_Liquidity_Framework.pdf',
        {'mode': 'LAYOUT'}
    ):content::VARCHAR AS CONTENT,
    'Basel_III_Liquidity_Framework.pdf' AS SOURCE_FILE;

-- RBI Fraud Reporting Framework
INSERT INTO REGULATORY_POLICIES (REGULATION_NAME, SECTION_TITLE, CATEGORY, CONTENT, SOURCE_FILE)
SELECT 
    'RBI Fraud Reporting Framework (Parsed from PDF)' AS REGULATION_NAME,
    'Full Document Text' AS SECTION_TITLE,
    'FRAUD' AS CATEGORY,
    SNOWFLAKE.CORTEX.AI_PARSE_DOCUMENT(
        @REGULATORY_DOCS_STAGE, 
        'RBI_Fraud_Reporting_Framework.pdf',
        {'mode': 'LAYOUT'}
    ):content::VARCHAR AS CONTENT,
    'RBI_Fraud_Reporting_Framework.pdf' AS SOURCE_FILE;

-- Step 6: Update existing rows to mark them as manually-entered (structured data)
UPDATE REGULATORY_POLICIES SET SOURCE_FILE = 'Manual Entry (Structured)' WHERE SOURCE_FILE IS NULL;

-- Step 7: Recreate the Cortex Search Service to include SOURCE_FILE
CREATE OR REPLACE CORTEX SEARCH SERVICE POLICY_SEARCH_SERVICE
    ON CONTENT
    ATTRIBUTES REGULATION_NAME, SECTION_TITLE, CATEGORY, SOURCE_FILE
    WAREHOUSE = COMPUTE_WH
    TARGET_LAG = '1 hour'
    AS (
        SELECT CONTENT, REGULATION_NAME, SECTION_TITLE, CATEGORY, SOURCE_FILE
        FROM RISK_COPILOT_DB.RISK_COPILOT.REGULATORY_POLICIES
    );

-- Step 8: Verify the data
SELECT SOURCE_FILE, COUNT(*) AS ROW_COUNT 
FROM REGULATORY_POLICIES 
GROUP BY SOURCE_FILE 
ORDER BY SOURCE_FILE;

-- Expected output: 25 rows from 'Manual Entry (Structured)' + 5 rows from PDF files = 30 total
