import json
from analyzer import analyze_report
healthy_report = """
Patient Name: Sarah

CBC Report

Hemoglobin: 13.8 g/dL
WBC: 6800 cells/uL
Platelets: 270000 cells/uL
Vitamin D: 38 ng/mL
HbA1c: 5.2%
"""
iron_deficiency = """
Patient Name: Emma

Hemoglobin: 9.5 g/dL
WBC: 7000 cells/uL
Platelets: 280000 cells/uL
Vitamin D: 30 ng/mL
HbA1c: 5.3%
"""
diabetes_report = """
Patient Name: David

Hemoglobin: 14.1 g/dL
HbA1c: 7.1%
Vitamin D: 32 ng/mL
WBC: 7100 cells/uL
Platelets: 255000 cells/uL
"""
vitamin_report = """
Patient Name: Lisa

Vitamin D: 10 ng/mL
Vitamin B12: 140 pg/mL
Hemoglobin: 11.2 g/dL
"""
incomplete_report = """
Glucose: 104 mg/dL
"""
reports = {
    "Healthy": healthy_report,
    "Iron Deficiency": iron_deficiency,
    "Diabetes": diabetes_report,
    "Vitamin Deficiency": vitamin_report,
    "Incomplete": incomplete_report,
}
for name, report in reports.items():
    print("=" * 60)
    print(name)
    print("=" * 60)

    result = analyze_report(report)

    print(json.dumps(result, indent=4))

    print("\n\n")
