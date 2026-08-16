### Define events such as:
LOGIN
LOGOUT

CREATE
UPDATE
DELETE

APPROVE
REJECT
REVIEW
LOCK
RELEASE

SAMPLE_CREATED
RESULT_ENTERED
RESULT_CHANGED

MATERIAL_RECEIVED
MATERIAL_MOVED
SAMPLING_REQUESTED

### Audit Event Data :
AuditEvent

id
timestamp
user
action
module
entity_type
entity_id
old_value
new_value
ip_address
description

### Example:
User: Ahmed
Action: UPDATE
Entity: TestResult
Entity ID: 1827

Before:
Result = 98.2

After:
Result = 98.5

Reason:
Correction after instrument verification