#!/usr/bin/env python3
"""Simple connectivity test - just check if we can reach the host."""

import socket
import subprocess

host = "ep-orange-bird-ah8awb4f.c-3.us-east-1.aws.neon.tech"
port = 5432

print(f"Testing network connectivity to {host}:{port}\n")

# Test 1: DNS resolution
print("=" * 60)
print("Test 1: DNS Resolution")
print("=" * 60)
try:
    ip = socket.gethostbyname(host)
    print(f"✅ {host} resolves to {ip}")
except socket.gaierror as e:
    print(f"❌ DNS resolution failed: {e}")
    exit(1)

# Test 2: TCP connection
print("\n" + "=" * 60)
print("Test 2: TCP Connection to PostgreSQL port")
print("=" * 60)
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    result = sock.connect_ex((host, port))
    if result == 0:
        print(f"✅ Can reach {host}:{port}")
        sock.close()
    else:
        print(f"❌ Cannot reach {host}:{port} (error code: {result})")
except Exception as e:
    print(f"❌ TCP test failed: {e}")

# Test 3: Try psql if available
print("\n" + "=" * 60)
print("Test 3: psql command (if available)")
print("=" * 60)
try:
    result = subprocess.run(["psql", "--version"], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        print(f"✅ psql is available: {result.stdout.strip()}")
        print("\nTry running this command manually:")
        print('psql "postgresql://neondb_owner:npg_c64GDzMSKbge@ep-orange-bird-ah8awb4f.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"')
    else:
        print("❌ psql is not available")
except Exception as e:
    print(f"ℹ️  psql not available or error: {e}")
    print("Install PostgreSQL client to test with psql")
