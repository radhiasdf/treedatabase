import sqlite3
import csv
import tabulate as tab
import tkinter

# import replit

backkey = "<"


# Inserting data from the csvs to the databases
def InsertCSVs():
	with open("maori trees - Sheet1.csv", "r") as file:
		reader = csv.reader(file)
		for row in reader:
			c.execute("""INSERT INTO Trees (ID, maori_name, reference, scientific_name) 
						VALUES (?, ?, ?, ?);""", (row[0], row[1], row[2], row[3]))

	with open("employee.csv", "r") as file:
		reader = csv.reader(file)
		for row in reader:
			c.execute("""INSERT INTO Employees (ID, first_name, last_name, email, gender, employerID) 
						VALUES (?, ?, ?, ?, ?, ?);""", (row[0], row[1], row[2], row[3], row[4], row[5]))


# Error checking inputs
def checkinput(text, type, rangeend):
	inp = input(text).strip()
	if inp == backkey:
		return backkey
	if type == "int":
		try:
			inp = int(inp)
			if inp in range(1, rangeend):
				return inp
			else:
				return False
		except:
			return False


connect = sqlite3.connect('Database.db')
c = connect.cursor()


def update():
	# replit.clear()
	print("-Enter '" + backkey + "' to go back-")


# This resets the thing
try:
	c.execute("SELECT * FROM Trees;")
	print('alreadyasdf')
except sqlite3.OperationalError:
	print('nope')
	# Resetting tables bc duplication error
	c.execute("DROP TABLE IF EXISTS 'Trees';")
	c.execute("DROP TABLE IF EXISTS 'Employees';")
	# Creating tables
	c.execute("""
	CREATE TABLE Trees (
		ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
		maori_name TEXT NOT NULL,
		reference TEXT NOT NULL,
		scientific_name TEXT NOT NULL
	);
	""")
	c.execute("""
	CREATE TABLE Employees (
		ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
		first_name TEXT NOT NULL,
		last_name TEXT NOT NULL,
		email TEXT NOT NULL,
		gender TEXT NOT NULL,
		employerID INTEGER NOT NULL REFERENCES Trees(ID)
	);
	""")
	InsertCSVs()
	connect.commit()

tables = ["Trees", "Employees"]
fields = ["Trees.ID", "Trees.maori_name", "Trees.reference", "Trees.scientific_name", "Employees.ID",
		  "Employees.first_name", "Employees.last_name", "Employees.email", "Employees.gender", "Employees.employerID"]


def Main():
	while True:
		update()
		action = input("What do you want to do?\n1. Add\n2. Search\n")

		# Adding stuff
		if action == "1":
			while True:
				querytable = table_addnew()
				try:
					fields_addnew(querytable)
				except:
					break

		# Looking for something
		if action == "2":
			while True:
				update()
				print("Available fields:")
				for i in range(len(fields)):
					print(str(i + 1) + ". " + fields[i])

				shownfields_nameslist = displayed_fields_searching()
				try:
					filters = AskFilters(shownfields_nameslist)
				except:
					break
				try:
					ExecuteSearchingQuery(filters)
				except:
					pass

# For adding new entries
def table_addnew():
	update()
	while True:
		querytable = checkinput("Available tables: \n1.Trees\n2.Employees\nEnter number: ", "int", 3)
		if querytable == backkey:
			return
		elif querytable != False:
			break
	# converts the number into the name
	querytable = tables[querytable - 1]
	return querytable


def fields_addnew(querytable):
	# asks the user for every field to be filled
	addinglist = []
	for field in fields:
		if querytable in field and ".ID" not in field:
			while True:
				temp = input("Enter new " + field + ": ").strip()
				if temp == backkey:
					return
				elif "employerID" in field:
					try:
						temp = int(temp)
						break
					except:
						pass
				else:
					break
			addinglist.append(temp)

	# adds the data according to the table

	if querytable == 'Trees':
		c.execute("""INSERT INTO Trees(maori_name, reference, scientific_name)
		VALUES (?,?,?);""", (addinglist[0], addinglist[1], addinglist[2]))

		c.execute("SELECT * FROM " + querytable + ";")
		headers = fields[1:3]

	if querytable == "Employees":
		c.execute("SELECT * FROM Trees WHERE Trees.ID = ?;", (int(addinglist[4]),))
		if len(c.fetchall()) == 0:
			print("\nnote: the company ID doesn't exist\n")

		c.execute("""INSERT INTO Employees(first_name, last_name, email, gender, employerID)
		VALUES (?,?,?,?,?);""", (addinglist[0], addinglist[1], addinglist[2], addinglist[3], addinglist[4]))

		# For employees the displayed info is all the people in their identified company
		c.execute("""SELECT Trees.maori_name, Employees.ID, Employees.first_name, Employees.last_name FROM Trees
					INNER JOIN Employees
					ON Trees.ID = Employees.employerID
					WHERE Trees.ID = ?;""", (addinglist[4],))
		headers = ["Trees.maori_name", "Employees.ID", "Employees.first_name", "Employees.last_name"]

	connect.commit()
	# displays the table with added data
	print(tab.tabulate(c.fetchall(), headers, tablefmt='simple'))
	action = input("\nEnter nothing to add more, '" + backkey + "' to do something else (go back): ").strip()
	if action.lower() == "b": pass


# asking for the displayed fields. The numbers correspond to fields and theyre strung up to a string for execute to use.
def displayed_fields_searching():
	global queryFields
	global queryFieldsList
	while True:
		valid = True
		inp = input("Enter numbers separated by commas for all fields to be displayed in order, eg. 2,5,6:\n")
		if inp == backkey:
			return
		list = inp.split(",")
		queryFields = ""
		for i in list:
			try:
				queryFields += fields[int(i) - 1] + ", "
			except:
				valid = False
		if valid: break
	queryFields = queryFields[:-2]
	queryFieldsList = queryFields.split(", ")
	return queryFieldsList


def AskFilters(shownfields_nameslist):
	# applying filters (if any) for each field
	filters = []
	for field in shownfields_nameslist:
		while True:
			temp = input("Leave blank or enter something as a filter in " + field + ": ").strip()
			if temp == backkey:
				return
			if temp == "": break
			try:
				temp = int(temp)
				break
			except:
				if 'ID' in field:
					pass  # stay in while loop and re-input bc IDs cant be letters
				else:
					temp = temp.capitalize()
					break
		filters.append(temp)
	return filters


def ExecuteSearchingQuery(filters):
	# putting together the filters into a query part
	filtersquery = ""
	filters_set = set(filters)
	try:
		filters_set.remove('')
	except:
		pass
	if len(filters_set) > 0: filtersquery += " WHERE"

	appliedfilters = 0
	for i in range(len(filters)):
		if filters[i] != '':
			appliedfilters += 1
			if appliedfilters > 1: filtersquery += " AND"
			if type(filters[i]) == int:
				filtersquery += " " + queryFieldsList[i] + " LIKE (" + str(filters[i]) + ")"
			else:
				filtersquery += " " + queryFieldsList[i] + " LIKE ('" + filters[i] + "')"

	# if the user's just searching in the Trees tables theres no need to join the 2 tables. so if were just searching company names theyre not repeated.
	jointablesquery = ""
	if "Employees" in queryFields:
		jointablesquery = " INNER JOIN Employees ON Trees.ID = Employees.employerID"

	# selecting and printing the database
	wholequery = "SELECT " + queryFields + " FROM Trees" + jointablesquery + filtersquery + ";"
	c.execute(wholequery)
	fetchall = c.fetchall()
	headers = queryFieldsList
	print("\n" + tab.tabulate(fetchall, headers, tablefmt='simple'))
	if len(fetchall) == 0: print("No results found")

	action = input("\nEnter nothing to do another search, '" + backkey + "' to do something else (go back): ")
	if action.lower() == backkey: Main()


Main()
