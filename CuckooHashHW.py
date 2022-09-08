#I hereby certify that this program is solely the result of my own work and is in compliance with the Academic Integrity policy of the course syllabus and the academic integrity policy of the CS department.


from BitHash import *
import cityhash
import pytest
import random

class CuckooHash(object):
    
    def __init__(self, size):
        self.__HashTab1 = [None] * size
        self.__HashTab2 = [None] * size 
        
    def find(self, key):
        
        # hash the key in both tables
        hashVal1 = BitHash(key, 1) % len(self.__HashTab1)
        hashVal2 = BitHash(key, 2) % len(self.__HashTab1)
        
        # check if it is in the first table 
        if self.__HashTab1[hashVal1] and self.__HashTab1[hashVal1][0] == key:
            return self.__HashTab1[hashVal1][1]
        elif self.__HashTab2[hashVal2] and self.__HashTab2[hashVal2][0] == key:
            return self.__HashTab2[hashVal2][1]
        else:
            return None 
            
    def insert(self, key, data):
                
        # if the key is already in the tables, return False
        if self.find(key) != None: 
            return False 
        
        else:
            # hash the key
            hashVal = BitHash(key, 1) % len(self.__HashTab1)
               
            # hold whatever is in the key's position in temp, and put the key 
            # and data in that position in the table
            temp = self.__HashTab1[hashVal]
            self.__HashTab1[hashVal] = key, data
            
            # if there is already a key in the position of the hash table, 
            # call method to deal with collisions 
            if temp != None: 
                # if collisions was successful, then insert was successful and 
                # return the key, data pair 
                if self.__collision(temp, False, False, 1): 
                    return key, data 
                
            # otherwise, insert was successful
            else: 
                return key, data
                
    def __collision(self, temp, new1 = False, new2 = False, tableExp = 1):
        
        count = 0        
        
        # while there is a key data pair already in the bucket and it   
        # has looped fewer than 50 times
        while temp and count < 50: 
            
            # increment count each time go through the loop
            count += 1
            
            # if have looped an odd number of times, it means must hash to 
            # the second table
            if count % 2 == 1: 
                
                # if called by insert method 
                if not new1:                 
                    
                    # hash the temp to the 2nd table
                    hashValTemp2 = BitHash(temp[0], 2) % len(self.__HashTab2)                    
            
                    # store whatever is in temp's position in the 2nd table as temp
                    # and put temp from table 1 in that position in table 2
                    temp, self.__HashTab2[hashValTemp2] = self.__HashTab2[hashValTemp2], temp
                
                # if collision was called by growHash method
                else:
                    
                    # hash the temp to the 2nd table
                    hashValTemp2 = BitHash(temp[0], 2) % len(new2)                    
                    
                    # store whatever is in temp's position in the 2nd table as temp
                    # and put temp from table 1 in that position in table 2
                    temp, new2[hashValTemp2] = new2[hashValTemp2], temp
                    
            # if have looped an even number of times, it means must hash to 
            # the first table                
            else: 
             
                # if called by insert method 
                if not new1:                 
       
                    # hash the temp to the 1st table
                    hashValTemp1 = BitHash(temp[0], 1) % len(self.__HashTab1)
                                    
                    # store whatever is in temp's position in the 1st table as temp
                    # and put temp from table 2 in that position in table 1
                    temp, self.__HashTab1[hashValTemp1] = self.__HashTab1[hashValTemp1], temp  
                
                #if collision was called by growHash method
                else: 
                    
                    # hash the temp to the 1st table
                    hashValTemp1 = BitHash(temp[0], 1) % len(new1)                                    
                    
                    # store whatever is in temp's position in the 1st table as temp
                    # and put temp from table 2 in that position in table 1
                    temp, new1[hashValTemp1] = new1[hashValTemp1], temp
                    
        # fell out of loop either because found an empty spot in the table 
        # or because exceeded 50 loops without finding an empty spot 
        
        # if fell out because found an empty spot, insertion succeeded 
        if not temp: return True
    
        # if fell out because looped 50 times, must grow the tables and rehash
        if count == 50: 
            
            # if invoking growHash returns true, then successfully dealt with 
            # collisions and the key, data pair was inserted 
            if self.__growHash(tableExp, temp): 
                return True
    
    def __growHash(self, tableExp, temp = False):
        
        # create 2 new hash tables 
        new1 = [None] * (len(self.__HashTab1) * (2 ** tableExp))
        new2 = [None] * (len(self.__HashTab2) * (2 ** tableExp))
        
        # reset bithash
        ResetBitHash()
        
        # immediately insert temp - the key/data pair that we are left with after
        # collision failed - into the new fist table
        hashVal = BitHash(temp[0], 1) % (len(new1))
        new1[hashVal] = temp
        
        # loop through the old hash tables
        for i in range(len(self.__HashTab1)):
            
            # insert i from the first hash table to the first new table
            if self.__HashTab1[i] != None: 
                
                oldKey = self.__HashTab1[i][0]
                oldData = self.__HashTab1[i][1]
                
                # rehash the key 
                hashVal = BitHash(oldKey, 1) % (len(new1))
                
                # hold whatever is in that position on the new table, and insert
                # the key and data as a tuple 
                temp = new1[hashVal]
                new1[hashVal] = oldKey, oldData
                
                # if there is already a key in the position of the hash table, 
                # call method to deal with collisions 
                if temp != None:
                    tableExp +=1
                    self.__collision(temp, new1, new2, tableExp)            

            # insert i from the second hash table to the first new table
            if self.__HashTab2[i] != None:
                
                oldKey = self.__HashTab2[i][0]
                oldData = self.__HashTab2[i][1]
                
                # rehash the key 
                hashVal = BitHash(oldKey, 1) % (len(new1))
                
                # hold whatever is in that position on the new table, and insert
                # the key and data as a tuple 
                temp = new1[hashVal]
                new1[hashVal] = oldKey, oldData
                
                # if there is already a key in the position of the hash table, 
                # call method to deal with collisions 
                if temp != None:
                    tableExp +=1
                    self.__collision(temp, new1, new2, tableExp)                 
    
        # once finish, set the old hash tables to point to the new ones and
        # return true
        self.__HashTab1 = new1
        self.__HashTab2 = new2
        return True 
    
    def delete(self, key):
        
        # hash the key in both tables
        hashVal1 = BitHash(key, 1) % len(self.__HashTab1)
        hashVal2 = BitHash(key, 2) % len(self.__HashTab1)
       
        # check if it is in the first table and if it is, set its position to None
        if self.__HashTab1[hashVal1] and self.__HashTab1[hashVal1][0] == key:
            self.__HashTab1[hashVal1] = None 
            return key
        
        # check if it is in the second table and if it is, set its position to None 
        elif self.__HashTab2[hashVal2] and self.__HashTab2[hashVal2][0] == key:
            self.__HashTab2[hashVal2] = None
            return key 

        # if the key is not in the table, then do nothing
        else:
            return False 
            
    def __len__(self):
        return len(self.__HashTab1) 
    
    def __str__(self):
        ans1 = '{'
        ans2 = '{'
        for l in range(len(self.__HashTab1)):
            if self.__HashTab1[l]: 
                ans1 += str(self.__HashTab1[l][0]) + ":" + str(self.__HashTab1[l][1]) + ","
        for l in range(len(self.__HashTab2)):        
            if self.__HashTab2[l]:                 
                ans2 += str(self.__HashTab2[l][0]) + ":" + str(self.__HashTab2[l][1]) + ","
                 
        ans1 += '}'    
        ans2 += '}'    
        
        return ans1 + ans2
  
  
#TEST CODE:
  
# create a fake hash class that is just a dictionary  
class FakeHash(object): 
    
    def __init__(self):
        self.__hash = {}
    
    def insert(self, key, data):
        
        # only insert the key, data if it was not already inserted
        if key in self.__hash: return False
        self.__hash[key] = data 
        return key, data 
   
    def __len__(self):
        return len(self.__hash)
    
    def find(self, key): 
        if key in self.__hash: 
            return self.__hash[key]   
    
    def keys(self): return self.__hash.keys()
    
    def delete(self, key):
        if key in self.__hash: 
            self.__hash[key] = None

# check that insert and find work with few inserts                
def test_manualInsertSmall(): 
    c = CuckooHash(5)
    c.insert('hi','a')
    c.insert('my','b') 
    c.insert('name','c') 
    c.insert('hi', 's')
    assert c.find('hi') == 'a'
    assert c.find('my') == 'b'
    assert c.find('name') == 'c'
    
# check that insert and find work with few more inserts - this really checks
# that the proper thing is done when there are collisions and when it needs to grow
def test_manualInsertBig():
    c = CuckooHash(5)
    c.insert('a', 1)
    assert c.find('a') == 1
    c.insert('b', 2)
    assert c.find('b') == 2  
    c.insert('c', 3)
    assert c.find('c') == 3
    c.insert('d', 4)
    assert c.find('d') == 4    
    c.insert('e', 5)
    assert c.find('e') == 5
    c.insert('f', 6)
    assert c.find('f') == 6    
    c.insert('g', 7)
    assert c.find('g') == 7
    c.insert('h', 8)
    assert c.find('h') == 8    
    c.insert('i', 9)    
    assert c.find('i') == 9
    c.insert('j', 10)    
    assert c.find('j') == 10   
    c.insert('k', 11)
    assert c.find('k') == 11
    c.insert('l', 12)
    assert c.find('l') == 12   
    
# check that insert works with a small hash table - this really tests growHash
def test_small():
    c = CuckooHash(5)
    d = FakeHash()
    
    # insert the key, data pair into the real hash table and the fake on 
    for i in range(20):
        a = str(random.randint(1, 100))
        b = str(random.randint(1, 100)) 
        c.insert(a,b) 
        d.insert(a,b)
        assert c.find(a) == d.find(a)
    
    # check that it is in both     
    for i in d.keys():
        assert c.find(i) == d.find(i)

# check that insert works with a medium-sized hash table 
def test_medium():
    c = CuckooHash(20)
    d = FakeHash()
    
    for i in range(100):
        a = str(random.randint(1, 200))
        b = str(random.randint(1, 200)) 
        c.insert(a,b) 
        d.insert(a,b)
        assert c.find(a) == d.find(a)
   
    for i in d.keys():
        assert c.find(i) == d.find(i)

# check that insert works with a big hash table 
def test_big():
    c = CuckooHash(50)
    d = FakeHash()
   
    for i in range(1000):
        a = str(random.randint(1, 500))
        b = str(random.randint(1, 500)) 
        c.insert(a,b) 
        d.insert(a,b)
        assert c.find(a) == d.find(a)
   
    for i in d.keys():
        assert c.find(i) == d.find(i)

# check that insert works with a very big hash table 
def test_veryBig():
    c = CuckooHash(50)
    d = FakeHash()
   
    for i in range(100000):
        a = str(random.randint(1, 5000))
        b = str(random.randint(1, 5000)) 
        c.insert(a,b) 
        d.insert(a,b)
        assert c.find(a) == d.find(a)
   
    for i in d.keys():
        assert c.find(i) == d.find(i)
        
# test that delete works with few inserts 
def test_deleteSmall():
    c = CuckooHash(5)
    c.insert('hi','a')
    c.insert('my','b') 
    c.insert('name','b') 
    c.insert('hi', 's')
    assert c.find('name') == 'b'
    c.delete('name')
    assert not c.find('name')
    
# test that deleting a key that is not in the table return False
def test_deleteNotThere():
    c = CuckooHash(5)
    c.insert('hi','a')
    c.insert('my','b') 
    c.insert('name','b') 
    c.insert('hi', 's')
    assert not c.delete('no')

# test that delete works with many inserts and deletions
def test_deleteBig():
    c = CuckooHash(50)
    d = FakeHash()
    
    for i in range(1000):
        c.insert(i,str(i)) 
        d.insert(i,str(i))
   
    for i in d.keys():
        assert c.find(i) == d.find(i)    
   
    # go through and delete every 20th key
    for i in range(9999, -1, -20):
        c.delete(i)
        assert not c.find(i)
pytest.main(["-v", "-s", "CuckooHashHW.py"])  