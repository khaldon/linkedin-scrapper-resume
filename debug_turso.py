import os
import libsql_experimental as libsql
from dotenv import load_dotenv

# Load env vars from .env if present
load_dotenv()

def test_turso_connection():
    url = os.getenv("TURSO_DATABASE_URL")
    token = os.getenv("TURSO_AUTH_TOKEN")

    print(f"1. Checking Environment Variables...")
    print(f"   TURSO_DATABASE_URL: {'✅ Found' if url else '❌ Missing'}")
    print(f"   TURSO_AUTH_TOKEN:   {'✅ Found' if token else '❌ Missing'}")

    if not url or not token:
        print("\n⚠️  Missing credentials! Cannot test Turso connection.")
        print("   Please ensure TURSO_DATABASE_URL and TURSO_AUTH_TOKEN are set.")
        return

    print(f"\n2. Attempting to connect to: {url}")
    try:
        conn = libsql.connect(url, auth_token=token)
        print("   ✅ Connection successful!")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return

    print("\n3. Testing Write Operation...")
    try:
        cursor = conn.cursor()
        # Create a temporary test table
        cursor.execute("CREATE TABLE IF NOT EXISTS _debug_test (id INTEGER PRIMARY KEY, message TEXT)")
        cursor.execute("INSERT INTO _debug_test (message) VALUES ('Hello from Debug Script')")
        conn.commit()
        print("   ✅ Write successful!")
    except Exception as e:
        print(f"   ❌ Write failed: {e}")
        return

    print("\n4. Testing Read Operation...")
    try:
        cursor.execute("SELECT * FROM _debug_test LIMIT 1")
        row = cursor.fetchone()
        print(f"   ✅ Read successful! Retrieved: {row}")
    except Exception as e:
        print(f"   ❌ Read failed: {e}")
        return

    print("\n5. Cleaning up...")
    try:
        cursor.execute("DROP TABLE _debug_test")
        conn.commit()
        print("   ✅ Cleanup successful!")
    except Exception as e:
        print(f"   ⚠️ Cleanup failed (not critical): {e}")

    print("\n🎉 TURSO CONNECTION IS WORKING CORRECTLY!")

if __name__ == "__main__":
    test_turso_connection()
