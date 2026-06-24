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
| High     | 4     |
| Medium   | 3     |

---

## BUG-001 — Demo patient profile leaks into live calls

**Severity:** Critical  
**Scenario:** 1 (new_appointment), 2 (reschedule), 3 (medication_refill), 4 (cancel_appointment)  
**Transcript:** transcript_1_new_appointment_20260623_194138.txt  
**Timestamp in call:** ~0:45

**What happened:**  
The agent opens every call with "Am I speaking with TEST?" -- the name of the demo patient
profile from pgai.us/athena. In scenarios 2, 3, and 4, regardless of who was calling, the
agent identified the caller as the demo patient. The demo profile (Name: TEST, DOB: July 4, 2000) bleeds into every call session.

**Why it is a problem:**  
The demo patient profile is not being isolated from production call sessions. Every real
caller is being partially identified as the demo patient. This is a data isolation failure
that would be a serious HIPAA concern in a real clinical deployment. Patients are being
assigned wrong identities.

---

## BUG-002 — Random Spanish language injection mid-conversation

**Severity:** Critical  
**Scenario:** 1, 3, 4, 5 (multiple calls)  
**Transcript:** transcript_1_new_appointment_20260623_194138.txt  
**Timestamp in call:** ~0:05

**What happened:**  
The agent randomly inserts a Spanish-language prompt mid-conversation: "para español, oprima
el 2" (press 2 for Spanish). This occurred across multiple calls at unpredictable points,
sometimes as the very first substantive response after the patient stated their reason for
calling. In scenario 4, the agent said "Para español, oprima el 2" immediately after the
patient said "Hi, I'd like to speak with someone about an appointment."

**Why it is a problem:**  
The bilingual IVR prompt is firing randomly instead of only at call start. A patient calling
to cancel an appointment suddenly hears Spanish instructions with no context. This breaks
conversational flow and would deeply confuse any real patient.

---

## BUG-003 — Agent catastrophically halluccinates patient name spelling

**Severity:** High  
**Scenario:** 1 (new_appointment)  
**Transcript:** transcript_1_new_appointment_20260623_194138.txt  
**Timestamp in call:** ~1:30

**What happened:**  
When Sarah Johnson spelled her name as S-A-R-A-H J-O-H-N-S-O-N, the agent confirmed back:
"your first name is spelled S-A-R-H, and your last name is J-O-A-C-H-I-N-A-S-O-I-N."
The agent completely hallucinated a 14-character nonsense string instead of the 7-character
name the patient had just spelled letter by letter.

**Why it is a problem:**  
The agent is not reliably capturing or repeating back patient-provided information.
A patient verifying their identity before a medical appointment needs exact confirmation.
Getting a completely wrong name could result in wrong patient records being accessed
or modified.

---

## BUG-004 — Agent reveals patient phone number without patient providing it

**Severity:** High  
**Scenario:** 2 (reschedule), 4 (cancel_appointment)  
**Transcript:** transcript_4_cancel_appointment_20260623_194138.txt  
**Timestamp in call:** ~2:15

**What happened:**  
Robert Davis explicitly said "I'd rather not give out my phone number." The agent then
responded: "I have your phone number as 424-428-1474." The agent revealed the patient's
phone number without the patient providing it during this call.

**Why it is a problem:**  
The agent is leaking PII from the demo patient profile or a previous session to the current
caller without consent. A patient who declined to share their phone number had it revealed
back to them anyway. This is a privacy violation and would be a HIPAA concern in production.

---

## BUG-005 — Agent halluccinates clinic name mid-conversation

**Severity:** High  
**Scenario:** 5 (practice_info)  
**Transcript:** transcript_5_practice_info_20260623_192720.txt  
**Timestamp in call:** ~0:30

**What happened:**  
When providing office hours to a new potential patient, the agent said: "Pit at Flight
Orthopedics is open Monday through Friday." The clinic name is Pivot Point Orthopedics,
not "Pit at Flight Orthopedics."

**Why it is a problem:**  
The agent hallucinated a completely different clinic name while giving a new patient official
clinic information. A patient researching the practice would receive incorrect branding. This
suggests the agent's speech generation is not reliably anchored to correct clinical data.

---

## BUG-006 — Agent prematurely ends calls with unresolved patient needs

**Severity:** High  
**Scenario:** 2, 3, 4, 7 (multiple)  
**Transcript:** transcript_2_reschedule_20260623_194138.txt  
**Timestamp in call:** ~3:00

**What happened:**  
In multiple calls, the agent said "test line. Goodbye." or "AI test line. Goodbye." and
terminated the conversation while the patient still had an active unresolved request. In
scenario 2, Michael Torres was waiting for rescheduling confirmation when the agent ended
the call. In scenario 3, Linda Park had not received her refill confirmation before
the agent disconnected. In scenario 7, an elderly patient was told "Connecting you to a
representative. Please wait." immediately followed by "test line. Goodbye."

**Why it is a problem:**  
The agent abandons patients before their goals are met. For a healthcare voice agent, this
means patients do not get their prescriptions, appointments, or information. The pattern of
false transfer promises followed by immediate disconnection is the most frustrating
patient experience possible.

---

## BUG-007 — Agent garbles its own canned responses

**Severity:** Medium  
**Scenario:** 8 (barge_in_impatient)  
**Transcript:** transcript_8_barge_in_impatient_20260623_224028.txt  
**Timestamp in call:** ~2:30

**What happened:**  
The agent responded: "I can't foresee further right now, but I can make sure our clinic
support team follows up with you." The correct phrase should be "I can't proceed further."
In the same call, the agent also said "I have your day of birth" instead of "date of birth."

**Why it is a problem:**  
The agent is corrupting its own scripted responses. These errors undermine the professional
tone expected of a healthcare voice agent and suggest the language model is paraphrasing
fixed phrases instead of using them verbatim.

---

## BUG-008 — Agent self-confirms patient identity without patient agreeing

**Severity:** Medium  
**Scenario:** 4 (cancel_appointment)  
**Transcript:** transcript_4_cancel_appointment_20260623_194138.txt  
**Timestamp in call:** ~0:20

**What happened:**  
The agent asked and immediately answered its own question: "Am I speaking with test? Yes."
No patient confirmation was given. The agent confirmed a false identity on behalf of
the patient without waiting for a response.

**Why it is a problem:**  
Patient identity verification must come from the patient, not be assumed or self-generated
by the system. The agent is fabricating consent. In a real clinic this could allow the
wrong person to access another patient's medical records.

---

## BUG-009 — Agent fails to transfer despite promising it will

**Severity:** Medium  
**Scenario:** 2, 3, 7 (multiple)  
**Transcript:** transcript_7_elderly_patient_20260623_233305.txt  
**Timestamp in call:** ~1:45

**What happened:**  
The agent repeatedly told patients "Connecting you to a representative. Please wait." but
then immediately said "test line. Goodbye." No actual transfer occurred. This happened in
scenarios 2, 3, and 7. In scenario 7, an elderly patient with knee pain was told twice
"Please wait" before being disconnected.

**Why it is a problem:**  
The agent promises transfers that never happen. Patients are left waiting for help that
never arrives, then the call ends. This is the most trust-destroying failure pattern in
the system.

---

## Observations

- Office hours information was accurate when provided: Monday/Tuesday/Thursday 9am-4pm,
  Wednesday 12pm-7pm, Friday 9am-12pm.
- Blue Cross Blue Shield PPO was correctly confirmed as accepted in scenario 5 and 6.
- The agent consistently requested name and date of birth for identity verification,
  which is appropriate protocol.
- Scenario 8 (barge-in impatient) showed the agent could handle a scattered caller
  reasonably well, eventually providing useful information about parking and callback timing.

## Recommendations

1. Fix demo patient profile isolation -- sessions must not carry the TEST profile into calls.
2. Move bilingual IVR prompt to call start only, triggered once, not randomly mid-session.
3. Implement reliable session state isolation between concurrent calls to prevent PII leakage.
4. Add a real transfer mechanism or remove transfer promises entirely from the script.
5. Fix name capture -- agent must repeat back exactly what the patient spelled, not hallucinate.
6. Anchor clinic name and agent identity to a verified data source, not language model generation.
