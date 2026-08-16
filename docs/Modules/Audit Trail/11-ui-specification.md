# UI Specification

## Audit Viewer Page

### Route
```
/audit
```

### Permissions
- Requires `AUDIT_VIEW` permission
- Module-scoped filtering for QC Supervisor

### Layout
```
┌─────────────────────────────────────────────────────────────────┐
│ Header: "Audit Trail"                              [Export]     │
├─────────────────────────────────────────────────────────────────┤
│ Filters Bar (collapsible)                                       │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│ │ Date     │ │ Actor    │ │ Action   │ │ Module   │ │ Entity │ │
│ │ Range    │ │ Search   │ │ Multi    │ │ Multi    │ │ Type   │ │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘ │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│ │ Entity   │ │ Field    │ │ Correl.  │ │ Session  │ │ [Search]│ │
│ │ ID       │ │ Name     │ │ ID       │ │ ID       │ │ [Reset] │ │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ Results Table                                                     │
│ ┌───┬────────────┬────────┬────────┬────────┬────────┬────────┐ │
│ │ # │ Timestamp  │ Actor  │ Action │ Module │ Entity │ ...  │ │
│ ├───┼────────────┼────────┼────────┼────────┼────────┼──────┤ │
│ │ 1 │ 2024-01-15 │ J. Doe │ FIELD_ │ RECEIV │ MatBat │ [>]  │ │
│ │   │ 10:30:00   │        │ CHANGE │ ING    │ ch-123 │      │ │
│ ├───┼────────────┼────────┼────────┼────────┼────────┼──────┤ │
│ │ 2 │ 2024-01-15 │ SYSTEM │ TRANS  │ ANAL.  │ Sample │ [>]  │ │
│ │   │ 10:29:45   │        │ ITION  │ YSIS   │ -456   │      │ │
│ └───┴────────────┴────────┴────────┴────────┴────────┴──────┘ │
│ Pagination: [<] 1 2 3 ... 154 [>]  Showing 1-25 of 15420       │
├─────────────────────────────────────────────────────────────────┤
│ Status Bar: "Hash chain: VERIFIED (last checked 2024-01-15      │
│ 02:00 UTC)  |  Export: 2 pending  |  Archive: 2023 complete"   │
└─────────────────────────────────────────────────────────────────┘
```

### Filter Details

| Filter | Component | Behavior |
|---|---|---|
| Date Range | Dual date-time picker | Presets: Today, Yesterday, Last 7d, Last 30d, Custom |
| Actor | User autocomplete | Search by name/email; "System" option |
| Action | Multi-select chips | All 7 actions; default all |
| Module | Multi-select chips | All 10 modules; default all |
| Entity Type | Autocomplete | Known entity types from catalog |
| Entity ID | Text input | UUID validation |
| Field Name | Text input | For FIELD_CHANGE |
| Correlation ID | Text input | UUID |
| Session ID | Text input | UUID |

### Table Columns

| Column | Display | Sortable | Filterable |
|---|---|---|---|
| # | Sequence number | ✅ | ✅ |
| Timestamp | YYYY-MM-DD HH:mm:ss.ffffff | ✅ | Via date range |
| Actor | Name (avatar) | ✅ | Via actor filter |
| Action | Badge (color-coded) | ✅ | Via action filter |
| Module | Badge (color-coded) | ✅ | Via module filter |
| Entity | Type + truncated ID | ✅ | Via entity filters |
| Field | Field name (FIELD_CHANGE only) | ❌ | Via field filter |
| Expand | Chevron button | ❌ | ❌ |

### Row Expansion (Detail Panel)

Click chevron → Slide-down panel:

```
┌────────────────────────────────────────────────────────────┐
│ Event Details                                    [Copy JSON] │
├────────────────────────────────────────────────────────────┤
│ ID: uuid | Sequence: 1,234,567 | Hash: d4e5f6...          │
│ Actor: John Doe (john@example.com) | Type: USER            │
│ IP: 192.168.1.100 | Session: uuid | Correlation: uuid      │
├────────────────────────────────────────────────────────────┤
│ Changes:                                                     │
│ ┌──────────────┬─────────────────────┬────────────────────┐ │
│ │ Field        │ Old Value           │ New Value          │ │
│ ├──────────────┼─────────────────────┼────────────────────┤ │
│ │ manufacturer │ Acme Corp (uuid)    │ Beta Ltd (uuid)    │ │
│ │ _id          │                     │                    │ │
│ └──────────────┴─────────────────────┴────────────────────┘ │
├────────────────────────────────────────────────────────────┤
│ Digital Signature: ✅ VERIFIED                               │
│ Meaning: "Approved Certificate of Analysis for batch..."    │
│ Signed by: Jane Smith | 2024-01-15 10:30:00.123456Z        │
│ Type: SHARED_SECRET_TOTP | Data Hash: a1b2c3...            │
└────────────────────────────────────────────────────────────┘
```

### Color Coding

| Action | Badge Color |
|---|---|
| CREATE | Green |
| UPDATE | Blue |
| DELETE | Red |
| TRANSITION | Purple |
| SIGN | Gold |
| VIEW_SENSITIVE | Gray |
| FIELD_CHANGE | Orange |

| Module | Badge Color |
|---|---|
| RECEIVING | Indigo |
| SAMPLING | Teal |
| ANALYSIS | Blue |
| CERTIFICATE | Purple |
| RELEASE | Green |
| USER_MGMT | Orange |
| SECURITY | Red |
| WAREHOUSE | Brown |
| MONOGRAPH | Pink |
| SYSTEM | Gray |

---

## Export Dialog

### Trigger
- Click "Export" button in header
- Requires `AUDIT_EXPORT` permission

### Modal Flow

```
Step 1: Configure Export
┌────────────────────────────────────────┐
│ Export Audit Events                    │
├────────────────────────────────────────┤
│ Format:  ○ PDF    ○ CSV                │
│ Date Range: [Same as viewer filters]   │
│ Filters: [Inherited from viewer]       │
│                                        │
│ Estimated records: 15,420              │
│ ⚠ Requires QC Manager approval (>10K)  │
│                                        │
│ [Cancel]              [Request Export] │
└────────────────────────────────────────┘

Step 2: Approval Pending (if >10K)
┌────────────────────────────────────────┐
│ Export Requested                       │
├────────────────────────────────────────┤
│ Your export requires approval.         │
│ QC Manager will be notified.           │
│                                        │
│ Request ID: uuid                       │
│ Status: PENDING_APPROVAL               │
│                                        │
│ [Close]                                │
└────────────────────────────────────────┘

Step 3: Download Ready (Notification)
┌────────────────────────────────────────┐
│ Export Complete ✅                     │
├────────────────────────────────────────┤
│ audit-export-20240115-103000.pdf       │
│ 15,420 records | 2.4 MB                │
│ SHA-256: a1b2c3...                     │
│                                        │
│ [Download]    [View in List]           │
└────────────────────────────────────────┘
```

### Export List Page
```
/audit/exports
```
- Table: ID, Requested By, Date Range, Format, Status, Records, Requested At, Actions
- Actions: Download (if completed), View Details, Cancel (if pending)

---

## Integrity Verification Page

### Route
```
/audit/integrity
```
- Requires `AUDIT_VERIFY` permission

### Layout
```
┌────────────────────────────────────────────────────────────┐
│ Hash Chain Verification                     [Run Check]    │
├────────────────────────────────────────────────────────────┤
│ Last Run: 2024-01-15 02:00:00 UTC | Status: ✅ PASSED      │
│ Events Verified: 2,847,192 | Duration: 4m 32s              │
├────────────────────────────────────────────────────────────┤
│ Manual Verification                                          │
│ Range: [From Sequence] to [To Sequence]  [Verify]          │
│ OR Date Range: [From] to [To]              [Verify]        │
├────────────────────────────────────────────────────────────┤
│ Results:                                                     │
│ ┌─────────┬────────────┬──────────┬──────────┬────────────┐ │
│ │ Status  │ Range      │ Events   │ Duration │ Details    │ │
│ ├─────────┼────────────┼──────────┼──────────┼────────────┤ │
│ │ ✅ PASS │ 1-1,000,000│ 1,000,000│ 2m 15s   │ [View]     │ │
│ │ ❌ FAIL │ 1,000,001- │ 500,000  │ 1m 02s   │ [View]     │ │
│ │         │ 1,500,000  │          │          │ 3 mismatch │ │
│ └─────────┴────────────┴──────────┴──────────┴────────────┘ │
└────────────────────────────────────────────────────────────┘
```

### Mismatch Detail Modal
```
┌────────────────────────────────────────────────────────────┐
│ Integrity Mismatch Details                                 │
├────────────────────────────────────────────────────────────┤
│ Sequence: 1,234,567                                        │
│ Timestamp: 2024-01-15 10:30:00.123456Z                    │
│ Error: CHAIN_BROKEN                                        │
│ Expected Previous Hash: a1b2c3d4e5f6...                    │
│ Actual Previous Hash:   deadbeefcafe...                    │
│                                                         │
│ Event Data:                                                │
│ { "action": "FIELD_CHANGE", "module": "RECEIVING", ... }  │
│                                                         │
│ [Export for Forensics]    [Acknowledge]                   │
└────────────────────────────────────────────────────────────┘
```

---

## Archive Management Page

### Route
```
/audit/archives
```
- Requires `AUDIT_ARCHIVE` permission (System Admin only)

### Layout
- Table: ID, Date Range, Event Count, Status, Initiated By, Verified By, Initiated At, Verified At, Actions
- Actions: Verify (if IN_PROGRESS), View Details, Detach Partition (if VERIFIED)

---

## Electronic Signature Setup

### Route
```
/profile/signature
```
- Available to all authenticated users

### TOTP Setup Flow
```
Step 1: Choose Method
┌────────────────────────────────────────┐
│ Configure Electronic Signature         │
├────────────────────────────────────────┤
│ Method:  ○ TOTP (Authenticator App)    │
│          ○ Static Secret               │
│                                        │
│ [Next]                                 │
└────────────────────────────────────────┘

Step 2a: TOTP - Scan QR
┌────────────────────────────────────────┐
│ Scan QR Code with Authenticator App    │
├────────────────────────────────────────┤
│ [QR Code Image]                        │
│                                        │
│ Secret: JBSWY3DPEHPK3PXP (manual entry)│
│                                        │
│ Enter 6-digit code: [______] [Verify]  │
└────────────────────────────────────────┘

Step 2b: Static - Enter Secret
┌────────────────────────────────────────┐
│ Enter Your Static Secret               │
├────────────────────────────────────────┤
│ Secret: [________________] [Show]      │
│ Confirm: [________________]            │
│                                        │
│ [Save]                                 │
└────────────────────────────────────────┘

Step 3: Success
┌────────────────────────────────────────┐
│ ✅ Electronic Signature Configured     │
├────────────────────────────────────────┤
│ Method: TOTP                           │
│ You can now sign approvals.            │
│                                        │
│ [Done]                                 │
└────────────────────────────────────────┘
```

---

## Signature Prompt Modal (Reusable Component)

### Trigger
- Any action requiring electronic signature (approve certificate, review results, release material)

### Modal
```
┌────────────────────────────────────────┐
│ Electronic Signature Required          │
├────────────────────────────────────────┤
│ Action: Approve Certificate of Analysis│
│ Meaning: "Approved CoA for batch       │
│ MB-2024-001"                           │
│                                        │
│ Method: TOTP (Authenticator App)       │
│                                        │
│ Enter 6-digit code: [______]           │
│ Time remaining: 25s ⏱                  │
│                                        │
│ [Cancel]              [Sign]           │
└────────────────────────────────────────┘
```

### States
- **Loading**: Verifying...
- **Success**: ✅ Signed — auto-close after 1s
- **Error**: ❌ Invalid code (shake animation)
- **Locked**: 🔒 Too many attempts — try again in 15m

---

## Notifications

### In-App Notification Center
- Export completed/failed
- Archive completed/failed
- Integrity check passed/failed
- Signature configured/rotated
- Approval required (for exports)

### Email Notifications (Configurable)
- Export ready for download
- Archive verification required
- Critical integrity alert
- Signature method changed

---

## Responsive Behavior

| Breakpoint | Adjustments |
|---|---|
| Desktop (>1024px) | Full table, side-by-side filters |
| Tablet (768-1024px) | Collapsible filter drawer, horizontal scroll table |
| Mobile (<768px) | Stack filters, card-based event list, no table |

---

## Accessibility

- All filters: proper labels, ARIA descriptions
- Table: semantic `<table>`, sortable headers with `aria-sort`
- Expandable rows: `aria-expanded`, keyboard accessible (Enter/Space)
- Color coding: never sole indicator (always with text/icon)
- Modals: focus trap, ESC to close, restore focus
- Timers: announce remaining time to screen readers