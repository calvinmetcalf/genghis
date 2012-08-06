import sqlite3,os,couchdbkit,base64,json,zlib

def flip_y(zoom, y):
    return (2**zoom-1) - y

def makeBin(x,z):
    bx = bin(x)
    bx = bx[2:]
    while len(bx)<z:
        bx="0"+bx
    return bx
    
def get(indb,outdb):
    sdb = sqlite3.connect(indb)
    server = couchdbkit.Server()
    db = server.create_db(outdb)
    show = {"_id":"_design/m","shows":{"tile":"function(doc, req) {return {base64 :doc.tile,headers : {'Content-Type' :'image/png'}  };}","grid":"function(doc, req) {return {body :doc.grid,headers : {'Content-Type' :'application/json'}  };}"}}
    metadata = dict(con.execute('select name, value from metadata;').fetchall())
    metadata["_id"]="metadata"
    db.save_docs([show,metadata])
    tiles = sdb.execute('select zoom_level, tile_column, tile_row, tile_data from tiles;')
    d= getGrids(db)
    docs=[]
    t=tiles.fetchone()
    while t:
        z = t[0]
        x = t[1]
        y1 = t[2]
        y = flip_y(z,y1)
        bx = makeBin(x,z)
        by = makeBin(y,z)
        tab = dict({"0":{"0":"a","1":"b"},"1":{"0":"c","1":"d"}})
        r=""
        for i in range(z):
            r = r+tab[bx[i]][by[i]]
        j = getJSON(sdb,z,y1,x,d)
        doc={'_id':r,'z':z,'x':x,'y':y,grid:j,'tile':base64.b64encode(t[3])}
        docs.append(doc)
        if len(docs)>500:
            db.save_docs(docs)
            docs=[]
        t = tiles.fetchone()

def getJSON(db,z,y,x,d):
    grids = db.execute('select grid from grids where zoom_level=:z and tile_column =:x and tile_row=:y',{"z":z,"x":x,"y":y}).fetchone()
    jd= json.loads(zlib.decompress(grids[0]))
    jd["data"]=d
    return json.dumps(jd)
    

def getGrids(db):
    gdc = db.execute('select key_name, key_json FROM grid_data)
    gd=gdc.fetchone()
    data={}
    while gd:
        data[gd[0]]=json.loads(gd[1])
        gd=gdc.fetchone()
    return data