#a table utility class that facilitates tabular/csv based IO
#and class generation
import copy, csv,sys
csv.field_size_limit(sys.maxsize)
class rtable(object):
    """
    A lightweight table tool that can do IO and simple filtering/ordering.
    """

    def __init__(self, another = None):
        """
        Example usage
        a= tabular()
        b= tabular(a)
        now a and b are deep copies
        c= tabular(["C1"], [[1],[2]])
        c is now a valid table of shape 2,1
        """
        self.header = {}
        #unique identifier
        self.data = []
        self.order_list= None
        #data is accessed by unique key and header (idx)
        self.nr= 0
        self.nc= 0
        if another is None:
            return
        else:
            self=another.another()
            return
    @property
    def head(self):
        return sorted(self.header.keys(),key=lambda x: self.header[x])
    @property
    def heads(self):
        return sorted(self.header.items(),key=lambda x: x[1])
    @property
    def shape(self):
        return self.nr,self.nc
    @property
    def cols (self):
        return [i for i,j in sorted(self.header.items(), key = lambda x : x[1])]
    @property
    def rows (self):
        return self.data

    def viz(self):
        """
        Export for Viz/js usable data formats
        """
        return (self.header(), self.data)

    def indexBy(self,idx):
        self.reorder()
        col = self % idx
        if len(set((col)))< len(col):
            print "Your column is not unique, cannot index the data"
            return
        self.lookup=dict(zip(col, xrange(self.nr)))
        return

    def getIndex(self,key):
        if not hasattr(self, "lookup") or key not in self.lookup:
            return None
        else:
            return self.lookup[key]


    def __lt__ (self,row=None):
        if len(row)<len(self.header.keys()):
            raise ValueError("Added Row must have same length as table, instead got {0:d} and {1:d}".format(len(self.header.keys()), len(row)))
        if self.nc==0: self.nc=len(row)
        if len (row) > len(self.header):
            self.data.append(row[:len(self.header)])
            print "Added a row longer than header, truncating. If this is undesired, consider quitting {0:d} vs {1:d} , {2}".format(len(row), len(self.header), row)
        else:
            self.data.append(row)
        self.nr +=1
        return self

    def another (self, cc):
        """
        Export another table tools with rows manipulated by self.order_list
        """
        another = tabular()
        another.header = copy.deepcopy(self.header);
        another.nc = self.nc
        for i in cc:
            temp = copy.deepcopy(self.data[i])
            another < temp
        return another

    def add_row(self,row=None):
        return self < row

    def __lshift__ (self, pp = None):
        col,header = pp
        return self.add_column(col,header)

    def add_column(self, col= None, header = None, add="ignore"):
        if header is None or col is None:
            raise ValueError("Must input both column header and column")
        if header in self.header:
            if add == "strict":
                raise KeyError ("Column tag conflict {0}".format(header))
            elif add == "ignore":
                print "Ignored one duplicate column {0}".format(header)
                return
            else:
                ifx=2
                while header+"-{}".format(ifx) in self.header:
                    ifx+=1
                header=header+"-{}".format(ifx)
                print "Renamed to {0}".format(header)
        if len(self.data)==0:
            for i in xrange(len(col)):
                self.data.append([col[i]])
            self.nr=len(col)
        elif len(col)!=self.nr:
            raise ValueError("Column length is incorrect!")
        else:
            for i in xrange(self.nr):
                self.data[i].append(col[i])
        self.header [header] = self.nc
        self.nc+=1
        return

    def __mul__(self,f):
        """
        Data maps
        """
        self.data=[[f(i) for i in j] for j in self.data]
        return self

    def reorder(self):
        #self.order_list=None
        del self.order_list
        self.order_list = None
        return

    def order (self, f=lambda x: x, idx=0, reverse=False):
        col = self.col_map(f, idx, overwrite=False)
        self.order_list=list(xrange(self.nr))
        self.order_list = sorted(self.order_list,\
                key=lambda x: col[x], reverse=reverse)
        return self.order_list

    def filter(self, f=lambda x: True, idx=0):
        self.reorder()
        self.order_list=[]
        col = self % idx
        assert (len (col)==self.nr)
        for i in xrange(self.nr):
            if f(col[i]):
                self.order_list.append(i)
        return self.order_list

    def col_map (self, f, idx=None, overwrite=True):
        """
        Column wise maps
        """
        if type (idx)!=int:
            idx=self.header[idx]
        if idx >= self.nc:
            raise ValueError("Column index out of bound")
        col = []
        for i in xrange(self.nr):
            val=f(self.data[i][idx])
            col.append(val)
            if overwrite:
                self.data[i][idx]=val
        return col

    def col_maps(self, fs,idx=None):
        cols = []
        for f in fs:
            cols=self.col_map(f,idx)
        return cols
    def cols_map(self, f,idx=None):
        if type(idx) == int or type(idx)==str:
            idx = [idx]
        elif type(idx) == tuple:
            if len(idx)==1 or not idx[1]:
                idx=range(0,self.nc)[idx[0]:]
            else:
                idx=range(0,self.nc)[idx[0]:idx[1]]
        elif type(idx)==list:
            pass
        else:
            raise ValueError("Wrong format")
        cols = []
        for idx1 in idx:
            cols.append(self.col_map(f,idx1))
        return cols
    def cols_maps(self, fs,idxs=None):
        cols = []
        for f in fs:
            cols=self.cols_map(f,idx)
        return cols

    def __mod__ (self, idx=None):
        """
        Column wise access, examples:
        t % ["C1", 2] -> column with "C1" and col 3
        t % 1 -> col2
        t % (-3 , ) : return cols[-3:]
           Note: Can also use 0 instead of nothing
           Also: t % (, 2) does NOT work, use (0,2) instead
        """
        _temp = self.cols_map(lambda x: x, idx)
        if self.order_list:
            temp=[]
            for _tmp in _temp:
                tmp = [_tmp[i] for i in self.order_list]
                temp.append(tmp)
        else:
            temp = _temp
        if len (temp)==1:
            temp = temp[0]
        return temp

    def col_assign (self, col, idx):
        if type(idx)==str and idx in self.header:
            idx=self.header[idx]
        elif type(idx)==int and idx<self.nc:
            pass
        else:
            raise ValueError("Index for column is wrong.")
        if len(col)!=self.nr:
            raise ValueError("Column length incorrect")
        for i in xrange(self.nr):
            self.data[i][idx]=col[i]

    def row_assign (self, row, idx):
        if idx>=self.nr:
            raise ValueError("Row Index too large")
        if(len(row)!=self.nc):
            raise ValueError("Row length incorrect")
        self.data[idx]=row
        return
    #the following are accessor lifters
    def __setitem__ (self, key, value):
        return self.data.__setitem__(key, value)
    def __getitem__ (self, key):
        return self.data.__getitem__(key)
    def __delitem__ (self, key):
        return self.data.__delitem__(key)
    def __getslice__ (self, i,j):
        return self.data.__getslice__(i,j)
    def __setslice__ (self, i,j, key):
        return self.data.__setslice__(i,j,key)
    def __delslice__ (self, i,j):
        return self.data.__delslice__(i,j)
    def __len__ (self):
        return self.data.__len__()
    def __reversed__(self):
        return self.data.__reversed__()
    def __iter__(self):
        return self.data.__iter__()
    #here we ask if a certain column is in the collection
    def __contains__(self,item):
        return self.header.__contains__(item)

    def __str__(self):
        output = ["\t".join([str(i[0]) for i in sorted(self.header.items(),key=lambda x: x[1])])]
        output2= ["\t".join(map(str,i)) for i in self.data]
        return "\n".join(output2)

    def __repr__(self):
        #like str but with order
        output = ["\t".join([str(i[0]) for i in sorted(self.header.items(),key=lambda x: x[1])])]
        output2= []
        if self.order_list is None:
            cc = xrange(len(self.data))
        else: cc= self.order_list
        for i in cc:
            output2.append("\t".join(map(str,self.data[i])))
        return "\n".join(output+output2)

    def purge (self):
        """
        Purge data by del methods and then reset the tabular object
        """
        del self.data
        del self.order_list
        self.nc=self.nr=0
        self.data=[]
        self.header={}
        return self

    def load (self, cols, rows,add="ignore"):
        """
        This is the initializer load routine.
        Will delete current data
        """
        self.__init__()
        for col in cols:
            self.add_column([],col,add)
        for row in rows:
            self < row
        return self

    def loadf(self, fname, sep="\t", guard="", header = None, isFile=True, add=""):
        self.purge()
        if not isFile:
            f=fname.split("\n")
            #allow this to raise exception
        else:
            f=open(fname,"r")
        if guard != "":
            reader = csv.reader((row for row in f if row[0]!="#"), delimiter=sep, quotechar=guard)
        else:
            reader = csv.reader((row for row in f if row[0]!="#"), delimiter=sep)
        if header is None:
            try:
                header= reader.next()
            except:
                print "Your file is empty!"
                return
        try:
            testrow = reader.next()
        except:
            print "Your file has only one line!"
            return self.load(header,[])
        if len(header) == len (testrow) - 1:
            print "Automatically padding one column label for your data. IF this is undesired please check!"
            header = ["row_id"]+header
        elif len(header) == len(testrow):
            pass
        else:
            print "your header is "
            print header
            print "your first row is "
            print testrow
            raise ValueError("Parsing failed, header too short/long for the data")
        rows = [testrow]
        for line in reader:
            if len(line)>0:
                rows.append(line)
        return self.load(header, rows,add)
    def as_dicts(self, idx = None):
        """
        Export the table as dicts of lists and provide optionally an array of indices
        """
        if idx:
            idxs = self % idx
            assert len(set(idxs)) == self.nr, "Indice column is not unique!"
        else:
            idxs = None
        out = {}
        for i in self.head:
            if i == idx:
                continue
            out[i] = self % i
        if idxs:
            return out,idxs
        else:
            return out
