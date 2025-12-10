"""
Smart Triage System - Suggests appropriate doctors based on patient symptoms/reason
"""
import re
from models import Doctor

# Keyword to specialization mapping
SYMPTOM_SPECIALIZATION_MAP = {
    # Cardiology
    'heart': 'Cardiology',
    'chest pain': 'Cardiology',
    'chest': 'Cardiology',
    'palpitation': 'Cardiology',
    'blood pressure': 'Cardiology',
    'hypertension': 'Cardiology',
    'cardiac': 'Cardiology',
    
    # Dermatology
    'skin': 'Dermatology',
    'rash': 'Dermatology',
    'acne': 'Dermatology',
    'eczema': 'Dermatology',
    'allergy': 'Dermatology',
    'itching': 'Dermatology',
    'hives': 'Dermatology',
    
    # Orthopedics
    'bone': 'Orthopedics',
    'fracture': 'Orthopedics',
    'joint': 'Orthopedics',
    'back pain': 'Orthopedics',
    'spine': 'Orthopedics',
    'knee': 'Orthopedics',
    'shoulder': 'Orthopedics',
    'arthritis': 'Orthopedics',
    
    # Neurology
    'headache': 'Neurology',
    'migraine': 'Neurology',
    'seizure': 'Neurology',
    'numbness': 'Neurology',
    'dizziness': 'Neurology',
    'nerve': 'Neurology',
    'brain': 'Neurology',
    
    # Gastroenterology
    'stomach': 'Gastroenterology',
    'digestion': 'Gastroenterology',
    'nausea': 'Gastroenterology',
    'vomiting': 'Gastroenterology',
    'diarrhea': 'Gastroenterology',
    'constipation': 'Gastroenterology',
    'liver': 'Gastroenterology',
    'abdomen': 'Gastroenterology',
    
    # Pulmonology
    'breathing': 'Pulmonology',
    'cough': 'Pulmonology',
    'asthma': 'Pulmonology',
    'lung': 'Pulmonology',
    'respiratory': 'Pulmonology',
    'shortness of breath': 'Pulmonology',
    
    # ENT
    'ear': 'ENT',
    'nose': 'ENT',
    'throat': 'ENT',
    'sinus': 'ENT',
    'hearing': 'ENT',
    'tonsil': 'ENT',
    
    # Ophthalmology
    'eye': 'Ophthalmology',
    'vision': 'Ophthalmology',
    'blurry': 'Ophthalmology',
    'glasses': 'Ophthalmology',
    
    # Pediatrics
    'child': 'Pediatrics',
    'baby': 'Pediatrics',
    'infant': 'Pediatrics',
    'kid': 'Pediatrics',
    
    # Gynecology
    'pregnancy': 'Gynecology',
    'menstrual': 'Gynecology',
    'period': 'Gynecology',
    'pelvic': 'Gynecology',
    
    # Urology
    'urinary': 'Urology',
    'bladder': 'Urology',
    'kidney': 'Urology',
    'prostate': 'Urology',
    
    # General/Internal Medicine (fallback)
    'fever': 'General Medicine',
    'cold': 'General Medicine',
    'flu': 'General Medicine',
    'fatigue': 'General Medicine',
    'weakness': 'General Medicine',
    'checkup': 'General Medicine',
    'general': 'General Medicine',
}


def analyze_symptoms(reason_text):
    """
    Analyze patient's reason for visit and extract likely specializations needed.
    Returns a list of matching specializations ranked by relevance.
    """
    if not reason_text:
        return ['General Medicine']
    
    reason_lower = reason_text.lower()
    matches = {}
    
    for keyword, specialization in SYMPTOM_SPECIALIZATION_MAP.items():
        if keyword in reason_lower:
            # Count matches and prioritize longer keyword matches
            weight = len(keyword)
            if specialization in matches:
                matches[specialization] += weight
            else:
                matches[specialization] = weight
    
    if not matches:
        return ['General Medicine']
    
    # Sort by weight (higher = more relevant)
    sorted_specs = sorted(matches.items(), key=lambda x: x[1], reverse=True)
    return [spec for spec, weight in sorted_specs]


def suggest_doctors(reason_text, limit=5):
    """
    Suggest appropriate doctors based on patient's reason for visit.
    Returns list of Doctor objects sorted by relevance.
    """
    specializations = analyze_symptoms(reason_text)
    
    suggested_doctors = []
    seen_ids = set()
    
    # First, find doctors matching the primary specializations
    for spec in specializations:
        doctors = Doctor.query.filter(
            Doctor.specialization.ilike(f'%{spec}%')
        ).all()
        
        for doc in doctors:
            if doc.id not in seen_ids:
                suggested_doctors.append({
                    'doctor': doc,
                    'match_reason': f'Specializes in {doc.specialization}',
                    'relevance': 'high' if spec == specializations[0] else 'medium'
                })
                seen_ids.add(doc.id)
    
    # If no specialists found, suggest general medicine doctors
    if not suggested_doctors:
        general_docs = Doctor.query.filter(
            Doctor.specialization.ilike('%general%')
        ).all()
        
        for doc in general_docs:
            if doc.id not in seen_ids:
                suggested_doctors.append({
                    'doctor': doc,
                    'match_reason': 'General practitioner',
                    'relevance': 'low'
                })
                seen_ids.add(doc.id)
    
    # If still no doctors, return all available doctors
    if not suggested_doctors:
        all_doctors = Doctor.query.limit(limit).all()
        for doc in all_doctors:
            suggested_doctors.append({
                'doctor': doc,
                'match_reason': 'Available doctor',
                'relevance': 'low'
            })
    
    return suggested_doctors[:limit]


def get_specialization_summary(reason_text):
    """
    Get a human-readable summary of detected conditions.
    """
    specializations = analyze_symptoms(reason_text)
    if specializations == ['General Medicine'] and reason_text:
        return "General consultation recommended"
    
    if len(specializations) == 1:
        return f"Suggested specialty: {specializations[0]}"
    else:
        return f"Suggested specialties: {', '.join(specializations[:3])}"
