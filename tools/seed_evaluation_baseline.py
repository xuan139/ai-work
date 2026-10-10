import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db import get_user_by_username, init_db
from app.evaluation_baseline import seed_enterprise_evaluation_baseline


def main() -> None:
    init_db()
    admin = get_user_by_username("admin")
    if not admin or admin.get("role") != "admin":
        raise SystemExit("Admin account is unavailable")
    print(seed_enterprise_evaluation_baseline(admin))


if __name__ == "__main__":
    main()
