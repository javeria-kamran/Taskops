#!/usr/bin/env python3
"""Test database connection to Neon."""

import asyncpg
import asyncio
import os
import ssl

async def test_connection():
    try:
        # Read directly from .env file
        env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
        db_url = None
        
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('DATABASE_URL='):
                        db_url = line.split('=', 1)[1].strip()
                        break
        
        if not db_url:
            print("❌ DATABASE_URL not found in .env")
            return
        
        print(f"Using DATABASE_URL from file:")
        print(f"  {db_url}\n")
        
        # Extract host for display
        host = db_url.split('@')[-1].split('/')[0] if '@' in db_url else 'unknown'
        print(f'Connecting to: {host}')
        print(f'Timeout: 30 seconds\n')
        
        # Test 1: Try with sslmode from URL
        print("=" * 60)
        print("Test 1: Using URL parameters as-is")
        print("=" * 60)
        try:
            conn = await asyncio.wait_for(
                asyncpg.connect(db_url),
                timeout=30
            )
            version = await conn.fetchval('SELECT version()')
            print(f'✅ Connection successful!')
            print(f'PostgreSQL: {version[:80]}...')
            await conn.close()
            return
        except Exception as e:
            print(f'❌ Failed: {type(e).__name__}: {str(e)[:150]}')
        
        # Test 2: Try with SSL disabled
        print("\n" + "=" * 60)
        print("Test 2: With SSL disabled")
        print("=" * 60)
        try:
            clean_url = db_url.split('?')[0] if '?' in db_url else db_url
            conn = await asyncio.wait_for(
                asyncpg.connect(clean_url, ssl=False),
                timeout=30
            )
            version = await conn.fetchval('SELECT version()')
            print(f'✅ Connection successful!')
            print(f'PostgreSQL: {version[:80]}...')
            await conn.close()
            return
        except Exception as e:
            print(f'❌ Failed: {type(e).__name__}: {str(e)[:150]}')
        
        # Test 3: Try with custom SSL context
        print("\n" + "=" * 60)
        print("Test 3: With custom SSL context (insecure)")
        print("=" * 60)
        try:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            clean_url = db_url.split('?')[0] if '?' in db_url else db_url
            conn = await asyncio.wait_for(
                asyncpg.connect(clean_url, ssl=ssl_context),
                timeout=30
            )
            version = await conn.fetchval('SELECT version()')
            print(f'✅ Connection successful!')
            print(f'PostgreSQL: {version[:80]}...')
            await conn.close()
            return
        except Exception as e:
            print(f'❌ Failed: {type(e).__name__}: {str(e)[:150]}')
        
        print("\n" + "=" * 60)
        print("⚠️  All connection attempts failed")
        print("=" * 60)
        print("\nPossible causes:")
        print("  1. Incorrect credentials (user/password)")
        print("  2. Neon account suspended or project deleted")
        print("  3. Network connectivity issues")
        print("  4. Database doesn't exist")
        
    except Exception as e:
        print(f'❌ Error: {type(e).__name__}: {e}')

if __name__ == '__main__':
    asyncio.run(test_connection())
