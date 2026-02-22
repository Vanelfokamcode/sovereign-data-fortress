# dagster_fortress/resources/dbt_resource.py
"""
dbt CLI resource for Dagster
"""

from pathlib import Path
from dagster_dbt import DbtCliResource

# Paths
DBT_PROJECT_DIR = Path(__file__).parent.parent.parent / "dbt_fortress"
DBT_PROFILES_DIR = Path.home() / ".dbt"  # profiles.yml is here

# Verify paths exist
if not DBT_PROJECT_DIR.exists():
    raise FileNotFoundError(f"dbt project not found: {DBT_PROJECT_DIR}")

if not DBT_PROFILES_DIR.exists():
    raise FileNotFoundError(f"dbt profiles dir not found: {DBT_PROFILES_DIR}")

if not (DBT_PROFILES_DIR / "profiles.yml").exists():
    raise FileNotFoundError(
        f"profiles.yml not found in {DBT_PROFILES_DIR}. "
        "Run 'dbt debug' to create it."
    )

# Create dbt resource
dbt_resource = DbtCliResource(
    project_dir=DBT_PROJECT_DIR,
    profiles_dir=DBT_PROFILES_DIR,  # This is the key fix
    target="dev"
)
