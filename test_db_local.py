from src.database import Database
import os

# Ensure no Turso env vars are set
if "TURSO_DATABASE_URL" in os.environ:
    del os.environ["TURSO_DATABASE_URL"]
if "TURSO_AUTH_TOKEN" in os.environ:
    del os.environ["TURSO_AUTH_TOKEN"]

print("Testing Local Database Fallback...")
try:
    db = Database("test_local.db")
    print("✅ Database initialized")
    
    job_data = {
        "url": "https://example.com/job1",
        "title": "Test Job",
        "company": "Test Corp",
        "poster": "John Doe",
        "description": "Test Description",
        "full_description": "Full Test Description"
    }
    
    job_id = db.save_job(job_data)
    print(f"✅ Job saved with ID: {job_id}")
    
    job = db.get_job(job_id)
    if job and job['title'] == "Test Job":
        print("✅ Job retrieved successfully")
    else:
        print("❌ Job retrieval failed")
        
    # Clean up
    os.remove("test_local.db")
    print("✅ Test cleanup complete")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
