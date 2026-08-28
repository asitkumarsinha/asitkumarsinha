# Marg ERP — Business Logic

**Companion to:** [White paper](./WHITE_PAPER.md)  
**Source:** Public product copy and help articles on [margcompusoft.com](https://margcompusoft.com/) and Marg CARE (ERP-to-ERP).  
**Scope:** Logical operating model as marketed. Internal source code, unpublished Control Room flags, and partner-specific customisations are out of scope.

This document describes **who acts**, **what objects exist**, **which rules fire**, and **how value moves** through the Marg ecosystem.

---

## 1. Design principles (inferred)

1. **Invoice is the system of record for stock and tax.** Every sale/purchase mutates inventory, party ledger, GST registers, and (optionally) e-invoice / e-way / WhatsApp.  
2. **Pharma/FMCG physics first.** Batch, expiry, MRP, scheme (free/bonus), and HSN are first-class, not afterthoughts.  
3. **Network beats data entry.** ERP-to-ERP, photo/PDF purchase import, and eRetail exist to eliminate typing between trading partners who already run Marg.  
4. **Compliance is a pipeline, not a report.** Bill → IRN / e-way → GSTR JSON/Excel/CSV → portal.  
5. **Role-split mobile.** Owner, retailer, salesman, and delivery staff get different apps, not one mega-app.

---

## 2. Actors and roles

| Actor | Typical product | Primary jobs |
| --- | --- | --- |
| Chemist / medical retailer | Chemist / Pharmacy / Retail | Counter billing, expiry, substitutes, ABHA/DHC extras, order from stockist |
| Kirana / grocery / garment / jewellery / salon / restaurant | Vertical retail / POS | Fast POS, barcode, schemes, multi-tender |
| Pharma / FMCG distributor / stockist | Distribution / Pharma software | Receive chemist orders, godowns, schemes, e-way, collections |
| Manufacturer | Pharma ERP / Manufacturing | RM–PM–SFG–FG, costing, production, excise/gate pass (legacy), GST |
| Field salesman | eOrder / SFAXpert | Book orders, collect, GPS |
| Delivery staff | eDelivery | Dispatch, proof of delivery, rack/mobile rack |
| Business owner | eOwner / Marg Cloud | Multi-branch KPIs, credit, cash |
| Accountant / CA | GST modules, CA community | Returns, TDS/TCS, audit packs |
| Partner / BSS | Partner portal, BSS login | Sell, implement, AMC, training |
| Bank | Connected banking | NEFT/RTGS, reconciliation |
| GSTN / NIC | e-invoice, e-way, GST portal | Statutory IDs and filings |
| Patient / end consumer | POS, MargMart, Digital Healthcare, My Shop QR | Buy, scan QR, consult, loyalty |

**Access pattern:** Silver edition sells “1 full + 1 view-only”; Gold sells unlimited users. User-wise / counter-wise / shift-wise cash is a first-class retail control.

---

## 3. Core domain objects

```
Company (GSTIN, FY, branches)
  └── Godown / Store / Rack
        └── Item (HSN, salt, schedule, barcode)
              └── Batch (qty, MRP, expiry, rate, scheme)
  └── Party (customer / supplier / doctor)
        └── Ledger + CreditLimit + Outstanding + PDC
  └── Document (SO, PO, SI, PI, DN, CN, Payment, Receipt, JV)
  └── TaxLine (CGST/SGST/IGST, TCS, TDS)
  └── Scheme / Discount / Loyalty
  └── Claim (purchase/sale claim vs company)
```

### 3.1 Item master (especially pharma)

- Identity: name, pack, company, HSN/SAC, barcode.  
- Clinical/trade: salt composition, substitutes, Schedule H / H1 / narcotics / TB reporting flags.  
- Planning: reorder level, fast/slow/non-moving classification, focused vs dump vs near-expiry buckets.  
- Mapping keys for ERP-to-ERP and purchase import (local item ↔ distributor item).

### 3.2 Batch

- Quantity on hand per godown.  
- Expiry date; near-expiry window drives alerts and return-to-supplier workflows.  
- MRP vs sale rate vs scheme (free qty).  
- Indexing often by expiry (FEFO-style usage is implied by “expiry management”).

### 3.3 Party

- GSTIN, billing/shipping, credit limit, salesman, beat (distribution).  
- Family ledger group (chemist: one family, many patients).  
- Doctor (for commission / company-wise sales reports).  
- Distributor mapping for ERP-to-ERP.

### 3.4 Commercial documents

| Document | Effect |
| --- | --- |
| Sales invoice / POS bill | −stock, +receivable or cash, GST out, optional IRN, WhatsApp |
| Purchase bill | +stock, +payable, GST in, claim tracking |
| Sales/purchase order | Reservation / pipeline; ERP-to-ERP SO lands as order on distributor |
| Debit / credit note | Tax and value correction |
| E-way bill | Movement compliance above threshold |
| Payment / receipt | Ledger + reconciliation; MargPay auto-links bill |
| Production / issue / receipt | Manufacturing inventory state changes |

---

## 4. End-to-end process flows

### 4.1 Retail counter (happy path)

```
Scan/search item (barcode | name | salt | substitute)
  → Select batch (prefer valid, non-expired; warn near-expiry)
  → Apply MRP, discount, scheme, GST (CGST/SGST or IGST)
  → Tender: cash | UPI | card | wallet | credit (check live credit limit)
  → Print / WhatsApp invoice
  → Decrement batch qty; update cash drawer / shift; queue GST register
  → Optional: ABHA 2.0 line (chemist incentive), DHC upsell, loyalty points
```

**Rules**

- Do not sell expired batch; alert near-expiry.  
- If customer credit limit exceeded, notify during billing.  
- Multi-tender allowed; denomination tracking for cash.  
- User/counter/shift isolation for cash summary.  
- Substitute suggestion when asked SKU is missing (salt match + supplier location via PharmaNXT).

### 4.2 Purchase and replenishment

```
Trigger: reorder report (sale velocity | profit | stock days | shortage)
     or  ERP-to-ERP cart
     or  Photo / PDF / Excel / CSV of supplier bill
  → Map lines to item master
  → Create purchase / GRN
  → Receive batches (qty, expiry, MRP, free qty)
  → Book payable; GST ITC register
  → Register purchase claim if scheme/company benefit exists
```

**Rules**

- Prefer import over typing (“100% accuracy” claim).  
- Map unknown SKUs before posting.  
- Free/bonus qty from schemes must land as stock without inflating purchase value incorrectly (scheme engine).  
- Near-expiry and dump stock feed “push sale” and return-to-supplier.

### 4.3 ERP-to-ERP ordering (two-sided)

**Retailer setup**

1. Map distributor party.  
2. Map items (including bulk auto-map).  
3. Browse live stock, rate, scheme on distributor.  
4. Cart → Place order (`Transaction > ERP to ERP Order` in help docs).

**Distributor setup**

1. `Master > eBusiness Setup` → Register company.  
2. Receive orders into ERP (no phone/WhatsApp typing).  
3. Shortage visibility; convert to invoice / pick / dispatch.

**Network rule:** both ends must be on Marg; value is error reduction and speed, not a public open marketplace.

### 4.4 Distribution / warehouse

```
Inbound order (ERP-to-ERP | eOrder | phone entered)
  → Allocate batch (FEFO / scheme / MRP constraints)
  → Pick (rack / mobile rack)
  → Invoice + e-invoice (IRN) + e-way if goods movement requires
  → eDelivery assign
  → Proof of delivery → receivable
  → WhatsApp reminder if overdue
```

**Rules**

- Multi-godown stock truth.  
- Credit limit on chemist.  
- Scheme date/qty/batch conditions.  
- Expiry returns to principal to avoid dump loss.

### 4.5 Manufacturing (pharma ERP pages)

Inventory layers: **raw material, packing material, semi-finished, finished goods**.

```
Plan production → issue RM/PM → process / assemble → receipt FG
  → Cost rollup (bulk vs FG)
  → FG batch + expiry
  → Sale as in distribution
  → Wastage analysis, multi-store
```

Supporting: production planning, costing, gate pass / invoice, multi-warehouse, MIS.

### 4.6 GST “billing to filing”

```
Taxable document posted
  → Split CGST/SGST vs IGST from place of supply
  → If turnover/threshold: generate e-invoice (IRN); advertised ~₹0.15 / auto IRN
  → If movement threshold: e-way bill
  → Period close: GSTR-1 / 3B (and other returns as applicable), TCS/TDS
  → Export Excel | JSON | CSV to GSTN
  → Internal audit reports; GST 2.0 / IMS / GSTR-9 Table 8A readiness
```

**Rules**

- Tax computed at billing time, not as a night batch only.  
- Portal visit is optional if APIs/files succeed; fallback is file upload.  
- TDS/TCS calculated in accounting, not only in GST returns.

### 4.7 Money movement

```
Invoice outstanding
  → Reminder (WhatsApp / SMS / email)
  → Collect: cash | cheque/PDC | MargPay QR/UPI | connected NEFT/RTGS
  → Auto reconcile (140+ banks claimed)
  → Bill-by-bill matching
```

**MargPay commercial rule (as advertised):** 0% service charge to merchant; 2% cashback for retailers (verify contractually; this is marketing).

### 4.8 Multi-company / multi-location

- Company is a licensed object (Nano/Basic cap at 2; Gold unlimited).  
- DMSXpert / Marg Cloud: central users, branches, logs.  
- Stock and books can be per location with consolidated owner view.

---

## 5. Decision and calculation engines

### 5.1 Tax

- **Intra-state:** CGST + SGST.  
- **Inter-state:** IGST.  
- HSN from item; GSTIN from party; place of supply from shipping.  
- Reverse charge / TCS / TDS when nature of supply requires (feature-listed, not fully specified publicly).

### 5.2 Price and scheme

Inputs: MRP, party rate list, date-effective scheme, qty slabs, free goods, combo, loyalty, making-charge/weight/purity (jewellery), doctor commission (chemist).

Output: net taxable, discount, free qty, tax, margin reports.

### 5.3 Inventory health

Classification used in copy:

- Fast / slow / non-moving  
- Focused / dump / near-expiry  
- Reorder from sale, profit, or stock-cover days  

Alerts: low stock, expiry, payments.

### 5.4 Credit

Live check at invoice time; notifications; outstanding ageing; PDC.

### 5.5 Jewellery-specific (vertical overlay)

Weight × rate × purity + making charges; old gold exchange; karigar/repair/approval; high-value barcode/tag.

### 5.6 Restaurant-specific

Dine-in / takeaway / delivery; KOT to kitchen; bill split; dish popularity.

---

## 6. Integration logic

| Rail | Business effect |
| --- | --- |
| GSTN / e-invoice / e-way | Legal invoice identity and transit |
| WhatsApp / SMS / email | Invoice delivery and collection |
| Banks (ICICI, Axis, SBI, J&K, IndusInd, 140+ recon) | Pay out and auto-match |
| Barcode / pole display / cash drawer / touch POS | Counter speed |
| MargMart / My Shop QR | Consumer or retailer self-order |
| ABHA 2.0 / Digital Healthcare | Chemist extra income (e.g. ₹20 per ABHA billing in campaign copy) |
| OCR / photo-to-purchase | Inbound invoice capture |

---

## 7. Reporting (decision layer)

Advertised **1,000+ MIS reports**, including:

- GST, trial balance, P&L, balance sheet, cash flow, ledger  
- Stock, expiry, dump, reorder, godown  
- Salesman / counter / shift / day cash  
- Doctor commission and company-wise pharma sales  
- Claims and scheme benefit tracking  
- Production costing and wastage (manufacturing)

**Operating rule:** operational users live in transaction screens; owners live in eOwner + MIS; accountants live in GST and financial statements.

---

## 8. Licensing logic (commercial rules)

- Geography: India & South Asia (INR) vs rest of world (USD).  
- GST 18% extra on license.  
- Extra **user** and extra **company** are billable SKUs except Gold (unlimited).  
- Customisation is a separate SOW.  
- Unauthorized marketplace purchase → no official support.  
- Attach products (Cloud, Books, Pay, e-invoice per IRN, healthcare, training) stack on the core license.

---

## 9. Control and security (as claimed)

- User rights (full vs view-only).  
- Counter and cash-drawer access.  
- Marg Cloud: branch, user, data, log control.  
- “7-layered data security”; Azure encryption mentioned in third-party interviews for cloud.  
- Audit-ready books for GST and internal audit.

---

## 10. State machine (document)

```
Draft → Confirmed/Posted → (IRN assigned) → (E-way assigned)
                  ↓
            Partially paid → Settled
                  ↓
         Credit/Debit note / Cancel (statutory rules)
```

Inventory moves only on **posted** goods documents. GST registers move with posted taxable documents. Bank/cash moves with payment documents. ERP-to-ERP orders are **pre-invoice** states on the distributor until billed.

---

## 11. Value-chain map (pharma)

```
Manufacturer (Marg Manufacturing)
        ↓ FG invoices + e-way
Distributor / Stockist (Marg Distribution)
        ↓ ERP-to-ERP / eRetail / schemes
Chemist (Marg Chemist)
        ↓ POS + GST + optional ABHA/DHC
Patient
```

Marg’s distinctive business logic is **closing the middle arrow** so the chemist’s shortage becomes a structured order on the stockist’s ERP, with shared item mapping, live rate/scheme, and no re-keying.

---

## 12. Implementation checklist (logical, not a user manual)

1. Create company, FY, GSTIN, godowns.  
2. Load item master (or PharmaNXT-assisted).  
3. Opening batches with expiry.  
4. Party masters + credit limits + GSTIN.  
5. Tax and series (invoice numbering).  
6. User roles and counters.  
7. Bank and MargPay.  
8. e-invoice / e-way credentials.  
9. Distributor/item mapping for ERP-to-ERP.  
10. WhatsApp templates; reorder parameters; scheme calendar.  
11. Go-live parallel run; partner AMC and GST update channel.

---

*Figures, prices, and slogans are taken from Marg’s public site as of August 2026 and may change. Use this as a product/domain blueprint, not as a contract or statutory opinion.*
