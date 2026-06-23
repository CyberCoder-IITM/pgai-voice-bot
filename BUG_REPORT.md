# Bug Report — Pretty Good AI Agent Evaluation

**Tester:** Saleeq Adnan Syed  
**Test Date:** June 23, 2026  
**Phone Number Used:** +14244281474  
**Total Calls:** 11 calls across 10 scenarios

---

## Summary

| Severity | Count |
| -------- | ----- |
| Critical | 2     |
| High     | 4     |
| Medium   | 3     |

---

## BUG-001 — Demo patient profile leaks into live calls

**Severity:** Critical  
**Scenario:** 1 (new_appointment), 2 (reschedule), 3 (medication_refill), 4 (cancel_appointment)  
**Transcript:** transcript_1_new_appointment_20260623_163456.txt  
**Timestamp in call:** ~0:45

**What happened:**  
The agent repeatedly assigns the demo patient's data (Name: "Sarah", DOB: July 4, 2000) to
real callers mid-conversation. In scenario 1, the agent said "your date of birth is July 4,
2000 for demo purposes" unprompted to Sarah Johnson who had not provided her DOB. In scenarios
2, 3, and 4, the agent opened calls with "Am I speaking with Sarah?" regardless of who was
calling.

**Why it is a problem:**  
The demo patient profile from pgai.us/athena (Test Patient, DOB July 4 2000) is bleeding
into production call sessions. Every caller is being partially identified as the demo patient.
This is a data isolation failure that would be a serious HIPAA concern in a real clinical
deployment. Patients are being assigned wrong identities and wrong dates of birth.

---

## BUG-002 — Random Spanish language injection mid-conversation

**Severity:** Critical  
**Scenario:** 1, 3, 4, 5 (multiple calls)  
**Transcript:** transcript_1_new_appointment_20260623_163456.txt  
**Timestamp in call:** ~0:30

**What happened:**  
The agent randomly inserts a Spanish-language prompt mid-conversation: "para español, oprima
el 2" (press 2 for Spanish). This occurred in 4 out of 11 calls at unpredictable points,
sometimes as the agent's very first response after the patient stated their reason for calling.

**Why it is a problem:**  
The bilingual IVR prompt is firing at random instead of only at call start. A patient calling
to schedule an appointment or request a refill suddenly hears Spanish instructions with no
context. This breaks conversational flow completely and would confuse any real patient. The
trigger condition for this prompt appears to be broken.

---

## BUG-003 — Agent hallucinates "deployment" instead of "appointment"

**Severity:** High  
**Scenario:** 1 (new_appointment)  
**Transcript:** transcript_1_new_appointment_20260623_163456.txt  
**Timestamp in call:** ~1:10

**What happened:**  
When Sarah Johnson asked to schedule a routine checkup, the agent responded: "To schedule a
deployment, I'll meet a demo patient profile. If you prefer not to create one now, you can
scan the QR code at the booth later to set up your profile."

**Why it is a problem:**  
The agent used the word "deployment" instead of "appointment" and referenced a "QR code at
the booth" -- language from a physical event or trade show, not a medical practice. This
suggests the agent's language model is hallucinating non-clinical context. A real patient
would be deeply confused and lose trust in the system immediately.

---

## BUG-004 — Cross-patient data contamination between sessions

**Severity:** High  
**Scenario:** 3 (medication_refill)  
**Transcript:** transcript_3_medication_refill_20260623_163456.txt  
**Timestamp in call:** ~2:30

**What happened:**  
During Linda Park's call to request a lisinopril refill, the agent confirmed an appointment
for a completely different patient: "You're all set for Wednesday, July 1st at 10 a.m. with
Dr. Kelly Noble. Please bring your photo ID, insurance card..." This appointment belonged to
Michael Torres from the previous call (scenario 2).

**Why it is a problem:**  
Patient session data from a previous call was carried over into a new patient's session. Linda
Park received appointment confirmation for Michael Torres's visit. In a real healthcare
setting this would be a critical HIPAA violation -- one patient receiving another patient's
appointment details. Session state is not being properly isolated between calls.

---

## BUG-005 — Agent invents non-existent doctor names

**Severity:** High  
**Scenario:** 1 (new_appointment), 2 (reschedule)  
**Transcript:** transcript_1_new_appointment_20260623_143408.txt  
**Timestamp in call:** ~2:00

**What happened:**  
When asked about available doctors, the agent offered appointments with doctors whose names
do not exist at the practice: "Dr. Sigmil Lukoski", "Dr. Zygmuda Lukoski", and
"Dr. Zbigniew-Lukoski" (the name changed spelling three times in the same call). The patient
had asked specifically about Dr. Williams.

**Why it is a problem:**  
The agent is hallucinating doctor names rather than pulling from a real provider list. A
patient who books with "Dr. Zbigniew-Lukoski" will arrive at the clinic to find no such
doctor exists. This is a direct patient safety concern in addition to a trust issue.

---

## BUG-006 — Agent prematurely ends calls with unresolved patient needs

**Severity:** High  
**Scenario:** 2, 3, 4, 8 (multiple)  
**Transcript:** transcript_2_reschedule_20260623_163456.txt  
**Timestamp in call:** ~3:00

**What happened:**  
In multiple calls, the agent said "Have a great day. Goodbye." or "test line. Goodbye." and
terminated the conversation while the patient still had an active unresolved request. In
scenario 2, Michael Torres was mid-sentence confirming an appointment time when the agent
ended the call. In scenario 3, Linda Park had not received her refill confirmation before
the agent disconnected.

**Why it is a problem:**  
The agent abandons patients before their goals are met. For a healthcare voice agent, this
means patients do not get their prescriptions, appointments, or information. They must call
back and repeat the entire process, creating frustration and potential health risk for
prescription-dependent patients.

---

## BUG-007 — Agent contradicts itself within a single call

**Severity:** Medium  
**Scenario:** 10 (controlled_substance_refill)  
**Transcript:** transcript_10_controlled_substance_refill_20260623_163456.txt  
**Timestamp in call:** ~3:45 and ~4:30

**What happened:**  
In scenario 10, the agent said at ~3:45: "You've reached Pivot Point Orthopedics. We're not
affiliated with Dr. Patel's office." Then at ~4:30 in the same call: "Since we are connected
to Dr. Patel's office, they're the best ones to help with your refill."

**Why it is a problem:**  
The agent directly contradicted itself within the same conversation. This destroys patient
trust and suggests the agent does not maintain consistent state about its own identity and
affiliations during a session.

---

## BUG-008 — Agent fails to transfer but claims it will

**Severity:** Medium  
**Scenario:** 2, 3, 7 (multiple)  
**Transcript:** transcript_7_elderly_patient_20260623_163456.txt  
**Timestamp in call:** ~4:00

**What happened:**  
The agent repeatedly told patients "Connecting you to a representative. Please wait." or
"Please hold while I get this started." but then immediately said "Goodbye" or "Hello, you've
reached the Pretty Good AI test line. Goodbye." No actual transfer occurred.

**Why it is a problem:**  
The agent promises a transfer that never happens. Patients (particularly in scenario 7,
an elderly patient with knee pain) were left waiting for a transfer that resulted in the
call ending. This pattern of false promises followed by disconnection is the most
frustrating patient experience possible.

---

## BUG-009 — Agent misidentifies patient name mid-conversation

**Severity:** Medium  
**Scenario:** 7 (elderly_patient)  
**Transcript:** transcript_7_elderly_patient_20260623_163456.txt  
**Timestamp in call:** ~3:20

**What happened:**  
Dorothy Simmons confirmed her name clearly at the start of the call. Later in the same
conversation the agent addressed her as "Dorsey" -- a hallucinated variation of her name.

**Why it is a problem:**  
The agent failed to retain the correct patient name from earlier in the same session.
Calling a patient by the wrong name after they have already confirmed it erodes trust and
suggests the agent does not maintain reliable short-term conversational memory.

---

## Observations

- The agent successfully handled basic scheduling flow in scenario 1 (143408 transcript)
  completing a full appointment booking with reasonable accuracy.
- Office hours information was accurate when provided (Monday/Tuesday/Thursday 9am-4pm,
  Wednesday 12pm-7pm, Friday 9am-12pm).
- Blue Cross Blue Shield PPO confirmation was handled correctly in scenario 6.
- The agent consistently asked for patient name and date of birth to verify identity,
  which is appropriate protocol.

## Recommendations

1. Fix demo patient profile isolation -- sessions must not carry default demo data.
2. Move bilingual IVR prompt to call start only, not mid-conversation injection.
3. Replace hallucinated doctor names with a real provider database lookup.
4. Implement session state isolation between concurrent calls.
5. Add a proper transfer mechanism or remove false transfer promises entirely.
6. Add session memory validation to prevent name and DOB mutations mid-call.
