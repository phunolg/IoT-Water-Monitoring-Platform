import os
from pathlib import Path
import sys

import django

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "water_monitor.settings")
django.setup()

from datetime import datetime
import json

from django.conf import settings
from django.core.management import call_command
from django.db import connections


class DatabaseMigrator:
    def __init__(self):
        self.mysql_config = {
            "ENGINE": "django.db.backends.mysql",
            "NAME": "quality_water",
            "USER": "root",
            "PASSWORD": "root",
            "HOST": "localhost",
            "PORT": "3306",
        }

    def create_postgresql_db(self):
        """Create PostgreSQL database if not exists"""
        print("Checking PostgreSQL database...")

        try:
            from django.db import connection

            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            print("PostgreSQL database connection successful!")
            return True
        except Exception as e:
            print(f"PostgreSQL connection failed: {e}")
            print("\nSteps to fix:")
            print("1. Install PostgreSQL: https://www.postgresql.org/download/")
            print("2. Create database: CREATE DATABASE smart_water_monitoring_db;")
            print("3. Update .env file with correct PostgreSQL credentials")
            return False

    def backup_mysql_data(self):
        """Export data from MySQL to JSON"""
        print("Backing up MySQL data...")
        settings.DATABASES["mysql_backup"] = self.mysql_config

        try:
            backup_file = (
                f"backup_mysql_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            backup_path = PROJECT_ROOT / "scripts" / backup_file

            print(f"Exporting to: {backup_path}")
            call_command(
                "dumpdata",
                "--database=mysql_backup",
                "--output=str(backup_path)",
                "--indent=2",
                "monitoring",
            )

            print(f"MySQL data backed up to: {backup_file}")
            return backup_path

        except Exception as e:
            print(f"MySQL backup failed: {e}")
            return None

    def migrate_to_postgresql(self):
        """Run PostgreSQL migrations"""
        print("Setting up PostgreSQL schema...")

        try:
            # Run migrations
            call_command("migrate", "--run-syncdb")
            print("PostgreSQL migrations completed!")
            return True
        except Exception as e:
            print(f"Migration failed: {e}")
            return False

    def import_data_to_postgresql(self, backup_file):
        """Import backed up data to PostgreSQL"""
        if not backup_file or not backup_file.exists():
            print("No backup file found, skipping data import")
            return True

        print("Importing data to PostgreSQL...")

        try:
            call_command("loaddata", str(backup_file))
            print("Data import completed!")
            return True
        except Exception as e:
            print(f"Data import failed: {e}")
            print("You can manually import later using:")
            print(f"python manage.py loaddata {backup_file}")
            return False

    def verify_migration(self):
        """Verify the migration was successful"""
        print("Verifying migration...")

        try:
            from monitoring.models import Device, Reading, User

            user_count = User.objects.count()
            reading_count = Reading.objects.count()
            device_count = Device.objects.count()

            print(f"Migration Results:")
            print(f"   Users: {user_count}")
            print(f"   Readings: {reading_count}")
            print(f"   Devices: {device_count}")

            if user_count > 0 or reading_count > 0:
                print("Migration verification successful!")
            else:
                print("No data found - this might be a fresh installation")

            return True

        except Exception as e:
            print(f"Verification failed: {e}")
            return False

    def run_migration(self):
        """Run the complete migration process"""
        print("Smart Water Monitoring - PostgreSQL Migration")
        print("=" * 60)

        if not self.create_postgresql_db():
            return False

        print("\nMySQL to PostgreSQL Migration Options:")
        print("1. Migrate existing MySQL data")
        print("2. Fresh PostgreSQL installation (skip MySQL backup)")

        choice = input("\nChoose option (1 or 2): ").strip()

        backup_file = None
        if choice == "1":
            backup_file = self.backup_mysql_data()
            if not backup_file:
                print("MySQL backup failed, continuing with fresh installation...")

        if not self.migrate_to_postgresql():
            return False

        if backup_file:
            self.import_data_to_postgresql(backup_file)

        self.verify_migration()

        print("\nPostgreSQL Migration Complete!")
        print("\nNext Steps:")
        print("1. Update your .env file: DATABASE_ENGINE=postgresql")
        print("2. Restart Django server: python manage.py runserver")
        print("3. Create superuser: python manage.py createsuperuser")
        print("4. Test the application: http://localhost:8000")

        return True


if __name__ == "__main__":
    migrator = DatabaseMigrator()
    success = migrator.run_migration()

    if success:
        print("\nMigration completed successfully!")
    else:
        print("\nMigration failed. Check the errors above.")
        sys.exit(1)
