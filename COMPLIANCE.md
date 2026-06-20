# Compliance & Methodology

This tool exists to help a wealth/asset-management firm **identify and prioritise publicly
documented UHNW prospects** of Indian origin. It is a research aid — not a substitute for legal
review. Confirm your own obligations with counsel and your DPO before any outreach.

## Principles

1. **Public sources only.** Use data that is lawfully public (rich lists, news, regulatory
   filings, company disclosures) or licensed from a provider whose terms permit your use.
   Do not scrape sites in breach of their terms, defeat access controls, or buy hacked/leaked data.
2. **Lawful basis for processing.** Holding personal data on prospects triggers data-protection
   law. Identify your lawful basis (commonly *legitimate interest* for B2B prospecting) and
   document a Legitimate Interest Assessment.
3. **Transparency & rights.** Be ready to tell a person how you got their data and to honour
   access, rectification, objection and erasure requests. Maintain a suppression/opt-out list.
4. **Data minimisation & security.** Collect only what you need, store it securely, restrict
   access, and set a retention period.
5. **No special-category or sensitive data**, and nothing about minors.

## Key regimes (verify current text — laws change)

- **EU/UK GDPR** — applies to prospects in the UK/Europe; legitimate-interest basis, right to
  object to direct marketing, PECR/ePrivacy rules on electronic marketing.
- **India DPDP Act 2023** — consent/legitimate-use rules for processing personal data of
  individuals in India; notice and rights obligations.
- **UAE PDPL**, **Singapore PDPA** (incl. Do-Not-Call registry), **US state laws** (e.g. CCPA/CPRA
  in California) — apply by prospect location.
- **Marketing rules** — CAN-SPAM (US), CASL (Canada), and local e-marketing/telemarketing rules
  govern *how* you contact people once identified.

## Source-specific notes

- **SEC EDGAR** is public US regulatory data; insider (Form 3/4/5) filings are published by law.
  Provide a real, descriptive `User-Agent` and respect SEC's fair-access rate limits.
- **Stock exchanges (NSE/BSE/NASDAQ/NYSE/ADX)** publish promoter/insider holdings — public, but
  use within each exchange's terms. Material non-public information must never be used.
- **Paid providers (Apollo/ZoomInfo)** — your use is bound by their contract and DPA; they carry
  obligations to data subjects you must support.
- **LinkedIn and similar** — automated scraping generally breaches their terms; prefer official
  APIs or licensed data.

## Methodology (how a lead is qualified & scored)

1. **Collect** candidate records from enabled sources.
2. **Qualify** against a UHNW floor (default $30m investable) and Indian-origin diaspora relevance.
3. **De-dupe & merge** records of the same person across sources.
4. **Score 0–100** (see README): net-worth tier, liquidity/addressability, geo fit,
   wealth-source fit, accessibility.
5. **Verify before outreach** — every figure and identity is a starting hypothesis to confirm.

## What this tool does NOT do

- It does not contact anyone, send marketing, or execute any transaction.
- It does not assert that any listed individual is a client or wishes to be contacted.
- It does not guarantee accuracy of third-party figures.
