import re
from typing import Any, Callable, Dict, List, Optional


class RuleDefinition:
    """Represents a discrete deterministic security rule."""

    def __init__(
        self,
        code: str,
        name: str,
        category: str,
        severity: str,
        default_weight: int,
        confidence: float,
        description: str,
        recommendation: str,
        pattern: Optional[re.Pattern] = None,
        custom_matcher: Optional[Callable[[str, Dict[str, Any]], Optional[str]]] = None,
        enabled: bool = True,
        version: str = "rules-v1.0.0",
    ):
        self.code = code
        self.name = name
        self.category = category
        self.severity = severity
        self.default_weight = default_weight
        self.confidence = confidence
        self.description = description
        self.recommendation = recommendation
        self.pattern = pattern
        self.custom_matcher = custom_matcher
        self.enabled = enabled
        self.version = version


# Custom Context Matchers

def match_unrealistic_compensation(text: str, metadata: Dict[str, Any]) -> Optional[str]:
    """Detect unrealistic high compensation paired with low-skill / data entry keywords."""
    low_skill_kw = re.search(r'\b(data entry|typist|typing|document formatting|assistant|packaging clerk|virtual assistant)\b', text, re.IGNORECASE)
    if not low_skill_kw:
        return None

    # Look for $50+/hr, ₹30,000+/week, $3,000+/week
    high_pay_match = re.search(
        r'(\$\s*(?:[5-9]\d|\d{3,})\s*(?:/|\s*per\s*)?\s*(?:hr|hour|day)|₹\s*(?:[3-9]\d{4}|\d{6,})\s*(?:/|\s*per\s*)?\s*(?:wk|week|month)|\$\s*[2-9],\d{3}\s*(?:/|\s*per\s*)?\s*week)',
        text,
        re.IGNORECASE,
    )
    if high_pay_match:
        return high_pay_match.group(0).strip()
    return None


def match_personal_recruiter_email(text: str, metadata: Dict[str, Any]) -> Optional[str]:
    """Detect free webmail domains used as primary recruiter contact."""
    match = re.search(r'\b[A-Za-z0-9._%+-]+@(gmail|yahoo|hotmail|outlook|rediffmail|protonmail|yopmail)\.com\b', text, re.IGNORECASE)
    if match:
        return match.group(0).strip()
    return None


RULE_REGISTRY: List[RuleDefinition] = [
    # -------------------------------------------------------------
    # Category A: Financial Fraud (Max Category Cap: 30)
    # -------------------------------------------------------------
    RuleDefinition(
        code="FIN_REGISTRATION_FEE",
        name="Mandatory Registration / Application Fee",
        category="financial",
        severity="critical",
        default_weight=30,
        confidence=0.98,
        description="The posting requests an upfront registration, processing, or application fee.",
        recommendation="Never pay any upfront registration or processing fee for employment. Legitimate employers never charge candidates.",
        pattern=re.compile(r'\b(registration fee|application fee|enrollment fee|processing fee|onboarding fee|registration charge)\b', re.IGNORECASE),
    ),
    RuleDefinition(
        code="FIN_TRAINING_FEE",
        name="Mandatory Training / Software Fee",
        category="financial",
        severity="high",
        default_weight=25,
        confidence=0.95,
        description="The candidate is required to purchase software licenses, ID clearance, or training modules.",
        recommendation="Employers provide all required work tools, hardware, and training materials at zero cost.",
        pattern=re.compile(r'\b(training fee|software license fee|id card clearance|kit fee|purchase (?:software|dictionary|materials) before)\b', re.IGNORECASE),
    ),
    RuleDefinition(
        code="FIN_ADVANCE_PAYMENT",
        name="Upfront Security Deposit / Joining Bond",
        category="financial",
        severity="critical",
        default_weight=30,
        confidence=0.98,
        description="Candidate is instructed to deposit funds or transfer a refundable security bond.",
        recommendation="Refuse all security deposit requests. Legitimate companies never request refundable bonds from recruits.",
        pattern=re.compile(r'\b(security deposit|refundable deposit|advance payment|equipment shipping bond|pay \d+ before (?:joining|interview|work))\b', re.IGNORECASE),
    ),
    RuleDefinition(
        code="FIN_CASHIER_CHECK_FRAUD",
        name="Cashier Check / Overpayment Equipment Scam",
        category="financial",
        severity="critical",
        default_weight=30,
        confidence=0.99,
        description="Candidate is instructed to deposit a mailed company check and purchase hardware from an authorized vendor.",
        recommendation="Do not deposit mailed checks. The check will bounce days later after you send real funds to the scam vendor.",
        pattern=re.compile(r'\b(cashier check|company check|electronic check|deposit (?:via|at|into)?\s*(?:mobile\s*)?check|deposit (?:the|a) check|keep \d+%(?: commission)? and wire|vendor check|mobile check deposit)\b', re.IGNORECASE),
    ),
    RuleDefinition(
        code="FIN_BITCOIN_ATM_DEPOSIT",
        name="Crypto / Bitcoin ATM Cash Deposit Scam",
        category="financial",
        severity="critical",
        default_weight=30,
        confidence=0.99,
        description="Candidate is instructed to deposit cash or company checks into a Bitcoin ATM or cryptocurrency kiosk.",
        recommendation="Never use Bitcoin ATMs or send crypto for employment. This is an irreversible financial scam.",
        pattern=re.compile(r'\b(bitcoin atm|coinstar|crypto kiosk|deposit at (?:the )?nearest bitcoin|qr code at bitcoin atm|metamask wallet|gas fee)\b', re.IGNORECASE),
    ),
    RuleDefinition(
        code="FIN_SEND_MONEY",
        name="Fund Forwarding / Account Routing",
        category="financial",
        severity="high",
        default_weight=25,
        confidence=0.95,
        description="Instructs employee to receive company funds into personal accounts and forward or wire them elsewhere.",
        recommendation="This is classic money mule recruitment. Receiving and routing unauthorized funds is illegal.",
        pattern=re.compile(r'\b(disburse company funds|forwarding funds|transfer to your personal bank|wire remainder|zelle to your personal|cashapp before laptop)\b', re.IGNORECASE),
    ),
    RuleDefinition(
        code="LOGISTICS_RESHIPPING_MULE",
        name="Reshipping & Package Forwarding Mule",
        category="logistics",
        severity="critical",
        default_weight=25,
        confidence=0.95,
        description="Candidate is instructed to receive, repackage, and forward merchandise/parcels to third parties.",
        recommendation="Reshipping stolen merchandise from your residence is illegal and constitutes mail fraud.",
        pattern=re.compile(r'\b(inspecting (?:luxury )?parcels|ship electronics and designer|repackage them with our prepaid|repackage and ship|forward packages|forwarded box)\b', re.IGNORECASE),
    ),

    # -------------------------------------------------------------
    # Category B: Communication Channels (Max Category Cap: 10)
    # -------------------------------------------------------------
    RuleDefinition(
        code="COMM_TELEGRAM_RECRUITMENT",
        name="Recruitment Directed Exclusively to Telegram",
        category="communication",
        severity="medium",
        default_weight=15,
        confidence=0.90,
        description="Recruiter directs screening and interview exclusively to Telegram direct messaging or channels.",
        recommendation="Legitimate corporate HR departments conduct interviews via official video tools (Meet, Zoom, Teams) or official portals.",
        pattern=re.compile(r'\b(telegram|t\.me/|@\w+_recruiter|telegram handle|contact (?:on|via) telegram)\b', re.IGNORECASE),
    ),
    RuleDefinition(
        code="COMM_WHATSAPP_RECRUITMENT",
        name="Recruitment via Unverified WhatsApp Channel",
        category="communication",
        severity="medium",
        default_weight=10,
        confidence=0.88,
        description="Job application or task onboarding conducted through WhatsApp messaging.",
        recommendation="Avoid conducting official onboarding on WhatsApp unless verified through the enterprise career page.",
        pattern=re.compile(r'\b(whatsapp|wa\.me/|message to \+?\d+ on whatsapp|contact hr manager on whatsapp)\b', re.IGNORECASE),
    ),
    RuleDefinition(
        code="COMM_SIGNAL_RECRUITMENT",
        name="Recruitment via Signal / Encrypted Chat",
        category="communication",
        severity="medium",
        default_weight=10,
        confidence=0.90,
        description="Recruiter mandates conducting employment screening on Signal or ephemeral messaging platforms.",
        recommendation="Verify recruiter corporate domain email before conducting discussions on third-party messaging apps.",
        pattern=re.compile(r'\b(signal app|interview conducted exclusively on signal)\b', re.IGNORECASE),
    ),
    RuleDefinition(
        code="COMM_PERSONAL_EMAIL",
        name="Free Personal Webmail Recruiter Address",
        category="communication",
        severity="low",
        default_weight=8,
        confidence=0.75,
        description="Primary contact email uses a free webmail provider (Gmail, Yahoo, Hotmail) rather than a corporate domain.",
        recommendation="Look for official corporate email domains (@company.com). Free email addresses should be verified with caution.",
        custom_matcher=match_personal_recruiter_email,
    ),

    # -------------------------------------------------------------
    # Category C: Recruitment Manipulation (Max Category Cap: 15)
    # -------------------------------------------------------------
    RuleDefinition(
        code="RECRUIT_GUARANTEED_SELECTION",
        name="Guaranteed Employment / 100% Selection Lure",
        category="manipulation",
        severity="high",
        default_weight=15,
        confidence=0.92,
        description="Claims unconditional 100% job placement or guaranteed hiring without competitive evaluation.",
        recommendation="Authentic hiring always involves substantive skill evaluation and interviews. Treat guarantees with skepticism.",
        pattern=re.compile(r'\b(100% (?:guaranteed|job placement)|guaranteed (?:hiring|selection|job)|instant (?:hiring|start)|direct selection without)\b', re.IGNORECASE),
    ),
    RuleDefinition(
        code="RECRUIT_NO_INTERVIEW",
        name="No Interview / Zero Qualification Required",
        category="manipulation",
        severity="high",
        default_weight=15,
        confidence=0.90,
        description="Posting claims no interview is required or immediate offer issued upon contact.",
        recommendation="Employment offers issued without formal interviews are typical vectors for financial or identity fraud.",
        pattern=re.compile(r'\b(no interview (?:required|needed)|zero qualifications? (?:needed|required)|immediate job offer letter without)\b', re.IGNORECASE),
    ),
    RuleDefinition(
        code="RECRUIT_URGENT_ACTION",
        name="High-Pressure Urgency Tactics",
        category="manipulation",
        severity="medium",
        default_weight=10,
        confidence=0.85,
        description="Uses psychological urgency to compel rapid, unconsidered candidate action.",
        recommendation="Do not let artificial urgency rush your due diligence. Verify company details independently.",
        pattern=re.compile(r'\b(urgent hiring|needed immediately|act immediately|limited spots remaining|urgent requirement|immediate vacancy)\b', re.IGNORECASE),
    ),

    # -------------------------------------------------------------
    # Category D: Compensation Anomalies (Max Category Cap: 20)
    # -------------------------------------------------------------
    RuleDefinition(
        code="COMP_UNREALISTIC_PAY",
        name="Unrealistic High Compensation for Entry Tasks",
        category="compensation",
        severity="high",
        default_weight=20,
        confidence=0.88,
        description="Offered wage is disproportionately high relative to basic data entry or typing tasks.",
        recommendation="Compare salary expectations against standard industry benchmarks on Glassdoor or Levels.fyi.",
        custom_matcher=match_unrealistic_compensation,
    ),
    RuleDefinition(
        code="COMP_EASY_MONEY_MINIMAL_WORK",
        name="Click / Video Liking Passive Income Claims",
        category="compensation",
        severity="high",
        default_weight=20,
        confidence=0.95,
        description="Promises large daily payouts for trivial tasks like liking YouTube videos or rating movies.",
        recommendation="These schemes funnel victims into predatory deposit-to-withdraw traps. Never participate.",
        pattern=re.compile(r'\b(liking (?:youtube|tiktok) videos|rating (?:movies|films|products)|earn \$\d+ daily watching|easy daily income|vip rating tasks)\b', re.IGNORECASE),
    ),

    # -------------------------------------------------------------
    # Category E: Sensitive Information Requests (Max Category Cap: 15)
    # -------------------------------------------------------------
    RuleDefinition(
        code="DATA_BANK_CREDENTIALS",
        name="Demands Banking Credentials / NetBanking Login",
        category="data_privacy",
        severity="critical",
        default_weight=25,
        confidence=0.99,
        description="Explicitly demands bank account login credentials, OTP codes, or passwords before hiring.",
        recommendation="Never share bank credentials, passwords, or OTP codes with any recruiter or prospective employer.",
        pattern=re.compile(r'\b(bank login credentials|netbanking password|enter banking credentials|send otp|share pin|credit card front and back)\b', re.IGNORECASE),
    ),
    RuleDefinition(
        code="DATA_AADHAAR_PAN_UPFRONT",
        name="Demands Government ID / SSN Upfront",
        category="data_privacy",
        severity="medium",
        default_weight=12,
        confidence=0.85,
        description="Demands full SSN, Aadhaar, PAN, or passport scans before conducting an initial interview.",
        recommendation="Official background screening occurs after an offer is extended, handled via verified compliance portals.",
        pattern=re.compile(r'\b(full ssn|send scanned driver license|copy of passport before interview|birth date and ssn for immediate)\b', re.IGNORECASE),
    ),

    # -------------------------------------------------------------
    # Category F: Crypto & Task Recharge Scams (Max Category Cap: 25)
    # -------------------------------------------------------------
    RuleDefinition(
        code="CRYPTO_WALLET_DEPOSIT",
        name="Cryptocurrency Deposit / USDT Wallet Recharge",
        category="crypto_task",
        severity="critical",
        default_weight=25,
        confidence=0.98,
        description="Instructs user to deposit USDT, Bitcoin, or funds into a crypto wallet or UPI portal to activate work.",
        recommendation="Employment that requires personal capital or crypto deposit is a fraudulent task scam.",
        pattern=re.compile(r'\b(usdt|crypto wallet|deposit \d+ usdt|daily payments in bitcoin|deposit into company upi to activate)\b', re.IGNORECASE),
    ),
    RuleDefinition(
        code="TASK_DEPOSIT_TO_WITHDRAW",
        name="Deposit-to-Withdraw Task Trap",
        category="crypto_task",
        severity="critical",
        default_weight=25,
        confidence=0.98,
        description="Requires user to deposit money to unlock withdrawals or complete task batches.",
        recommendation="Do not send funds. Any portal requiring a recharge to withdraw earned money is an investment task trap.",
        pattern=re.compile(r'\b(deposit to unlock|activate commission portal|withdrawal enabled upon completing|vip rating tasks)\b', re.IGNORECASE),
    ),

    # -------------------------------------------------------------
    # Category G: 🇮🇳 India-Specific Fraud Vectors (Max Category Cap: 30)
    # -------------------------------------------------------------
    RuleDefinition(
        code="FIN_UPI_QR_PAYMENT",
        name="Demands UPI / QR Code / GPay / PhonePe / Paytm Payment",
        category="financial",
        severity="critical",
        default_weight=30,
        confidence=0.99,
        description="Candidate is instructed to transfer funds via UPI, Google Pay, PhonePe, Paytm, or scan a QR code for application processing, ID cards, or training kits.",
        recommendation="Never make UPI or QR code transfers for any job. Legitimate Indian employers (TCS, Infosys, Wipro, etc.) NEVER charge application or onboarding fees.",
        pattern=re.compile(r'\b(gpay|phonepe|paytm|bhim upi|upi id|scan (?:the )?qr code|pay through upi|transfer to upi|gate pass fee|laptop security deposit|refundable security via upi)\b', re.IGNORECASE),
    ),
    RuleDefinition(
        code="RECRUIT_INDIAN_IT_IMPERSONATION",
        name="Unauthorized Indian Enterprise Impersonation (TCS, Infosys, Wipro, Tata)",
        category="manipulation",
        severity="critical",
        default_weight=25,
        confidence=0.95,
        description="Posting claims to represent top Indian corporate giants (TCS, Infosys, Wipro, Tata, HCL, Reliance) while using unofficial communication channels or demanding fees.",
        recommendation="Top Indian IT firms have strict zero-fee policies and only contact candidates from corporate domains (@tcs.com, @infosys.com, @wipro.com). Report to 1930 Cybercrime Helpline.",
        pattern=re.compile(r'\b(?:tcs|infosys|wipro|tata motors|tata consultancy|hcl tech|tech mahindra|reliance jio|cognizant)\b.*?(?:registration fee|processing fee|interview fee|gate pass|security deposit|@gmail\.com|@yahoo\.com|whatsapp only)', re.IGNORECASE),
    ),
    RuleDefinition(
        code="DATA_AADHAAR_PAN_HARVESTING",
        name="Mandatory Aadhaar / PAN / OTP Upload Before Screening",
        category="data_privacy",
        severity="high",
        default_weight=20,
        confidence=0.92,
        description="Candidate is required to submit clear copies of Aadhaar card, PAN card, or share OTP codes prior to any official interview.",
        recommendation="Do not share Aadhaar or PAN details on unverified forms or messaging apps. Masked Aadhaar should only be provided during formal verified onboarding.",
        pattern=re.compile(r'\b(aadhaar card|pan card photo|upload aadhaar|send pan copy|aadhaar otp|submit aadhaar and pan before interview)\b', re.IGNORECASE),
    ),
]

