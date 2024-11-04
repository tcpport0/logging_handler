import os
import sys
from pathlib import Path

# Add src directory to Python path
src_path = str(Path(__file__).parent.parent / 'src')
sys.path.insert(0, src_path)

from dotenv import load_dotenv
load_dotenv()

import pytest
from datetime import datetime, timezone

@pytest.fixture
def test_context():
    return {
        'test_id': f"test-{datetime.now(timezone.utc).timestamp()}",
        'test_run': 'automated'
    }