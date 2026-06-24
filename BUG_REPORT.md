# Bug Report — Pretty Good AI Agent Evaluation

**Tester:** Saleeq Adnan Syed  
**Test Date:** June 23-24, 2026  
**Phone Number Used:** +14244281474  
**Total Calls:** 11 calls across 10 scenarios

---

## Summary

| Severity | Count |
| -------- | ----- |
| Critical | 2     |
| High     | 3     |
| Medium   | 3     |

---

## BUG-001 — Demo patient profile leaks into every call

**Severity:** Critical  
**Scenario:** All scenarios (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)  
**Transcript:** transcript_1_new_appointment_20260623_194138.txt  
**Timestamp in call:** ~0:05

**What happened:**  
Every single call opened with the agent asking "Am I speaking with TEST?" -- the name of
the demo patient from pgai.us/athena. Regardless of who was calling, the agent identified
the caller as the demo test patient. This occurred across all 11 test calls.

**Why it is a problem:**  
The demo patient profile is not being isolated from production call sessions. Every real
caller is being greeted as the demo test patient. In a real deployment, every patient would
be asked if they are someone else entirely. This is a fundamental data isolation failure
that would destroy patient trust and create HIPAA compliance concerns.

---

## BUG-002 — Agent catastrophically halluccinates patient name when confirming spelling

**Severity:** Critical  
**Scenario:** 1 (new_appointment)  
**Transcript:** transcript_1_new_appointment_20260623_194138.txt  
**Timestamp in call:** ~1:30

**What happened:**  
Sarah Johnson spelled her name letter by letter: S-A-R-A-H J-O-H-N-S-O-N. The agent
confirmed back: "your first name is spelled S-A-R-H, and your last name is
J-O-A-C-H-I-N-A-S-O-I-N." The agent hallucinated a 14-character nonsense string in place
of the 7-character last name the patient had just spelled.

**Why it is a problem:**  
A patient spelling their name for identity verification expects exact confirmation. The agent
is not reliably capturing spoken letter sequences. If the agent were to save this hallucinated
name to a patient record, the record would be permanently corrupted. This is a direct patient
safety concern.

---

## BUG-003 — Agent repeatedly asks patient to spell name after already confirming it

**Severity:** High  
**Scenario:** 1 (new_appointment), 2 (reschedule)  
**Transcript:** transcript_1_new_appointment_20260623_194138.txt  
**Timestamp in call:** ~1:00 and ~1:45

**What happened:**  
In scenario 1, Sarah Johnson was asked to spell her name three separate times in the same
call. After spelling it the second time, the agent confirmed it incorrectly, then asked her
to spell it again. In scenario 2, Michael Torres was asked to spell his name twice despite
the agent already having confirmed his date of birth.

**Why it is a problem:**  
Repeatedly asking patients for the same information is a poor user experience and suggests
the agent has no short-term memory of what was already collected in the current call. For a
patient calling to schedule an appointment, being asked to spell their name three times would
cause frustration and call abandonment.

---

## BUG-004 — Agent reveals patient phone number without patient providing it

**Severity:** High  
**Scenario:** 2 (reschedule), 4 (cancel_appointment)  
**Transcript:** transcript_4_cancel_appointment_20260623_194138.txt  
**Timestamp in call:** ~2:15

**What happened:**  
Robert Davis explicitly said "I'd rather not give out my phone number if that's okay."
The agent then responded: "I have your phone number as 424-428-1474. Is that correct?"
The agent revealed a phone number the patient had specifically declined to provide.

**Why it is a problem:**  
The agent is surfacing PII from a previous session or the demo profile without patient
consent. A patient who declined to share their phone number had it read back to them
unprompted. This is a privacy violation and would be a HIPAA compliance issue in production.

---

## BUG-005 — Agent terminates calls with unresolved patient needs

**Severity:** High  
**Scenario:** 1, 2, 3, 4, 7, 10 (multiple)  
**Transcript:** transcript_2_reschedule_20260623_194138.txt  
**Timestamp in call:** ~3:00

**What happened:**  
In 6 out of 11 calls, the agent said "test line. Goodbye." or "AI test line. Goodbye."
and ended the conversation while the patient had an active unresolved request. Examples:

- Scenario 2: Michael Torres was waiting for rescheduling confirmation
- Scenario 3: Linda Park was waiting for medication refill approval
- Scenario 7: Dorothy Simmons was told "Connecting to a representative. Please wait."
  immediately followed by "test line. Goodbye."

**Why it is a problem:**  
More than half of all calls ended with the patient's goal completely unmet. For a healthcare
voice agent, this means patients do not receive their prescriptions or appointment changes.
The premature termination pattern appears to be triggered when the agent cannot access
patient records, which suggests a fallback behavior that abandons patients rather than
helping them.

---

## BUG-006 — Agent cannot process medication refill requests

**Severity:** Medium  
**Scenario:** 3 (medication_refill), 10 (controlled_substance_refill)  
**Transcript:** transcript_3_medication_refill_20260623_194138.txt  
**Timestamp in call:** ~1:30

**What happened:**  
In both medication-related scenarios, the agent collected the patient's name and date of
birth, then immediately responded with "I can't proceed further right now, but I can make
sure our clinic support team follows up with you." Neither Linda Park's lisinopril refill
nor Maria Garcia's Adderall refill were addressed. Both calls ended with the agent
disconnecting before any refill action was taken.

**Why it is a problem:**  
Prescription refills are one of the core use cases listed for PGAI's voice agent. The agent
is completely unable to handle this workflow, routing all refill requests to a support team
that never materializes. Patients dependent on daily medication who call for a refill will
receive no help and no callback.

---

## BUG-007 — Agent promises live transfer that never occurs

**Severity:** Medium  
**Scenario:** 2, 3, 4, 7 (multiple)  
**Transcript:** transcript_7_elderly_patient_20260623_233305.txt  
**Timestamp in call:** ~1:45

**What happened:**  
In 4 calls, the agent said "Connecting you to a representative. Please wait." but then
immediately disconnected. In scenario 7, an elderly patient with knee pain was told
"Please wait. Please wait." twice in a row before the call ended.

**Why it is a problem:**  
The agent is making a promise it cannot keep. Patients who stay on the line expecting a
transfer are instead disconnected. This false promise pattern is worse than simply saying
the agent cannot help, because it causes the patient to wait before ultimately receiving
no assistance.

---

## BUG-008 — Agent cannot locate patient records for routine requests

**Severity:** Medium  
**Scenario:** 1, 2, 3, 4 (multiple)  
**Transcript:** transcript_2_reschedule_20260623_194138.txt  
**Timestamp in call:** ~2:00

**What happened:**  
After collecting name, date of birth, and phone number, the agent repeatedly responded with
"Something's not right with the system, and I can't access your record." This occurred for
routine requests including appointment rescheduling, appointment cancellation, and medication
refills. In scenario 2, Michael Torres provided all requested information three times before
the agent admitted it could not access his record.

**Why it is a problem:**  
If the agent cannot reliably access patient records after identity verification, it cannot
fulfill any patient request. The system appears to be in a state where the lookup
functionality is broken for most callers, making the agent unable to serve its primary
purpose.

---

## Observations

- Office hours information was accurate: Mon/Tue/Thu 9am-4pm, Wed 12pm-7pm, Fri 9am-12pm.
- Blue Cross Blue Shield PPO was correctly confirmed as accepted in scenarios 5 and 6.
- Scenario 9 (reluctant caller) was handled gracefully -- agent maintained patient
  confidentiality and appropriately redirected the caller to a primary care provider.
- Scenario 6 (weekend request) correctly informed the patient the practice is closed on
  weekends and offered Wednesday evening alternatives.
- Scenario 8 (barge-in impatient) showed reasonable patience with a scattered caller and
  provided helpful parking information unprompted.

## Recommendations

1. Fix demo patient profile isolation -- TEST profile must not appear in production calls.
2. Fix patient record lookup -- the agent cannot serve patients if it cannot access records.
3. Add real transfer capability or remove transfer language from the fallback script entirely.
4. Implement reliable short-term memory for name and information already collected in session.
5. Fix name spelling capture -- agent must echo back exactly what the patient spelled.
6. Build proper medication refill workflow instead of immediately escalating to support team.
