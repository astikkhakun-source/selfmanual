import os
import pytest
from src.services.pdf_export import generate_pdf_report
from src.services.llm_report import get_fallback_mock_full_report


def test_pdf_rendering():
    session_id = "test-session-12345"
    mock_data = get_fallback_mock_full_report({})
    
    pdf_path = generate_pdf_report(session_id, mock_data)
    
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 1000  # PDF should be larger than 1KB
    
    # Cleanup test output
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
