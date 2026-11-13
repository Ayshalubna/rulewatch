"""ESSENTIALS BRIEFS: short, plain-English reference notes on the Dubai real estate rules people ask about most.

Why this exists: the official PDFs are long (and several are Arabic only), so everyday questions such as
"what is the DLD transfer fee?" or "do I need a permit for an Instagram ad?" were hard to answer from them alone.
Each note below states a well-established rule, names the law or regulator it comes from, and is stored in the
same searchable library as the official documents, so the Ask agent and the plan Checker can cite it.

They are loaded into the database once at start-up (and re-loaded only when this file changes).
Fees can change: every fee note tells the user to confirm the current amount with the regulator.
"""
import hashlib

from . import embed, store

VERSION = "2026-11-14a"

BRIEFS = [
    {
        "url": "https://dubailand.gov.ae/en/#rulewatch-essentials-buying-and-fees",
        "title": "Essentials brief: DLD fees, buying and selling property in Dubai",
        "regulator": "DLD/RERA",
        "topics": ["registration & title deeds", "mortgage & finance", "off-plan & escrow"],
        "summary_en": "Plain-English reference on the costs and steps of buying or selling property in Dubai: the 4% DLD "
                      "transfer fee, mortgage and off-plan registration fees, who may own freehold property, the sale "
                      "forms, and how to verify a title deed. Compiled from Dubai Land Department sources.",
        "summary_ar": "مرجع مبسط لتكاليف وخطوات شراء وبيع العقارات في دبي: رسوم نقل الملكية 4٪، رسوم تسجيل الرهن والبيع على "
                      "الخارطة، من يحق له التملك الحر، نماذج البيع، وكيفية التحقق من سند الملكية.",
        "notes": [
            ("DLD transfer fee when buying a property",
             "The Dubai Land Department (DLD) transfer fee on a property sale is 4% of the sale value. By default it "
             "is shared equally between buyer and seller unless they agree otherwise, and in practice the buyer "
             "usually pays all of it under the sale contract. On top of the 4% there is a DLD administration fee "
             "(AED 580 for apartments and offices, AED 430 for land, AED 40 for off-plan units), a title deed issuance "
             "fee of about AED 250, and the Registration Trustee office fee (AED 4,000 + VAT when the price is "
             "AED 500,000 or more, AED 2,000 + VAT below that). Fees can change, so confirm the current amounts with "
             "DLD before closing."),
            ("Mortgage registration fee",
             "Registering a mortgage at the Dubai Land Department costs 0.25% of the loan amount plus an administration "
             "fee of AED 290. This is paid in addition to the 4% transfer fee when a purchase is financed by a bank."),
            ("Off-plan (Oqood) registration fee and duty to register",
             "Every off-plan sale must be registered in the Interim Real Estate Register (Oqood) under Law No. 13 of "
             "2008; an off-plan sale that is not registered is void. The registration fee is 4% of the purchase "
             "price plus an administration fee. The developer is responsible for registering the sale, and buyers "
             "should receive the Oqood certificate as proof."),
            ("Can foreigners own property in Dubai (freehold areas)",
             "Yes. Under Law No. 7 of 2006 (Real Property Registration Law), UAE and GCC nationals may own property "
             "anywhere in Dubai, while other nationalities may own freehold title, a usufruct right or a long lease "
             "of up to 99 years in the areas designated by the Ruler of Dubai (the designated freehold areas, first "
             "listed in Regulation No. 3 of 2006). All ownership rights must be registered at DLD to be valid."),
            ("Steps and forms in a Dubai property resale (Form A, Form B, Form F, NOC)",
             "A typical resale goes: the seller signs Form A (listing agreement with a RERA-registered broker); the "
             "buyer signs Form B (buyer and broker agreement); buyer and seller sign Form F, the sale contract or MoU, "
             "usually with a 10% deposit cheque held by the broker; the seller obtains a No Objection Certificate "
             "(NOC) from the developer confirming service charges are paid; then both parties attend a DLD "
             "Registration Trustee office to pay by manager's cheque and transfer the title deed."),
            ("How to verify a title deed, broker or project",
             "Use the official Dubai REST app or the DLD website to verify a title deed, check that a broker holds a "
             "valid RERA broker card, confirm that an off-plan project is registered and see its escrow account and "
             "construction progress. A buyer should always verify the title deed and register the transfer at DLD; "
             "paying a private seller without DLD registration does not transfer ownership."),
            ("Property taxes: is there property tax, capital gains tax or VAT",
             "Dubai has no annual property tax and no personal income or capital gains tax on individuals selling "
             "property. Tenants pay a Dubai Municipality housing fee of 5% of annual rent, collected through the DEWA "
             "bill. For VAT (Federal Decree-Law No. 8 of 2017): the first sale of a new residential building within "
             "three years of completion is zero-rated, later residential sales and residential leases are exempt, and "
             "commercial property sales and leases carry 5% VAT."),
        ],
    },
    {
        "url": "https://dubailand.gov.ae/en/#rulewatch-essentials-brokers-and-advertising",
        "title": "Essentials brief: brokers, commission, advertising permits and AML duties",
        "regulator": "DLD/RERA",
        "topics": ["brokerage licensing", "advertising & marketing", "AML / KYC"],
        "summary_en": "Plain-English reference for real estate brokers in Dubai: registration and the broker card, how "
                      "commission works, the Trakheesi advertising permit and QR code that every property advert needs, "
                      "and anti-money-laundering reporting. Compiled from RERA and UAE federal sources.",
        "summary_ar": "مرجع مبسط للوسطاء العقاريين في دبي: التسجيل وبطاقة الوسيط، العمولة، تصريح الإعلان من نظام تراخيصي "
                      "ورمز الاستجابة السريعة المطلوب لكل إعلان عقاري، وواجبات مكافحة غسل الأموال.",
        "notes": [
            ("Broker commission in Dubai",
             "Broker commission in Dubai is set by agreement, not by one fixed statutory rate. The market standard is "
             "2% of the sale price on a sale, and about 5% of the first year's rent on a lease; 5% VAT is added to the "
             "commission. Under By-law No. 85 of 2006 a broker is only entitled to commission if registered with RERA, "
             "if there is a written brokerage agreement (Form A with the seller, Form B with the buyer), and if the deal "
             "was concluded through that broker's efforts. The agreed commission must be written in the contract."),
            ("How to become a registered real estate broker with RERA",
             "Real estate brokerage in Dubai is regulated by By-law No. 85 of 2006. A brokerage company needs a trade "
             "licence with a real estate brokerage activity and must be entered in the RERA brokers register. Each "
             "individual agent must complete the Certified Training for Real Estate Brokers at the Dubai Real Estate "
             "Institute (DREI), pass the RERA exam, provide a good conduct certificate, and obtain a broker card "
             "(broker registration number, BRN) through the Trakheesi system, renewed every year. Nobody may act as a "
             "broker, show property for commission or sign brokerage agreements before the card is issued; unlicensed "
             "brokerage is punishable by fines of up to AED 50,000."),
            ("Advertising permit for property ads, including Instagram and social media",
             "Yes, a permit is needed. Every real estate advertisement in Dubai, on property portals, Instagram, "
             "TikTok, Facebook, WhatsApp broadcasts, print or outdoor, needs a RERA advertising permit issued through "
             "the Trakheesi system before it is published. The permit number and its QR code (the Madmoun code) must "
             "appear on the advert. A permit is only issued to a RERA-registered brokerage or developer that has a "
             "signed listing agreement (Form A) or authorisation from the owner. Off-plan adverts also need the "
             "project to be registered and must show the developer and the escrow account. Advertising without a "
             "permit can be fined up to AED 50,000 and repeated breaches can suspend the licence."),
            ("Rules for the content of property adverts",
             "RERA's advertising terms require adverts to be accurate and not misleading: real prices and real photos "
             "of the actual unit, no promises of guaranteed returns or profits unless the guarantee is real, documented "
             "and names who gives it, no advertising a unit without the owner's authorisation, and the permit number "
             "and QR code on every advert. Influencers who promote property for payment also need the brokerage's "
             "permit to cover the advert."),
            ("Anti-money-laundering duties of brokers: cash and virtual asset deals",
             "Real estate brokers and agents are Designated Non-Financial Businesses and Professions under Federal "
             "Decree-Law No. 20 of 2018. They must identify the customer and beneficial owner (KYC), understand the "
             "source of funds, keep records for at least five years, and report suspicious transactions. They must "
             "also file a Real Estate Activity Report on the goAML system for any sale or purchase of freehold property "
             "where AED 55,000 or more is paid in cash, or where any part is paid in virtual assets or with funds "
             "converted from virtual assets. Skipping identity checks to close a deal faster is a breach."),
        ],
    },
    {
        "url": "https://dlp.dubai.gov.ae/en/#rulewatch-essentials-renting",
        "title": "Essentials brief: renting in Dubai (Ejari, rent increases, eviction, deposits, disputes)",
        "regulator": "Dubai Legislation",
        "topics": ["leasing & tenancy", "rent increase", "disputes & enforcement", "holiday homes"],
        "summary_en": "Plain-English reference on Dubai tenancy rules under Law No. 26 of 2007 as amended by Law No. 33 of "
                      "2008 and Decree No. 43 of 2013: Ejari registration, the rent increase caps, notice periods, legal "
                      "grounds for eviction, deposits, maintenance, subletting, holiday homes and the Rental Disputes Center.",
        "summary_ar": "مرجع مبسط لقواعد الإيجار في دبي وفق القانون رقم 26 لسنة 2007 وتعديلاته والمرسوم رقم 43 لسنة 2013: تسجيل "
                      "إيجاري، حدود زيادة الإيجار، مدد الإشعار، أسباب الإخلاء، التأمين، الصيانة ومركز فض المنازعات الإيجارية.",
        "notes": [
            ("What is Ejari and is it mandatory",
             "Ejari is the online system run by RERA for registering tenancy contracts in Dubai, and registration is "
             "mandatory: Article 4 of Law No. 26 of 2007 (as amended by Law No. 33 of 2008) requires every tenancy "
             "contract to be registered with RERA. Registration is the landlord's legal duty, though in practice the "
             "tenant or the agent often does it. Without an Ejari certificate a tenant cannot connect DEWA, sponsor "
             "residence visas or file a case at the Rental Disputes Center. The registration fee is about AED 220 at "
             "a typing centre (confirm the current fee)."),
            ("Maximum rent increase allowed in Dubai",
             "Decree No. 43 of 2013 caps rent increases on renewal by how far the current rent is below the average "
             "market rent for similar units in the RERA rental index: no increase if the rent is up to 10% below the "
             "average; up to 5% if it is 11% to 20% below; up to 10% if 21% to 30% below; up to 15% if 31% to 40% "
             "below; and up to 20% if it is more than 40% below. So the highest increase the law ever allows is 20%. "
             "The RERA Rental Index calculator (Smart Rental Index) gives the figure for a specific unit."),
            ("Notice needed to increase rent or change the tenancy contract",
             "A landlord or tenant who wants to change any term on renewal, including the rent, must notify the other "
             "party at least 90 days before the contract expires, unless they agreed a different period (Article 14 "
             "of Law No. 26 of 2007 as amended). Without that notice the contract renews on the same terms and the "
             "same rent."),
            ("Eviction when the contract expires: selling, personal use, renovation",
             "Under Article 25(2) of the tenancy law a landlord may ask a tenant to leave at the end of the contract "
             "only for four reasons: to demolish or rebuild the property, to carry out major renovation that cannot "
             "be done while it is occupied, for the landlord's own use or use by a first-degree relative (with no "
             "suitable alternative property), or to sell the property. In each case the landlord must give at least "
             "12 months' written notice served through the Notary Public or by registered mail. A WhatsApp message or "
             "a 30-day notice is not valid. If the landlord evicts for personal use, the property may not be re-let "
             "to someone else for two years (residential) or three years (non-residential), otherwise the tenant can "
             "claim compensation (Article 26)."),
            ("Eviction before the contract expires: unpaid rent and other breaches",
             "Under Article 25(1) a landlord may seek eviction during the term if the tenant does not pay rent within "
             "30 days of a written notice served through the Notary Public or registered mail, sublets without the "
             "landlord's written approval, uses the property for an illegal or different purpose, damages it or "
             "makes it unsafe, or breaches the law or the contract and does not fix it within 30 days of notice."),
            ("Security deposit, maintenance and subletting",
             "A landlord may take a security deposit and must refund it at the end of the tenancy, less the cost of "
             "any damage beyond normal wear (Article 20). The customary amount is 5% of annual rent for unfurnished "
             "and 10% for furnished property. Unless the contract says otherwise, the landlord is responsible for "
             "maintenance and for repairing defects that affect the tenant's use (Article 16). A tenant may not "
             "sublet or assign the property without the landlord's written consent (Article 24)."),
            ("Rental disputes: where to file and the fee",
             "Rental disputes in Dubai, including in free zones, are heard by the Rental Disputes Center (RDC), set up "
             "by Decree No. 26 of 2013. The filing fee is 3.5% of the annual rent, with a minimum of AED 500 and a "
             "maximum of AED 20,000, plus small administrative charges. An Ejari certificate is normally required to "
             "file a case."),
            ("Holiday homes and short-term rentals such as Airbnb",
             "Renting a home for short stays in Dubai requires a holiday home permit for each unit from the Department "
             "of Economy and Tourism (DET, formerly DTCM), under Decree No. 41 of 2013 and Administrative Resolution "
             "No. 1 of 2020. Operators need a holiday homes licence, the permit number must appear in every listing "
             "and advert, guests must be registered, and the Tourism Dirham fee is collected per night. Listing a unit "
             "on Airbnb or Booking.com without the permit is a violation."),
        ],
    },
    {
        "url": "https://dlp.dubai.gov.ae/en/#rulewatch-essentials-off-plan-and-owners",
        "title": "Essentials brief: off-plan sales, escrow, buyer default, defects and service charges",
        "regulator": "Dubai Legislation",
        "topics": ["off-plan & escrow", "jointly owned property & service charges", "registration & title deeds"],
        "summary_en": "Plain-English reference on Dubai off-plan and community rules: escrow accounts under Law No. 8 of "
                      "2007, when a developer may start selling, what happens when a buyer defaults under Law No. 13 of "
                      "2008, the developer's defects liability and service charges under Law No. 6 of 2019.",
        "summary_ar": "مرجع مبسط لقواعد البيع على الخارطة في دبي: حسابات الضمان وفق القانون رقم 8 لسنة 2007، متى يحق للمطور "
                      "البيع، إخلال المشتري وفق القانون رقم 13 لسنة 2008، مسؤولية المطور عن العيوب ورسوم الخدمات.",
        "notes": [
            ("What is an escrow account for off-plan projects",
             "Under Law No. 8 of 2007 a developer selling units off-plan must open a separate escrow account for each "
             "project with an escrow agent (a bank) accredited by DLD. All money paid by buyers must go into that "
             "account and may only be used for building that project; the developer cannot take buyer payments into "
             "its normal company account. The escrow agent keeps 5% of the account for one year after the completion "
             "certificate to cover defects. Buyers should always pay to the project escrow account shown in the "
             "sale agreement and on the Dubai REST app."),
            ("When may a developer start marketing and selling off-plan",
             "A developer may not advertise or sell off-plan units until it is registered with RERA as a developer, "
             "owns or has possession of the land, has the project registered with RERA and its escrow account open, "
             "and holds a RERA advertising permit for the campaign. Brokers may not market an unregistered project "
             "or take reservations for it."),
            ("What happens if an off-plan buyer stops paying (buyer default)",
             "Article 11 of Law No. 13 of 2008, as amended by Law No. 19 of 2017 and Law No. 19 of 2020, sets the "
             "process: the developer notifies DLD, DLD gives the buyer 30 days' notice to pay, and if the buyer still "
             "does not pay the remedy depends on construction progress. Above 80% complete, the developer may keep "
             "the contract and claim the balance, ask DLD to auction the unit, or cancel and keep up to 40% of the "
             "price. Between 60% and 80%, it may cancel and keep up to 40% of the price. Below 60% where work has "
             "started, up to 25%. If work has not started, up to 30% of the amounts paid. Check the Article for the "
             "exact wording before acting."),
            ("Developer liability for defects after handover",
             "Under Law No. 6 of 2019 on Jointly Owned Property, the developer is liable for ten years from the "
             "completion certificate to repair structural defects, and for one year to repair or replace defective "
             "installations such as mechanical, electrical, sanitary and plumbing works."),
            ("Service charges in jointly owned buildings",
             "Under Law No. 6 of 2019, service charges for a jointly owned property must be based on a budget "
             "approved by RERA and are shared by owners in proportion to their unit areas. They are collected and "
             "spent through the Mollak system and regulated bank accounts. A developer or management company may not "
             "set or collect charges above the approved budget, and unpaid charges are recovered through notice and "
             "the Rental Disputes Center."),
        ],
    },
    {
        "url": "https://u.ae/en/#rulewatch-essentials-visas-and-mortgages",
        "title": "Essentials brief: property investor visas and mortgage limits",
        "regulator": "UAE Federal",
        "topics": ["mortgage & finance", "registration & title deeds"],
        "summary_en": "Plain-English reference on the Golden Visa for property investors and the UAE Central Bank's "
                      "mortgage loan-to-value limits. Compiled from UAE federal government and Central Bank sources.",
        "summary_ar": "مرجع مبسط عن الإقامة الذهبية للمستثمرين العقاريين وحدود التمويل العقاري الصادرة عن مصرف الإمارات المركزي.",
        "notes": [
            ("Golden Visa and residence visa through property investment",
             "A property investor can obtain a 10-year renewable UAE Golden Visa by owning property in the UAE worth "
             "at least AED 2 million. The property may be mortgaged with an approved local bank, and off-plan property "
             "bought from approved developers also counts. In Dubai the application is made through the Dubai Land "
             "Department together with the residency authorities. A shorter two-year property investor residence has "
             "traditionally required property worth at least AED 750,000; DLD has been updating these thresholds, so "
             "confirm the current requirement with DLD before relying on it."),
            ("Mortgage limits: maximum loan-to-value and down payment",
             "The UAE Central Bank Mortgage Regulations cap home loans as follows. Expatriates: up to 80% of the value "
             "for a first home worth AED 5 million or less (minimum 20% down payment), 70% above AED 5 million, and 60% "
             "for a second or investment property. UAE nationals: 85%, 75% and 65% respectively. For off-plan property "
             "the cap is 50% for everyone. The maximum term is 25 years and total debt repayments may not exceed 50% "
             "of the borrower's income."),
        ],
    },
    {
        "url": "https://www.vara.ae/en/#rulewatch-essentials-tokenization",
        "title": "Essentials brief: tokenizing real estate and VARA licensing",
        "regulator": "VARA",
        "topics": ["tokenization & virtual assets", "AML / KYC", "advertising & marketing"],
        "summary_en": "Plain-English reference on who needs a VARA licence, how tokenized real estate is treated under "
                      "the Virtual Asset Issuance Rulebook, and the marketing and customer-check duties that apply.",
        "summary_ar": "مرجع مبسط حول من يحتاج إلى ترخيص من سلطة تنظيم الأصول الافتراضية، وكيف يُعامل ترميز العقارات وفق قواعد "
                      "إصدار الأصول الافتراضية، وواجبات التسويق والتحقق من العملاء.",
        "notes": [
            ("Licence needed to tokenize real estate or sell property tokens in Dubai",
             "The Virtual Assets Regulatory Authority (VARA) regulates virtual asset activities in Dubai, outside the "
             "DIFC, under Law No. 4 of 2022. Nobody may issue, offer or sell virtual assets to the public, or run "
             "exchange, broker-dealer, custody or management services, without the right VARA licence or approval. "
             "Tokens that represent a share of a property or its income are treated as Asset-Referenced Virtual Assets "
             "under the VARA Virtual Asset Issuance Rulebook: the issuance needs VARA approval and a whitepaper with "
             "clear risk disclosure, and the tokens must be distributed through a VARA-licensed provider. Selling "
             "property tokens with no VARA licence is a serious breach."),
            ("Customer checks and marketing rules for token sales",
             "VARA-licensed firms must verify every customer's identity and source of funds before they can buy "
             "(the Compliance and Risk Management Rulebook), so selling tokens to buyers with only an email address "
             "is not allowed. VARA's marketing rules apply to anyone promoting virtual assets to people in Dubai: "
             "adverts must be fair, clear and not misleading, must not promise guaranteed profit or 'zero risk', and "
             "must carry the required risk warnings."),
            ("DLD real estate tokenization project",
             "The Dubai Land Department runs a real estate tokenization initiative with VARA and the Dubai Future "
             "Foundation, under which title deeds of selected properties are tokenized and fractions are sold "
             "through a licensed platform, with ownership recorded at DLD. Any private tokenization business still "
             "needs its own VARA licence or approval and DLD involvement for the property title."),
        ],
    },
]


def _signature(b: dict) -> str:
    raw = VERSION + b["title"] + "".join(t + x for t, x in b["notes"])
    return hashlib.sha256(raw.encode()).hexdigest()


def ensure_loaded() -> int:
    """Adds or refreshes the briefs in the library. Returns how many briefs were (re)loaded."""
    loaded = 0
    for b in BRIEFS:
        sig = _signature(b)
        old = store.get_document_by_url(b["url"])
        if old and old.get("sha256") == sig and old.get("status") == "read":
            continue
        doc_id = store.add_document(b["url"], b["title"], b["regulator"], b["url"], sig, "", kind="html")
        texts = [f"{title}. {text}" for title, text in b["notes"]]
        vectors = embed.embed(texts)
        store.add_chunks(doc_id, [(i, t, v) for i, (t, v) in enumerate(zip(texts, vectors), start=1)])
        store.update_document(
            doc_id, title=b["title"], status="read", change_type="new", severity="medium",
            summary_en=b["summary_en"], summary_ar=b["summary_ar"], topics=b["topics"], affects={},
            key_points=[{"rule": text.split(". ")[0] + ".", "page": i}
                        for i, (title, text) in enumerate(b["notes"], start=1)][:6])
        loaded += 1
    return loaded
