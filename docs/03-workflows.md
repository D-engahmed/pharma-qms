# Business Workflows

## 1. Material Workflow

RECEIVED
   ↓
QUARANTINE
   ↓
SAMPLING_REQUESTED
   ↓
SAMPLED
   ↓
UNDER_ANALYSIS
   ↓
UNDER_REVIEW
   ↓
RELEASED


Alternative:


Any applicable stage
       ↓
    REJECTED


## 2. Sampling Workflow


REQUESTED
   ↓
ASSIGNED
   ↓
IN_PROGRESS
   ↓
COMPLETED (Sampled)


## 3. Analysis Workflow


NOT_STARTED
   ↓
IN_PROGRESS
   ↓
COMPLETED
   ↓
UNDER_REVIEW
   ↓
APPROVED (Tested)


Alternative:

UNDER_REVIEW
     ↓
  REJECTED

## 4. Certificate Workflow

DRAFT
   ↓
UNDER_REVIEW
   ↓
APPROVED
   ↓
LOCKED

Alternative:
Rejected


## 5. Material Release

Material can only be released when:

* Required analysis is complete.
* Required results are acceptable.
* Required review is complete.
* Certificate is approved.
* Required release permission is present.

## 6. Workflow Transition Rules

Document every allowed transition.

| Current            | Action               | Next               | Permission                 |
| ------------------ | -------------------- | ------------------ | -------------------------- |
| QUARANTINE         | Request Sampling     | SAMPLING_REQUESTED | receiving.request_sampling |
| SAMPLING_REQUESTED | Assign               | ASSIGNED           | sampling.assign            |
| ASSIGNED           | Start                | IN_PROGRESS        | sampling.create            |
| IN_PROGRESS        | Complete             | COMPLETED          | sampling.create            |
| COMPLETED          | Start Analysis       | IN_PROGRESS        | analysis.create            |
| COMPLETED          | Submit               | UNDER_REVIEW       | analysis.submit            |
| UNDER_REVIEW       | Approve              | APPROVED           | analysis.approve           |
| APPROVED           | Generate Certificate | DRAFT              | certificate.create         |
| DRAFT              | Submit               | UNDER_REVIEW       | certificate.review         |
| UNDER_REVIEW       | Approve              | APPROVED           | certificate.approve        |
| APPROVED           | Lock                 | LOCKED             | certificate.lock           |
| LOCKED             | Release              | RELEASED           | material.release           |
