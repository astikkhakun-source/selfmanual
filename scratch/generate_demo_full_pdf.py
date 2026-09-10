import os
import sys

# Ensure root selfmanual directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.services.pdf_export import generate_pdf_report
from src.services.llm_report import get_fallback_mock_full_report

sample_data = get_fallback_mock_full_report({})

pdf_path = generate_pdf_report("demo_full_session_175_q", sample_data)
print(f"SUCCESS: PDF generated at {pdf_path}")

