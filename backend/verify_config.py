import sys
import os

# Add the current directory to sys.path to import from sibling files
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config import JWT_SECRET as CONFIG_SECRET
    from auth.auth_dependencies import JWT_SECRET as DEP_SECRET
    from auth.auth_utils import JWT_SECRET as UTILS_SECRET

    print(f"Config Secret: {CONFIG_SECRET[:4]}...")
    print(f"Dependencies Secret: {DEP_SECRET[:4]}...")
    print(f"Utils Secret: {UTILS_SECRET[:4]}...")

    if CONFIG_SECRET == DEP_SECRET == UTILS_SECRET:
        print("\n✅ SUCCESS: JWT_SECRET is consistent across all modules!")
    else:
        print("\n❌ FAILURE: JWT_SECRET mismatch detected!")
        sys.exit(1)

except ImportError as e:
    print(f"\n❌ Error importing modules: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
    sys.exit(1)
