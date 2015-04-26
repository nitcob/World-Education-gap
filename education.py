import csv
import requests
import re
import pandas as pd
import sqlite3 as lite
import numpy as py
import csv
import math
from bs4 import BeautifulSoup

url = "http://web.archive.org/web/20110514112442/http://unstats.un.org/unsd/demographic/products/socind/education.htm"

r = requests.get(url)

soup = BeautifulSoup(r.content)

for row in soup('table'):
    print row

soup('table')[6]
for tag in soup.find_all(re.compile("^t")):
    print(tag.name)


A = soup('table')[6].findAll('tr', {'class': 'tcont'})
B = [x for x in A if len(x)==25] #removing records without value
records = []

for rows in B:

    col = rows.findAll('td')
    country = col[0].string
    year = col[1].string
    total = col[4].string
    men = col[7].string
    women = col[10].string
    record = (country, year, total, men, women)
    records.append(record)

column_name = ['country', 'year', 'total', 'men', 'women']

table = pd.DataFrame(records, columns = column_name)
print table
#Open an clean CSV file
con = lite.connect('gdp.db')
cur = con.cursor()
con.execute('DROP TABLE IF EXISTS gdp')
con.execute('DROP TABLE IF EXISTS education')
con.execute ('CREATE TABLE education (country_name text, year integer, total integer, men integer, woman integer)')
con.execute ('CREATE TABLE gdp (country_name, country_code,  _1999, _2000, _2001, _2002, _2003, _2004, _2005, _2006, _2007, _2008, _2009, _2010)')

with open('/home/nitcob/Downloads/ny.gdp.mktp.cd_Indicator_en_csv_v2/ny.gdp.mktp.cd_Indicator_en_csv_v2.csv','rU') as inputFile:
    next(inputFile) # skip the first two lines
    next(inputFile)
    header = next(inputFile)
    inputReader = csv.reader(inputFile)
    for line in inputReader:
        with con:
            cur.execute('INSERT INTO gdp (country_name, country_code, _1999, _2000, _2001, _2002, _2003, _2004, _2005, _2006, _2007, _2008, _2009, _2010) VALUES ("' + line[0] + '","' + '","'.join(line[42:-5]) + '");')
#print data from gdp in order to understand itr
with con:
    cur= con.cursor()
    cur.execute('SELECT*FROM gdp')

    rows = cur.fetchall()
    gdp = pd.DataFrame(rows)
print gdp

columns = ['Country Name','Country Code','Indicator Name','Indicator Code',
           '1999','2000','2001','2002','2003','2004','2005','2006','2007','2008','2009','2010']
df1999to2010 = pd.read_csv('/home/nitcob/Downloads/ny.gdp.mktp.cd_Indicator_en_csv_v2/ny.gdp.mktp.cd_Indicator_en_csv_v2.csv', skiprows=2, usecols=columns)

#create a df from CSV file

df1999to2010.set_index('Country Name', inplace=True)

#merged table and df1999to2010

merged = pd.merge(table, df1999to2010, how='inner', left_index=True, right_index=True)

#searches and matches values and years
merged['CommonYear'] = merged.apply(lambda x: x['year'], axis=1)
merged['CommonGDP'] = merged.apply(lambda x: x[x['year']], axis=1)

finalDataFrame = merged[['year', 'total', 'men', 'women', 'CommonGDP']]

finalDataFrame['logGDP'] = py.log(finalDataFrame['CommonGDP'])

finalDataFrame.sort('CommonGDP', ascending=True, inplace=True)

#ploted data
finalDataFrame.plot('total', 'logGDP')
