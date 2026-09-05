"""Golden Evaluation Benchmark for SentinelJob AI (Phase 6).
Contains 50 rigorously curated multi-cohort test cases spanning:
- Category A: Clean Legitimate
- Category B: Obvious Scams
- Category C: Impersonation & Typosquatting
- Category D: Borderline & Ambiguous
- Category E: Adversarial & Obfuscated
"""

from typing import Any, Dict, List
from pydantic import BaseModel


class GoldenTestCase(BaseModel):
    id: str
    cohort: str  # "clean_legitimate", "obvious_scam", "impersonation", "borderline", "adversarial"
    title: str
    company_name: str
    text: str
    expected_ground_truth: int  # 0 = Legitimate/Safe, 1 = Fraudulent/Threat
    expected_max_score: int = 100
    expected_min_score: int = 0
    expected_risk_tiers: List[str]  # e.g. ["low"], ["high", "critical"], ["low", "medium"]
    notes: str


GOLDEN_TEST_CASES: List[GoldenTestCase] = [
    # -------------------------------------------------------------------------
    # Cohort A: Clean Legitimate (Ground Truth: 0, Target Risk: LOW)
    # -------------------------------------------------------------------------
    GoldenTestCase(
        id="GOLDEN-A-01",
        cohort="clean_legitimate",
        title="Staff Storage Infrastructure Engineer",
        company_name="Stripe",
        text="Stripe is looking for a Staff Software Engineer to lead the design of our multi-region distributed database systems. Requirements include 7+ years of experience with Go or Java, consensus protocols (Raft/Paxos), and Kubernetes. Comprehensive healthcare, 401(k) matching, and equity. Apply online directly at https://stripe.com/jobs.",
        expected_ground_truth=0,
        expected_max_score=29,
        expected_risk_tiers=["low"],
        notes="Clean tier-1 technology enterprise listing with corporate domain careers page.",
    ),
    GoldenTestCase(
        id="GOLDEN-A-02",
        cohort="clean_legitimate",
        title="Full Stack Software Engineer",
        company_name="Vercel",
        text="Vercel is seeking a Full Stack Software Engineer to work on Next.js developer workflows. Tech stack: TypeScript, React, Rust, and WebAssembly. Standard multi-stage interview process including technical architecture review. Visit https://vercel.com/careers to apply.",
        expected_ground_truth=0,
        expected_max_score=29,
        expected_risk_tiers=["low"],
        notes="Legitimate modern SaaS developer tools company.",
    ),
    GoldenTestCase(
        id="GOLDEN-A-03",
        cohort="clean_legitimate",
        title="Research Intern - Machine Learning",
        company_name="Stanford Artificial Intelligence Laboratory",
        text="Stanford SAIL is accepting applications for Summer Research Interns. Undergraduate or graduate students with strong linear algebra, Python, and PyTorch foundation are encouraged to submit academic transcripts and research statements via https://ai.stanford.edu/admissions.",
        expected_ground_truth=0,
        expected_max_score=29,
        expected_risk_tiers=["low"],
        notes="Academic university research internship with .edu domain.",
    ),
    GoldenTestCase(
        id="GOLDEN-A-04",
        cohort="clean_legitimate",
        title="Cybersecurity Analyst - Public Sector",
        company_name="Cybersecurity and Infrastructure Security Agency",
        text="CISA is hiring a Cybersecurity Analyst in Arlington, VA. Responsibilities include threat intelligence feeds, incident response coordination, and vulnerability management. U.S. Citizenship required. Must obtain Top Secret clearance. Apply at https://www.cisa.gov/careers.",
        expected_ground_truth=0,
        expected_max_score=29,
        expected_risk_tiers=["low"],
        notes="Government public-sector recruitment on .gov domain with formal security clearance.",
    ),
    GoldenTestCase(
        id="GOLDEN-A-05",
        cohort="clean_legitimate",
        title="Senior Site Reliability Engineer (High Salary)",
        company_name="Google Cloud",
        text="Google Cloud Platform is hiring a Principal Site Reliability Engineer. Base salary range $245,000 - $320,000 plus bonus and restricted stock units. Requirements: 8+ years experience with Linux kernel tuning, TCP/IP networking, and distributed systems. Submit resume via https://google.com/careers.",
        expected_ground_truth=0,
        expected_max_score=29,
        expected_risk_tiers=["low"],
        notes="Legitimate high-compensation senior tech posting; high compensation must NOT trigger scam flag.",
    ),
    GoldenTestCase(
        id="GOLDEN-A-06",
        cohort="clean_legitimate",
        title="Customer Support Specialist (Official WhatsApp Channel)",
        company_name="Kredivo Financial Services",
        text="Kredivo is hiring a Customer Support Representative in Jakarta. Assist borrowers with loan inquiries and billing queries. Candidates can submit their application through https://kredivo.com/careers or message our verified enterprise recruitment desk.",
        expected_ground_truth=0,
        expected_max_score=35,
        expected_risk_tiers=["low", "medium"],
        notes="Legitimate fintech recruiting for customer support with corporate URL.",
    ),
    GoldenTestCase(
        id="GOLDEN-A-07",
        cohort="clean_legitimate",
        title="Post-Offer Compliance & Background Verification",
        company_name="Accenture Solutions",
        text="Welcome to Accenture! Following your formal job offer letter acceptance, our compliance portal requires you to upload your government identity documents (Aadhaar/PAN card) to initiate standard background screening via https://accenture.com/onboarding.",
        expected_ground_truth=0,
        expected_max_score=35,
        expected_risk_tiers=["low", "medium"],
        notes="Legitimate post-offer background check on corporate domain; must not trigger upfront scam flag.",
    ),
    GoldenTestCase(
        id="GOLDEN-A-08",
        cohort="clean_legitimate",
        title="Lead Cloud Architect",
        company_name="Amazon Web Services",
        text="AWS is looking for a Lead Solutions Architect in Seattle, WA. Tech stack: CloudFormation, ECS, DynamoDB, and IAM security models. Bachelor's in CS or equivalent. Apply through amazon.jobs.",
        expected_ground_truth=0,
        expected_max_score=29,
        expected_risk_tiers=["low"],
        notes="Authentic corporate cloud infrastructure recruitment.",
    ),

    # -------------------------------------------------------------------------
    # Cohort B: Obvious Scams (Ground Truth: 1, Target Risk: HIGH / CRITICAL)
    # -------------------------------------------------------------------------
    GoldenTestCase(
        id="GOLDEN-B-01",
        cohort="obvious_scam",
        title="Remote Data Entry Clerk - Advance Registration Fee",
        company_name="Apex Global Services",
        text="URGENT HIRING: Remote Data Entry Typist. Earn ₹35,000 weekly flexible hours. Direct selection without interview. Compulsory registration fee of ₹2,500 required for software kit clearance. Contact HR manager on WhatsApp.",
        expected_ground_truth=1,
        expected_min_score=60,
        expected_risk_tiers=["high", "critical"],
        notes="Registration fee + No interview + WhatsApp recruitment.",
    ),
    GoldenTestCase(
        id="GOLDEN-B-02",
        cohort="obvious_scam",
        title="Virtual Executive Assistant - Cashier Check Fraud",
        company_name="United Global Logistics Inc",
        text="Immediate vacancy for Executive Assistant. We will mail a cashier check of $3,500 to your address. Deposit check at your bank ATM, keep 10% commission, and wire the remainder to our authorized office supply vendor via Western Union.",
        expected_ground_truth=1,
        expected_min_score=60,
        expected_risk_tiers=["high", "critical"],
        notes="Classic cashier check overpayment and money routing fraud.",
    ),
    GoldenTestCase(
        id="GOLDEN-B-03",
        cohort="obvious_scam",
        title="Online Film Rating Specialist - USDT Task Scheme",
        company_name="Star Media VIP Tasks",
        text="Earn $400 daily rating Hollywood movies. Deposit 100 USDT into company crypto wallet to activate commission portal and unlock daily VIP withdrawal tasks. Connect on Telegram @StarMovie_Admin.",
        expected_ground_truth=1,
        expected_min_score=60,
        expected_risk_tiers=["high", "critical"],
        notes="Crypto deposit-to-withdraw task trap + Telegram funnel.",
    ),
    GoldenTestCase(
        id="GOLDEN-B-04",
        cohort="obvious_scam",
        title="Immediate Data Ingestion - Banking Credentials Demand",
        company_name="FastHire Health Systems",
        text="You have been selected for immediate employment! Send your bank login credentials, netbanking password, and debit card front and back photos to hr_payroll_services2026@gmail.com for direct deposit setup before call.",
        expected_ground_truth=1,
        expected_min_score=60,
        expected_risk_tiers=["high", "critical"],
        notes="Critical PII / banking credentials phishing.",
    ),
    GoldenTestCase(
        id="GOLDEN-B-05",
        cohort="obvious_scam",
        title="YouTube Video Liker & Social Media Assistant",
        company_name="Viral Boost Global",
        text="Earn $50/hour just liking YouTube and TikTok videos from home. Instant hiring guaranteed. Deposit ₹5,000 into company UPI to start receiving tasks. Join Telegram channel t.me/viral_boost_jobs.",
        expected_ground_truth=1,
        expected_min_score=60,
        expected_risk_tiers=["high", "critical"],
        notes="Click farming / passive income task scam with UPI recharge.",
    ),
    GoldenTestCase(
        id="GOLDEN-B-06",
        cohort="obvious_scam",
        title="Medical Transcriptionist - Training Bond Fee",
        company_name="CareFirst Transcriptions",
        text="Work from home Medical Transcriptionist. $65/hr. Selected applicants must transfer a $180 training fee and equipment shipping bond via CashApp before laptop dispatch. Telegram interview only.",
        expected_ground_truth=1,
        expected_min_score=60,
        expected_risk_tiers=["high", "critical"],
        notes="Training fee + Equipment shipping bond + Telegram.",
    ),
    GoldenTestCase(
        id="GOLDEN-B-07",
        cohort="obvious_scam",
        title="Mystery Shopper & Gift Card Evaluator",
        company_name="Retail Insight Group",
        text="We send you a company check for $2,800. Cash it at your bank, purchase Google Play and Apple gift cards at Walmart, and send photos of the gift card codes to our supervisor on Telegram @RetailEval.",
        expected_ground_truth=1,
        expected_min_score=60,
        expected_risk_tiers=["high", "critical"],
        notes="Check fraud paired with gift card laundering.",
    ),
    GoldenTestCase(
        id="GOLDEN-B-08",
        cohort="obvious_scam",
        title="Student Marketing Ambassador - Certificate Charge",
        company_name="Future Leaders Global",
        text="College Internship: ₹40,000 monthly stipend. 100% selection guaranteed. Mandatory ₹1,800 enrollment fee required for issuance of student registration ID before interview slot allocation.",
        expected_ground_truth=1,
        expected_min_score=60,
        expected_risk_tiers=["high", "critical"],
        notes="Student advance-fee internship scam.",
    ),

    # -------------------------------------------------------------------------
    # Cohort C: Impersonation & Typosquatting (Ground Truth: 1, Target: MEDIUM / HIGH / CRITICAL)
    # -------------------------------------------------------------------------
    GoldenTestCase(
        id="GOLDEN-C-01",
        cohort="impersonation",
        title="Microsoft Remote Cloud Engineer (Typosquatted Domain)",
        company_name="Microsoft",
        text="Microsoft is hiring Remote Cloud Engineers for Azure Core Infrastructure. Generous compensation package. Submit your application and resume on https://unresolving-fake-ms-portal.xyz or email hr@apex-scam.top.",
        expected_ground_truth=1,
        expected_min_score=35,
        expected_risk_tiers=["medium", "high", "critical"],
        notes="Impersonating Microsoft with unresolving domain and unrelated recruiter email.",
    ),
    GoldenTestCase(
        id="GOLDEN-C-02",
        cohort="impersonation",
        title="Google Operations Specialist (Unrelated Free Mail)",
        company_name="Google",
        text="Google is seeking an Operations Specialist in Dublin. Competitive salary and benefits. Send your CV directly to google_recruitment_emea2026@gmail.com on Telegram @GoogleRecruit_Dave.",
        expected_ground_truth=1,
        expected_min_score=40,
        expected_risk_tiers=["medium", "high", "critical"],
        notes="Impersonating Google with free webmail and unofficial Telegram channel.",
    ),
    GoldenTestCase(
        id="GOLDEN-C-03",
        cohort="impersonation",
        title="Apple Hardware QA Technician (Lookalike Domain)",
        company_name="Apple",
        text="Apple is expanding its hardware testing team in Cupertino. Apply directly at http://apple-careers-apply-now.info. Registration charge of $50 required for hardware test bench clearance.",
        expected_ground_truth=1,
        expected_min_score=60,
        expected_risk_tiers=["high", "critical"],
        notes="Lookalike domain + Upfront clearance charge.",
    ),
    GoldenTestCase(
        id="GOLDEN-C-04",
        cohort="impersonation",
        title="Amazon Warehouse Operations Lead",
        company_name="Amazon",
        text="Amazon Logistics is hiring Warehouse Team Leads. $45/hr. Selected candidates must contact recruiter via non-official telegram handle @AmazonRecruiter_VIP to schedule onboarding.",
        expected_ground_truth=1,
        expected_min_score=40,
        expected_risk_tiers=["medium", "high", "critical"],
        notes="Brand impersonation directing traffic to Telegram.",
    ),

    # -------------------------------------------------------------------------
    # Cohort D: Borderline & Ambiguous (Ground Truth: 0 or Low Threat, Target: LOW / MEDIUM < 60)
    # -------------------------------------------------------------------------
    GoldenTestCase(
        id="GOLDEN-D-01",
        cohort="borderline",
        title="Freelance Graphic Designer (Recruiter uses Gmail)",
        company_name="Studio Bright Design",
        text="Small boutique branding agency is looking for a freelance graphic designer. Tech stack: Figma, Illustrator, After Effects. Pay is $40/hr based on portfolio review. Please send your portfolio link to studiobright.design@gmail.com.",
        expected_ground_truth=0,
        expected_max_score=50,
        expected_risk_tiers=["low", "medium"],
        notes="Legitimate small design studio using free webmail; must NOT become critical.",
    ),
    GoldenTestCase(
        id="GOLDEN-D-02",
        cohort="borderline",
        title="Junior Frontend Developer (Recruiter uses WhatsApp Screening)",
        company_name="PixelCraft Labs",
        text="PixelCraft Labs is hiring a Junior React Developer in Bangalore. Requirements: JavaScript, Tailwind CSS, REST APIs. Our HR coordinator conducts initial 10-minute screening calls via WhatsApp at +919876543210. Apply at https://pixelcraftlabs.com/jobs.",
        expected_ground_truth=0,
        expected_max_score=55,
        expected_risk_tiers=["low", "medium"],
        notes="Early-stage startup using WhatsApp for initial scheduling alongside corporate domain.",
    ),
    GoldenTestCase(
        id="GOLDEN-D-03",
        cohort="borderline",
        title="Senior Director of Engineering ($350k)",
        company_name="Datadog",
        text="Datadog is looking for a Senior Director of Engineering for Observability. Salary $320,000 - $380,000 plus equity. Minimum 12 years leading enterprise distributed systems. Official portal: https://datadoghq.com/careers.",
        expected_ground_truth=0,
        expected_max_score=29,
        expected_risk_tiers=["low"],
        notes="Legitimate high-compensation executive engineering role.",
    ),
    GoldenTestCase(
        id="GOLDEN-D-04",
        cohort="borderline",
        title="Stealth AI Startup - Founding Engineer",
        company_name="CognitiveForge AI",
        text="Join our early-stage AI venture as Founding Engineer. We just launched our public site at https://cognitiveforge.ai. 3+ years experience with LLM orchestration and vector databases. Standard interview process.",
        expected_ground_truth=0,
        expected_max_score=45,
        expected_risk_tiers=["low", "medium"],
        notes="Recently launched startup; new domain age must act as weak signal, not fatal verdict.",
    ),
    GoldenTestCase(
        id="GOLDEN-D-05",
        cohort="borderline",
        title="Enterprise Account Executive (Greenhouse ATS Link)",
        company_name="Snowflake",
        text="Snowflake is hiring an Enterprise Account Executive. 5+ years B2B SaaS sales experience. Applications hosted via our applicant tracking portal on https://boards.greenhouse.io/snowflake/jobs/592819.",
        expected_ground_truth=0,
        expected_max_score=29,
        expected_risk_tiers=["low"],
        notes="Legitimate third-party ATS platform (Greenhouse).",
    ),

    # -------------------------------------------------------------------------
    # Cohort E: Adversarial & Obfuscated (Ground Truth: 1, Target: MEDIUM / HIGH / CRITICAL)
    # -------------------------------------------------------------------------
    GoldenTestCase(
        id="GOLDEN-E-01",
        cohort="adversarial",
        title="Data Entry with Spaced Obfuscation (r e g i s t r a t i o n)",
        company_name="Apex Global",
        text="URGENT HIRING: Remote Assistant needed immediately. Receive r e g i s t r a t i o n fee instructions and cashier check equipment details on T e l e g r a m @ScamLead.",
        expected_ground_truth=1,
        expected_min_score=50,
        expected_risk_tiers=["medium", "high", "critical"],
        notes="Spaced keyword evasion attempt targeting regex matching.",
    ),
    GoldenTestCase(
        id="GOLDEN-E-02",
        cohort="adversarial",
        title="Disguised Refundable Onboarding Contribution",
        company_name="Global Logistics Hub",
        text="Work from home Assistant. $55/hr. A refundable onboarding security contribution of $200 is required for training kit courier insurance before work commencement. Message on Signal.",
        expected_ground_truth=1,
        expected_min_score=50,
        expected_risk_tiers=["medium", "high", "critical"],
        notes="Paraphrased fee scheme using 'refundable onboarding contribution' and 'courier insurance'.",
    ),
    GoldenTestCase(
        id="GOLDEN-E-03",
        cohort="adversarial",
        title="Disguised Wallet Funding & Optimization Tasks",
        company_name="Digital Commerce Optimization Portal",
        text="Work 30 minutes daily completing online merchant rating tasks. Fund your personal workstation wallet with 50 USDT to unlock daily tier rating profits. Connect on Telegram @MerchantTaskPro.",
        expected_ground_truth=1,
        expected_min_score=55,
        expected_risk_tiers=["medium", "high", "critical"],
        notes="Evasive phrasing for deposit-to-withdraw crypto recharge trap.",
    ),
    GoldenTestCase(
        id="GOLDEN-E-04",
        cohort="adversarial",
        title="Disguised Account Routing / Equipment Check",
        company_name="Premier Supply Courier",
        text="Corporate procurement clerk. Company vendor check will be provided upon contact. Deposit company funds into your ATM and forward balance to courier via Zelle. Immediate start.",
        expected_ground_truth=1,
        expected_min_score=55,
        expected_risk_tiers=["medium", "high", "critical"],
        notes="Money mule recruitment disguising overpayment instructions.",
    ),
]
