import os
import sys

# Add project root to sys.path
sys.path.insert(0, r"c:\Sher_AI_Studio\projects\selfmanual")

from src.domain.scoring.full_engine import calculate_full_profile
from src.services.llm_report import get_fallback_mock_full_report, get_fallback_mock_core_report
from src.services.pdf_export import generate_pdf_report, generate_core_pdf_report

def main():
    print("=== Testing PDF Generation with Visual Components ===")
    
    # 1. Mock answers map
    mock_answers = {f"q{i}": (i % 7) + 1 for i in range(1, 161)}
    
    # 2. Calculate full profile
    profile = calculate_full_profile(mock_answers)
    print(f"Calculated profile indicators count: {len(profile.get('profile_indicators', []))}")
    print(f"Calculated system cycle steps count: {len(profile.get('system_cycle', {}).get('steps', []))}")
    
    # 3. Generate mock FULL report payload
    full_report_payload = get_fallback_mock_full_report(profile)
    
    session_id = "test_visual_session_99"
    
    # 4. Generate FULL PDF report
    full_pdf_path = generate_pdf_report(session_id, full_report_payload)
    print(f"FULL PDF generated successfully at: {full_pdf_path}")
    assert os.path.exists(full_pdf_path), "FULL PDF file does not exist!"
    print(f"FULL PDF size: {os.path.getsize(full_pdf_path)} bytes")

    # 5. Generate CORE PDF report
    core_report_payload = get_fallback_mock_core_report()
    core_pdf_path = generate_core_pdf_report(session_id, core_report_payload)
    print(f"CORE PDF generated successfully at: {core_pdf_path}")
    assert os.path.exists(core_pdf_path), "CORE PDF file does not exist!"
    print(f"CORE PDF size: {os.path.getsize(core_pdf_path)} bytes")

    print("\n[SUCCESS] Visual PDF test completed successfully!")

if __name__ == "__main__":
    main()

