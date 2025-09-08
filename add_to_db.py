#!/usr/bin/env python3
"""
Database Management Script for Zenith Club Certificate Portal
This script allows you to add, view, and manage certificate entries in the database.
"""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# Database configuration
DATABASE = "certificates.db"

def init_db():
    """Initialize database with tables if they don't exist"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create certificates table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS certificates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_number TEXT UNIQUE NOT NULL,
            has_certificate INTEGER DEFAULT 0,
            download_count INTEGER DEFAULT 0,
            last_downloaded DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create downloads log table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS download_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_number TEXT NOT NULL,
            email TEXT NOT NULL,
            downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

def add_certificate(roll_number, has_certificate=1):
    """Add a new certificate entry to the database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        # Convert roll number to lowercase for consistency
        roll_number = roll_number.lower().strip()
        
        cursor.execute('''
            INSERT INTO certificates (roll_number, has_certificate)
            VALUES (?, ?)
        ''', (roll_number, has_certificate))
        
        conn.commit()
        print(f"✅ Added certificate entry for roll number: {roll_number}")
        return True
        
    except sqlite3.IntegrityError:
        print(f"❌ Roll number {roll_number} already exists in database!")
        return False
    except Exception as e:
        print(f"❌ Error adding certificate: {e}")
        return False
    finally:
        conn.close()

def view_certificates():
    """View all certificate entries in the database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT roll_number, has_certificate, download_count, last_downloaded, created_at
        FROM certificates
        ORDER BY created_at DESC
    ''')
    
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        print("📭 No certificates found in database.")
        return
    
    print(f"\n📋 Certificate Database ({len(results)} entries):")
    print("-" * 80)
    print(f"{'Roll Number':<20} {'Has Cert':<10} {'Downloads':<10} {'Last Download':<20} {'Created':<15}")
    print("-" * 80)
    
    for row in results:
        roll_number, has_cert, downloads, last_dl, created = row
        has_cert_text = "✅ Yes" if has_cert else "❌ No"
        last_dl_text = last_dl[:16] if last_dl else "Never"
        created_text = created[:16] if created else "Unknown"
        
        print(f"{roll_number:<20} {has_cert_text:<10} {downloads:<10} {last_dl_text:<20} {created_text:<15}")

def search_certificate(roll_number):
    """Search for a specific certificate entry"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    roll_number = roll_number.lower().strip()
    
    cursor.execute('''
        SELECT * FROM certificates WHERE roll_number = ?
    ''', (roll_number,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        id_val, roll_num, has_cert, downloads, last_dl, created = result
        print(f"\n🔍 Certificate Details for {roll_num}:")
        print(f"   ID: {id_val}")
        print(f"   Has Certificate: {'✅ Yes' if has_cert else '❌ No'}")
        print(f"   Download Count: {downloads}")
        print(f"   Last Downloaded: {last_dl or 'Never'}")
        print(f"   Created At: {created}")
        return True
    else:
        print(f"❌ No certificate found for roll number: {roll_number}")
        return False

def delete_certificate(roll_number):
    """Delete a certificate entry from the database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    roll_number = roll_number.lower().strip()
    
    # Check if exists first
    cursor.execute('SELECT roll_number FROM certificates WHERE roll_number = ?', (roll_number,))
    if not cursor.fetchone():
        print(f"❌ Roll number {roll_number} not found in database!")
        conn.close()
        return False
    
    # Delete the record
    cursor.execute('DELETE FROM certificates WHERE roll_number = ?', (roll_number,))
    conn.commit()
    conn.close()
    
    print(f"✅ Deleted certificate entry for roll number: {roll_number}")
    return True

def add_dummy_data():
    """Add the requested dummy data"""
    dummy_roll = "220btccse000"
    success = add_certificate(dummy_roll, has_certificate=1)
    if success:
        print(f"🎯 Dummy certificate added!")
        print(f"   Roll Number: {dummy_roll}")
        print(f"   Email Format: dummy.{dummy_roll}@sushantuniversity.edu.in")

def interactive_menu():
    """Interactive menu for database operations"""
    while True:
        print("\n🎓 Zenith Club Certificate Database Manager")
        print("=" * 50)
        print("1. Add Certificate Entry")
        print("2. View All Certificates")
        print("3. Search Certificate")
        print("4. Delete Certificate")
        print("5. Add Dummy Data (220btccse000)")
        print("6. Initialize Database")
        print("0. Exit")
        print("-" * 50)
        
        try:
            choice = input("Select an option (0-6): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                roll_num = input("Enter roll number: ").strip()
                if roll_num:
                    has_cert = input("Has certificate? (y/n) [default: y]: ").strip().lower()
                    has_cert_val = 0 if has_cert == 'n' else 1
                    add_certificate(roll_num, has_cert_val)
                else:
                    print("❌ Roll number cannot be empty!")
            elif choice == "2":
                view_certificates()
            elif choice == "3":
                roll_num = input("Enter roll number to search: ").strip()
                if roll_num:
                    search_certificate(roll_num)
                else:
                    print("❌ Roll number cannot be empty!")
            elif choice == "4":
                roll_num = input("Enter roll number to delete: ").strip()
                if roll_num:
                    confirm = input(f"Are you sure you want to delete {roll_num}? (y/N): ").strip().lower()
                    if confirm == 'y':
                        delete_certificate(roll_num)
                    else:
                        print("❌ Deletion cancelled.")
                else:
                    print("❌ Roll number cannot be empty!")
            elif choice == "5":
                add_dummy_data()
            elif choice == "6":
                init_db()
            else:
                print("❌ Invalid option! Please select 0-6.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main function"""
    # Ensure database exists
    init_db()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "add" and len(sys.argv) >= 3:
            roll_number = sys.argv[2]
            add_certificate(roll_number)
        elif command == "view":
            view_certificates()
        elif command == "search" and len(sys.argv) >= 3:
            roll_number = sys.argv[2]
            search_certificate(roll_number)
        elif command == "delete" and len(sys.argv) >= 3:
            roll_number = sys.argv[2]
            delete_certificate(roll_number)
        elif command == "dummy":
            add_dummy_data()
        else:
            print("Usage:")
            print("  python add_to_db.py add <roll_number>")
            print("  python add_to_db.py view")
            print("  python add_to_db.py search <roll_number>")
            print("  python add_to_db.py delete <roll_number>")
            print("  python add_to_db.py dummy")
            print("  python add_to_db.py (for interactive menu)")
    else:
        # Run interactive menu
        interactive_menu()

if __name__ == "__main__":
    main()
