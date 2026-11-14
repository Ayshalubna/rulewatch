# RuleWatch evaluation results

Run on the live app (https://rulewatch.onrender.com) on 14 November 2026, model GPT-OSS 120B on Groq.

**Result: 26 / 26 overall verdicts matched the expected verdict.** 82 of 96 findings cite an official passage; the rest are marked "not covered yet".

| ID | Business type | Scenario | Expected | RuleWatch | Red / Yellow / Green | Seconds | Match |
|---|---|---|---|---|---|---|---|
| AG1 | Real estate agency / broker | Instagram ad without a permit | red | red | 3 / 1 / 0 | 11 | ✅ |
| AG2 | Real estate agency / broker | Ad promising guaranteed returns | red or yellow | red | 4 / 0 / 0 | 11 | ✅ |
| AG3 | Real estate agency / broker | New agent working before getting a broker card | red or yellow | red | 2 / 2 / 0 | 9 | ✅ |
| AG4 | Real estate agency / broker | Marketing an unregistered off-plan project | red | red | 2 / 0 / 2 | 9 | ✅ |
| AG5 | Real estate agency / broker | Big cash buyer, no ID checks | red | red | 4 / 0 / 0 | 20 | ✅ |
| AG6 | Real estate agency / broker | Using the standard lease brokerage forms | green or yellow | green | 0 / 0 / 4 | 20 | ✅ |
| DV1 | Developer | Buyer payments into company account | red | red | 2 / 0 / 2 | 17 | ✅ |
| DV2 | Developer | Launch event before registration | red or yellow | red | 2 / 0 / 0 | 24 | ✅ |
| DV3 | Developer | Setting service charges ourselves | red or yellow | red | 3 / 0 / 0 | 23 | ✅ |
| PM1 | Property manager | 20% rent increase on renewal | red | red | 1 / 2 / 1 | 13 | ✅ |
| LL1 | Individual landlord | Eviction by WhatsApp with 30 days notice | red | red | 3 / 0 / 1 | 24 | ✅ |
| LL2 | Individual landlord | Lease not registered | red or yellow | red | 1 / 1 / 0 | 20 | ✅ |
| LL3 | Individual landlord | Rent increase following the index with notice | green or yellow | yellow | 0 / 2 / 2 | 18 | ✅ |
| HH1 | Holiday homes / short-term rental operator | Airbnb listing without a holiday home permit | red | red | 4 / 0 / 0 | 18 | ✅ |
| OA1 | Owners association / community manager | Blocking access for unpaid service fees | red or yellow | red | 3 / 0 / 1 | 18 | ✅ |
| OA2 | Owners association / community manager | Collecting fees without an approved budget | red or yellow | red | 2 / 1 / 1 | 18 | ✅ |
| TK1 | Tokenization / PropTech startup | Selling property tokens without a licence | red | red | 4 / 0 / 0 | 21 | ✅ |
| TK2 | Tokenization / PropTech startup | Token buyers without ID checks | red | red | 4 / 0 / 0 | 18 | ✅ |
| TK3 | Tokenization / PropTech startup | Whitepaper with clear risk disclosure | green or yellow | green | 0 / 0 / 4 | 25 | ✅ |
| TK4 | Tokenization / PropTech startup | Token marketing promising profit | red or yellow | red | 4 / 0 / 0 | 21 | ✅ |
| MB1 | Mortgage broker / bank | Funds from an unknown third party | red or yellow | red | 3 / 0 / 1 | 15 | ✅ |
| VF1 | Valuation firm | Valuation by an unregistered valuer | red or yellow | yellow | 0 / 1 / 1 | 18 | ✅ |
| FM1 | Facility management / maintenance company | Sharing residents' data with marketers | red or yellow | yellow | 0 / 3 / 0 | 9 | ✅ |
| TN1 | Tenant or buyer (individual) | Tenant pays only the allowed increase | green or yellow | green | 0 / 0 / 4 | 27 | ✅ |
| TN2 | Tenant or buyer (individual) | Off-plan buyer paying the developer directly | red or yellow | red | 1 / 2 / 1 | 18 | ✅ |
| TN3 | Tenant or buyer (individual) | Buying without checking the title deed | red or yellow | red | 3 / 0 / 1 | 18 | ✅ |

## Scenario plans

- **AG1** (Real estate agency / broker): Tomorrow we will post a paid Instagram and TikTok ad for a 2-bed apartment in Dubai Marina. We have not applied for an advertising permit; we will do it after the ad gets leads.
- **AG2** (Real estate agency / broker): Our new campaign headline will be 'Guaranteed 10% rental return for 5 years' for units in JVC, without naming who gives the guarantee.
- **AG3** (Real estate agency / broker): We hired a new sales agent last week. She will show villas to clients and sign viewing agreements this weekend while her broker registration and card are still being processed.
- **AG4** (Real estate agency / broker): A developer friend gave us an off-plan tower that is not yet registered with the Land Department and has no escrow account yet. We will start marketing it and taking reservations now.
- **AG5** (Real estate agency / broker): A foreign buyer wants to pay AED 2.5 million in cash for a villa. To close fast we will skip the identity checks and source-of-funds questions.
- **AG6** (Real estate agency / broker): For every rental we will use the official lease brokerage agreement between owner and broker, and the agreement between broker and tenant.
- **DV1** (Developer): We start selling our new tower next month. Buyers will pay the 20% down payment into our normal company bank account while the escrow account is being opened.
- **DV2** (Developer): We will run a big launch event and billboards for our project before the project is registered and before we have marketing approvals.
- **DV3** (Developer): After handover we will set and collect service charges for the building at our own rate, without submitting a budget for approval.
- **PM1** (Property manager): On renewal we will increase all tenants' rent by 20% in one building, even where current rent is already close to the market average in the rental index.
- **LL1** (Individual landlord): I want to move into my apartment, so I will send my tenant a WhatsApp message giving 30 days to leave.
- **LL2** (Individual landlord): I will rent my flat with a simple paper contract and will not register it in Ejari to save time.
- **LL3** (Individual landlord): I will check the official rental index and send my tenant the allowed increase 90 days before the contract ends.
- **HH1** (Holiday homes / short-term rental operator): We will list 15 apartments in Downtown on Airbnb and Booking.com for nightly stays starting next week. We have no holiday home permit yet.
- **OA1** (Owners association / community manager): Owners who have not paid service charges will have their access cards blocked so they cannot use their own apartments until they pay.
- **OA2** (Owners association / community manager): This year we will collect higher service fees from owners. The new budget has not been approved by the regulator yet.
- **TK1** (Tokenization / PropTech startup): We will sell digital tokens representing shares of a Dubai Marina apartment to the public from AED 1,000 each. We have not applied for any VARA licence.
- **TK2** (Tokenization / PropTech startup): To grow fast, buyers can purchase our property tokens with only an email address. No ID or source-of-funds checks.
- **TK3** (Tokenization / PropTech startup): Before our licensed token issuance we will publish a whitepaper explaining the property, how rental income is shared with token holders, and the risks.
- **TK4** (Tokenization / PropTech startup): Our social media ads will say 'Buy property tokens, guaranteed 12% yearly profit, zero risk'.
- **MB1** (Mortgage broker / bank): A buyer's down payment will come from a company abroad we don't know. We will accept it without asking who owns the company.
- **VF1** (Valuation firm): To handle more mortgage valuations, our junior staff who are not registered valuers will sign valuation reports.
- **FM1** (Facility management / maintenance company): We will share residents' names, phone numbers and flat numbers with a marketing partner without asking residents.
- **TN1** (Tenant or buyer (individual)): My landlord asked for a 15% increase. I will check the rental index and agree only to the increase the rules allow.
- **TN2** (Tenant or buyer (individual)): I am buying an off-plan flat. The sales agent asked me to transfer my payment to the developer's general company account, not an escrow account. I will do it.
- **TN3** (Tenant or buyer (individual)): I will buy a ready apartment from a private seller and pay him directly without checking the title deed or registering the transfer with the Land Department.
