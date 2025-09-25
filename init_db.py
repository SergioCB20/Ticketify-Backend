#!/usr/bin/env python3
"""
Script to initialize the database with Alembic migrations
"""
import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False

def main():
    """Main function to initialize the database"""
    print("🚀 Initializing Ticketify Database...")
    
    # Change to project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    print(f"Working directory: {project_root}")
    
    # Create initial migration
    if not run_command(
        "alembic revision --autogenerate -m 'Initial migration with all models'",
        "Creating initial migration"
    ):
        sys.exit(1)
    
    # Apply migration
    if not run_command(
        "alembic upgrade head",
        "Applying migrations to database"
    ):
        sys.exit(1)
    
    print("\n🎉 Database initialization completed successfully!")
    print("\nNext steps:")
    print("1. Make sure PostgreSQL is running")
    print("2. Update .env file with correct database credentials")
    print("3. Run: python -m uvicorn app.main:app --reload")

if __name__ == "__main__":
    main()
