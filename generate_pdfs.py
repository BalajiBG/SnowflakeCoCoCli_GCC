"""Generate realistic regulatory PDF documents for unstructured data demo."""
import sys
sys.path.insert(0, r"C:\Users\balun\risk-copilot")
from pdf_helper import FPDF
import os

OUT_DIR = r"C:\Users\balun\risk-copilot\regulatory_docs"
os.makedirs(OUT_DIR, exist_ok=True)

docs = [
    {
        "filename": "PMLA_2002_Guidelines.pdf",
        "title": "PREVENTION OF MONEY LAUNDERING ACT, 2002",
        "subtitle": "Guidelines for Banking and Financial Institutions",
        "sections": [
            ("Section 12 - Obligation to Report", [
                "Every banking company, financial institution, and intermediary shall maintain a record of all transactions, the nature and value of which may be prescribed, whether such transactions comprise of a single transaction or a series of transactions integrally connected to each other, and where such series of transactions take place within a month.",
                "The Cash Transaction Report (CTR) threshold is INR 10,00,000 (Ten Lakh Rupees). All cash transactions exceeding this threshold must be reported to the Financial Intelligence Unit - India (FIU-IND) by the 15th day of the succeeding month.",
                "Suspicious Transaction Reports (STR) must be filed within 7 days of the transaction being identified as suspicious. A suspicious transaction includes transactions which give rise to a reasonable ground of suspicion that it may involve proceeds of an offence regardless of the amount involved.",
            ]),
            ("Section 3 - Offence of Money Laundering", [
                "Whosoever directly or indirectly attempts to indulge or knowingly assists or knowingly is a party or is actually involved in any process or activity connected with the proceeds of crime including its concealment, possession, acquisition or use and projecting or claiming it as untainted property shall be guilty of offence of money laundering.",
                "The punishment for money laundering under this act is rigorous imprisonment for a term which shall not be less than three years but which may extend to seven years and shall also be liable to fine.",
                "Structuring transactions to avoid reporting thresholds is specifically identified as an indicator of money laundering activity. Multiple cash deposits just below the INR 10 lakh threshold within a short period constitutes structuring.",
            ]),
            ("Section 66 - Tipping Off Prohibition", [
                "No person including a banking company, financial institution, or intermediary shall disclose to any person including the owner of the property or depositor or client, that information relating to such person has been reported under section 12 to the Director or any competent authority.",
                "Any person who contravenes the provisions shall be punishable with imprisonment for a term which may extend to three years and shall also be liable to fine which may extend to twenty-five thousand rupees.",
            ]),
            ("Section 50 - Powers of Director", [
                "The Director shall, for the purpose of this Act, have the same powers as are vested in a civil court under the Code of Civil Procedure, 1908 while trying a suit in respect of discovery and inspection, enforcing the attendance of any person and examining on oath, and compelling the production of records.",
            ]),
        ],
    },
    {
        "filename": "RBI_KYC_Master_Direction_2016.pdf",
        "title": "RBI MASTER DIRECTION ON KYC",
        "subtitle": "Know Your Customer (KYC) Direction, 2016 (Updated 2024)",
        "sections": [
            ("Chapter I - Preliminary", [
                "These Directions are issued under Section 35A of the Banking Regulation Act, 1949, Section 36(1)(a) of the Banking Regulation Act, 1949, and Rule 9 of the Prevention of Money-Laundering (Maintenance of Records) Rules, 2005.",
                "These directions apply to all Regulated Entities (REs) including Scheduled Commercial Banks, Regional Rural Banks, Local Area Banks, All India Financial Institutions, Non-Banking Financial Companies, and Payment System Operators.",
            ]),
            ("Chapter IV - Customer Due Diligence (CDD)", [
                "Banks shall apply Customer Due Diligence measures when establishing a business relationship, carrying out occasional transactions above the prescribed threshold, when there is a suspicion of money laundering or terrorist financing, or when there are doubts about the adequacy of previously obtained customer identification data.",
                "Enhanced Due Diligence (EDD) shall be applied for customers classified as high risk, including Politically Exposed Persons (PEPs), customers from high-risk jurisdictions identified by FATF, customers with complex or unusually large transactions, and customers with opaque ownership structures.",
                "KYC review frequency: Annual review for high-risk customers, biannual review for medium-risk customers, and review every five years for low-risk customers. Failure to complete KYC review within the prescribed period may result in account restrictions.",
            ]),
            ("Chapter V - Enhanced Due Diligence for High Risk Customers", [
                "For PEPs (Politically Exposed Persons), banks must obtain senior management approval for establishing or continuing the business relationship, take reasonable measures to establish the source of wealth and source of funds, and conduct enhanced ongoing monitoring of the business relationship.",
                "For customers from high-risk jurisdictions, banks shall apply countermeasures proportionate to the risks. This includes enhanced scrutiny of the business relationship and its purpose, increased monitoring and reporting of transactions, and limiting business relationships or financial transactions.",
                "Shell companies with opaque beneficial ownership structures require the bank to identify and verify the identity of the beneficial owner holding more than 25% ownership or control, obtain information on the nature of the business, and conduct ongoing monitoring.",
            ]),
            ("Chapter VIII - Record Maintenance", [
                "Banks shall maintain all records of transactions for a minimum period of five years from the date of transaction. Records pertaining to the identity of clients shall be maintained for a period of five years after the business relationship has ended.",
            ]),
        ],
    },
    {
        "filename": "FATF_Recommendations_2023.pdf",
        "title": "FATF RECOMMENDATIONS",
        "subtitle": "International Standards on Combating Money Laundering and Financing of Terrorism & Proliferation (2023 Update)",
        "sections": [
            ("Recommendation 10 - Customer Due Diligence", [
                "Financial institutions should be prohibited from keeping anonymous accounts or accounts in obviously fictitious names. Financial institutions should be required to undertake customer due diligence measures when establishing business relationships, carrying out occasional transactions above the applicable designated threshold (USD 15,000), or when there is a suspicion of money laundering or terrorist financing.",
                "The CDD measures to be taken include identifying the customer and verifying the customer's identity using reliable, independent source documents, identifying the beneficial owner, understanding and obtaining information on the purpose and intended nature of the business relationship, and conducting ongoing due diligence on the business relationship.",
            ]),
            ("Recommendation 16 - Wire Transfers", [
                "Countries should ensure that financial institutions include required and accurate originator information, and required beneficiary information, on wire transfers and related messages, and that the information remains with the wire transfer or related message throughout the payment chain.",
                "For cross-border wire transfers above USD 1,000, the ordering financial institution should include the name of the originator, the originator account number, the originator's address or national identity number or date and place of birth, and the name of the beneficiary and beneficiary account number.",
            ]),
            ("Recommendation 20 - Reporting of Suspicious Transactions", [
                "If a financial institution suspects or has reasonable grounds to suspect that funds are the proceeds of a criminal activity, or are related to terrorist financing, it should be required, by law, to report promptly its suspicions to the financial intelligence unit (FIU).",
                "Financial institutions should report suspicious transactions regardless of the amount involved. Round-tripping of funds through multiple jurisdictions, use of shell companies, rapid movement across accounts with no clear economic purpose, and transactions inconsistent with the customer's known profile are key red flags.",
                "The reporting obligation applies to attempted transactions that were not completed, and to funds where there are reasonable grounds to suspect they are linked to or related to or to be used for terrorism, terrorist acts or by terrorist organisations.",
            ]),
            ("Recommendation 26 - Regulation and Supervision of Financial Institutions", [
                "Countries should ensure that financial institutions are subject to adequate regulation and supervision and are effectively implementing the FATF Recommendations. Supervisors should have adequate powers to supervise or monitor, and ensure compliance by financial institutions with requirements to combat money laundering and terrorist financing.",
            ]),
        ],
    },
    {
        "filename": "Basel_III_Liquidity_Framework.pdf",
        "title": "BASEL III: LIQUIDITY COVERAGE RATIO",
        "subtitle": "Basel Committee on Banking Supervision - Liquidity Risk Framework",
        "sections": [
            ("Part 1 - The Liquidity Coverage Ratio", [
                "The objective of the LCR is to promote the short-term resilience of the liquidity risk profile of banks. It does this by ensuring that banks have an adequate stock of unencumbered high-quality liquid assets (HQLA) that can be converted easily and immediately in private markets into cash to meet their liquidity needs for a 30 calendar day liquidity stress scenario.",
                "The LCR standard requires that the value of the ratio be no lower than 100% (i.e. the stock of HQLA should at least equal total net cash outflows). Banks are expected to meet this requirement on an ongoing basis and hold a stock of unencumbered HQLA as a defence against the potential onset of liquidity stress.",
                "LCR = Stock of HQLA / Total net cash outflows over the next 30 calendar days >= 100%. Daily monitoring is required when the ratio falls below 110% and the bank must present a plan to restore compliance.",
            ]),
            ("Part 2 - High Quality Liquid Assets (HQLA)", [
                "Level 1 assets can be included without limit and include coins and banknotes, qualifying central bank reserves, qualifying marketable securities from sovereigns, central banks, PSEs, and multilateral development banks. Level 1 assets are not subject to a haircut.",
                "Level 2 assets can comprise no more than 40% of the total stock. Level 2A assets are subject to a 15% haircut and include qualifying corporate debt securities rated AA- or higher and qualifying covered bonds rated AA- or higher. Level 2B assets are subject to a 25-50% haircut.",
            ]),
            ("Part 3 - Cash Outflows", [
                "Total expected cash outflows are calculated by multiplying outstanding balances of various categories by the rates at which they are expected to run off or be drawn down. Retail stable deposits have a run-off rate of 5%, less stable deposits 10%, and unsecured wholesale funding from non-financial corporates 40%.",
                "Banks must monitor concentration of funding sources and establish limits on single counterparty exposure. Large deposit withdrawals and sudden outflows from institutional investors represent the highest risk categories.",
            ]),
            ("Part 4 - Net Stable Funding Ratio (NSFR)", [
                "The NSFR requires banks to maintain a stable funding profile in relation to the composition of their assets and off-balance sheet activities. The NSFR ratio must be at least 100% on an ongoing basis. NSFR = Available Stable Funding (ASF) / Required Stable Funding (RSF) >= 100%.",
            ]),
        ],
    },
    {
        "filename": "RBI_Fraud_Reporting_Framework.pdf",
        "title": "RBI MASTER DIRECTION ON FRAUDS",
        "subtitle": "Classification and Reporting of Frauds by Commercial Banks and Select FIs",
        "sections": [
            ("Chapter 2 - Classification of Frauds", [
                "Frauds have been classified based on the provisions of the Indian Penal Code (IPC) into the following categories: (a) Misappropriation and criminal breach of trust, (b) Fraudulent encashment through forged instruments, (c) Manipulation of books of account or through fictitious accounts, (d) Unauthorized credit facilities extended for reward or illegal gratification, (e) Cash shortages, and (f) Cheating and forgery.",
                "For the purpose of reporting, frauds are categorized by value: Category 1 - INR 1 lakh and above but less than INR 5 lakh, Category 2 - INR 5 lakh and above but less than INR 25 lakh, Category 3 - INR 25 lakh and above but less than INR 50 crore, Category 4 - INR 50 crore and above but less than INR 100 crore, Category 5 - INR 100 crore and above.",
            ]),
            ("Chapter 3 - Reporting Requirements", [
                "Banks must report all frauds of INR 1 lakh and above to RBI within three weeks of detection. For frauds of INR 100 crore and above, a flash report must be submitted to RBI within one week of detection, followed by a detailed report within three weeks.",
                "Quarterly progress reports must be submitted on all fraud cases of INR 25 lakh and above. The quarterly report should include the status of investigation, recovery made, action taken against the persons involved, and systemic improvements implemented.",
                "Trade-based money laundering (TBML) through over-invoicing, under-invoicing, multiple invoicing, phantom shipments, and transfer pricing manipulation must be specifically monitored in trade finance operations and reported as fraud when detected.",
            ]),
            ("Chapter 4 - Early Warning Signals", [
                "Banks must implement Early Warning Signal (EWS) systems that monitor: unusual transaction patterns deviating from customer profile, frequent changes in authorized signatories, sudden unexplained change in business activity or turnover, frequent change of accounts across banks, large value transactions inconsistent with declared business, and significant deviation from expected transaction volumes.",
                "Red Flag Indicators for trade finance include: significant discrepancies between goods described and goods shipped, unusually complex trade structures with multiple intermediaries, prices significantly above or below market rates, and shipments routed through free trade zones or transshipment points with no economic rationale.",
            ]),
        ],
    },
]

for doc in docs:
    pdf = FPDF()
    pw = pdf.w - 20

    # Title page
    pdf.add_page()
    pdf.ln(30)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(26, 26, 46)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(pw, 7, "CONFIDENTIAL - REGULATORY REFERENCE DOCUMENT", ln=True, align="C", fill=True)
    pdf.ln(15)
    pdf.set_text_color(26, 26, 46)
    pdf.set_font("Helvetica", "B", 20)
    pdf.multi_cell(pw, 10, doc["title"])
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(pw, 8, doc["subtitle"], ln=True)
    pdf.ln(20)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(pw, 5, "For use by compliance officers, AML investigators, and risk management teams.", ln=True)
    pdf.cell(pw, 5, "CoCoIceberg Risk & Compliance Copilot - Regulatory Document Library", ln=True)

    # Content pages
    for section_title, paragraphs in doc["sections"]:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(26, 26, 46)
        pdf.cell(pw, 10, section_title, ln=True)
        pdf.set_draw_color(41, 181, 232)
        pdf.line(10, pdf.get_y(), 10 + pw, pdf.get_y())
        pdf.ln(6)
        pdf.set_font("Helvetica", "", 10)
        for para in paragraphs:
            pdf.multi_cell(pw, 5, para)
            pdf.ln(4)

    path = os.path.join(OUT_DIR, doc["filename"])
    with open(path, "wb") as f:
        f.write(pdf.output())
    print(f"Created: {path} ({len(doc['sections'])} sections)")

print(f"\nAll {len(docs)} PDFs created in {OUT_DIR}")
