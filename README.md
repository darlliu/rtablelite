# rtablelite
pure python implementation of R/pandas table object class with simple IO functions. 

This is a very modest attempt at creating a R/pandas like data table object class for IO purposes working primarily on tsv files. The goal is to have a lightweight tool in pure python with not much overhead, which can be used with short one liners for simple IO.

basic use case
```python
from rtablelite import rtable

r=rtable()
r.loadf("./myfile")
print r.head 
#this shows the header as a list of column labels
#assume this gives "["Col1","Col2"] and the table has 3 rows each column

col2s=r%"Col2" #get all values from column with label "Col2"

r<<([100,200,300],"newCol3")#add a new column

r<([4,40,400]) #add a new row

r.filter(lambda x: int(x)>=200, "newCol3")
#filter using simple lambdas on values within a single column, values are by default strings

open("filtered_table.tsv","w").write(repr(r))
#using repr gives the right string for tsv output, with filtering and ordering intact

r.reorder()#can filter or order rows, but need to call reorder inbetween

r.order(lambda x: -int(x), "newCol3")

open("ordered_table.tsv","w").write(repr(r))
```
