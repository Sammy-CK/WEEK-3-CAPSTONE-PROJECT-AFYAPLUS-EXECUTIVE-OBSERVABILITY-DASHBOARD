# 15 clinical verification questions
# 5 per channel (USSD, Mobile App, Web Portal)
# 5 per feature (triage_advisor, epidemic_alerts, clinical_summaries)

EVAL_DATASET = [
    # USSD - triage_advisor
    {
        "id": "q1",
        "channel": "USSD",
        "feature": "triage_advisor",
        "question": "My child has fever and is very sleepy. When should I escalate?",
        "reference": (
            "Pediatric fever requires immediate escalation if the child is under three months old, "
            "temperature exceeds 39 degrees Celsius, the child is lethargic, or breathing is labored."
        ),
    },
    # USSD - epidemic_alerts
    {
        "id": "q2",
        "channel": "USSD",
        "feature": "epidemic_alerts",
        "question": "Are there cholera alerts in Nairobi this week?",
        "reference": (
            "Check the AfyaPlus epidemic bulletin for Nairobi County. If active cholera alerts exist, "
            "advise safe water use, hand hygiene, and referral to the nearest health facility for dehydration."
        ),
    },
    # USSD - clinical_summaries
    {
        "id": "q3",
        "channel": "USSD",
        "feature": "clinical_summaries",
        "question": "Summarize outpatient lab result turnaround time.",
        "reference": (
            "Standard outpatient laboratory results are typically available within 24 to 48 hours. "
            "Urgent tests may be expedited within 6 hours at designated hub laboratories."
        ),
    },
    # USSD - triage_advisor
    {
        "id": "q4",
        "channel": "USSD",
        "feature": "triage_advisor",
        "question": "Patient has diarrhea for 3 days. Refer now or wait?",
        "reference": (
            "Monitor for up to 48 hours in mild adult cases. Refer immediately if dehydration, "
            "blood in stool, high fever, or symptoms persist beyond 48 hours."
        ),
    },
    # USSD - epidemic_alerts
    {
        "id": "q5",
        "channel": "USSD",
        "feature": "epidemic_alerts",
        "question": "What symptoms trigger a malaria outbreak notification?",
        "reference": (
            "Clustered fever cases with headache, chills, and fatigue in endemic zones should trigger "
            "outbreak notification when case counts exceed the local baseline threshold."
        ),
    },
    # Mobile App - triage_advisor
    {
        "id": "q6",
        "channel": "Mobile App",
        "feature": "triage_advisor",
        "question": "Pregnant patient reports severe headache and swollen feet. What is the urgency?",
        "reference": (
            "Severe headache with swelling during pregnancy may indicate preeclampsia risk. "
            "Route to urgent maternal care or emergency department for immediate assessment."
        ),
    },
    # Mobile App - epidemic_alerts
    {
        "id": "q7",
        "channel": "Mobile App",
        "feature": "epidemic_alerts",
        "question": "Has dengue activity increased in Mombasa county?",
        "reference": (
            "Review the AfyaPlus regional surveillance dashboard. Rising dengue activity requires "
            "vector control advisories and fever monitoring in primary care facilities."
        ),
    },
    # Mobile App - clinical_summaries
    {
        "id": "q8",
        "channel": "Mobile App",
        "feature": "clinical_summaries",
        "question": "What documents are needed for outpatient registration?",
        "reference": (
            "Registration requires a valid national ID or passport, verified patient health record number, "
            "and Ministry of Health referral code when applicable."
        ),
    },
    # Mobile App - triage_advisor
    {
        "id": "q9",
        "channel": "Mobile App",
        "feature": "triage_advisor",
        "question": "Adult with chest pain and shortness of breath. Triage level?",
        "reference": (
            "Chest pain with shortness of breath is a critical emergency. "
            "Immediate escalation to emergency department is required."
        ),
    },
    # Mobile App - clinical_summaries
    {
        "id": "q10",
        "channel": "Mobile App",
        "feature": "clinical_summaries",
        "question": "How long are telemedicine intake sessions kept active?",
        "reference": (
            "Telemedicine intake sessions remain active for 30 minutes pending clinician review. "
            "Incomplete sessions auto-close and prompt the patient to rebook."
        ),
    },
    # Web Portal - triage_advisor
    {
        "id": "q11",
        "channel": "Web Portal",
        "feature": "triage_advisor",
        "question": "Elderly patient fell and cannot bear weight on leg. Next step?",
        "reference": (
            "Suspected fracture after a fall requires urgent imaging referral. "
            "Escalate to emergency or orthopaedic assessment within 4 hours."
        ),
    },
    # Web Portal - epidemic_alerts
    {
        "id": "q12",
        "channel": "Web Portal",
        "feature": "epidemic_alerts",
        "question": "What is the protocol when measles cases exceed baseline in a district?",
        "reference": (
            "Activate district measles response: case isolation, contact tracing, "
            "immunization catch-up campaigns, and daily situational reports to county health office."
        ),
    },
    # Web Portal - clinical_summaries
    {
        "id": "q13",
        "channel": "Web Portal",
        "feature": "clinical_summaries",
        "question": "Explain insurance pre-authorization steps for emergency claims.",
        "reference": (
            "Emergency claims above KES 50,000 require supervisor approval within 24 hours. "
            "Submit member ID, clinical summary, and itemized cost estimate through the claims portal."
        ),
    },
    # Web Portal - epidemic_alerts
    {
        "id": "q14",
        "channel": "Web Portal",
        "feature": "epidemic_alerts",
        "question": "How are influenza surges communicated to clinic managers?",
        "reference": (
            "Influenza surge alerts are pushed via the AfyaPlus manager dashboard and SMS broadcast. "
            "Clinics should increase triage staffing and stock antipyretics during active surge windows."
        ),
    },
    # Web Portal - clinical_summaries
    {
        "id": "q15",
        "channel": "Web Portal",
        "feature": "clinical_summaries",
        "question": "What is the staff travel reimbursement timeline?",
        "reference": (
            "Approved staff travel reimbursements are processed within 30 days of claim submission "
            "with valid receipts and supervisor sign-off."
        ),
    },
]

# Clinical safety thresholds for quality gate
QUALITY_GATES = {
    "bleu_4_min": 0.10,
    "rouge_l_min": 0.25,
    "token_f1_min": 0.30,
    "correctness_min": 3.0,
    "groundedness_min": 3.0,
    "relevance_min": 3.0,
    "helpfulness_min": 3.0,
    "judge_overall_min": 3.0,
}
