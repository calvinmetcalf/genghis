import anydbm,hashlib,base64,sqlite3

def opendb(f):
    c = anydbm.open(f,"c")
    return c

def flip_y(zoom, y):
    return (2**zoom-1) - y

def makeBin(x,z):
    bx = bin(x)
    bx = bx[2:]
    while len(bx)<z:
    bx="0"+bx
    return bx

def get(indb, out):
    sdb = sqlite3.connect(indb)
    tdb = opendb(out+".tiles.db")
    hdb = opendb(out+".hash.db")
    tiles = sdb.execute('select zoom_level, tile_column, tile_row, tile_data from tiles;')
    t=tiles.fetchone()
    while t:
        z = t[0]
        x = t[1]
        y = t[2]
        y = flip_y(z,y)
        bh = base64.b64encode(hashlib.sha256(t[3]).digest())
        bx = makeBin(x,z)
        by = makeBin(y,z)
        tab = dict({"0":{"0":"a","1":"b"},"1":{"0":"c","1":"d"}})
        r=""
        for i in range(z):
            r = r+tab[bx[i]][by[i]]
        hdb[bh]=t[3]
        tdb[r]=bh
        t = tiles.fetchone()
    sdb.close()
    tdb.close()
    hdb.close()