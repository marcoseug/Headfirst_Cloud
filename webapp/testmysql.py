import mysql.connector

import platform
using_distro = False
try:
    import distro
    using_distro = True
except ImportError:
    pass

if using_distro:
    linux_distro = distro.like()
else:
    linux_distro = platform.linux_distribution()[0]

# Connect to MySQL
connection = mysql.connector.connect(
    host="localhost",
    user="vsearch",
    password="mree",
    database="vsearchlogDB"
)

# Check if connection was successful
if connection.is_connected():
    print("Connected to MySQL!")
else:
    print("Failed to connect to MySQL.")

# Perform database operations
# For example, you can execute queries here

# Close the connection
connection.close()