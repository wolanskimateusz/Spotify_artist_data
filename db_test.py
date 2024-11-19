import pyodbc

# Wyświetlenie dostępnych sterowników ODBC
print("Dostępne sterowniki ODBC:")
for driver in pyodbc.drivers():
    print(driver)
