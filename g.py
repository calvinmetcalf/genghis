import sqlite3,os,couchdbkit,base64,json,zlib

def flip_y(zoom, y):
    return (2**zoom-1) - y

def makeBin(x,z):
    bx = bin(x)
    bx = bx[2:]
    while len(bx)<z:
        bx="0"+bx
    return bx

def quad(z,x,y):
    bx = makeBin(x,z)
    by = makeBin(y,z)
    tab = dict({"0":{"0":"a","1":"b"},"1":{"0":"c","1":"d"}})
    r=""
    if z==0:
        r="z"
    else:
        for i in range(z):
            r = r+tab[bx[i]][by[i]]
    return r
    
def up(indb,outdb):
    sdb = sqlite3.connect(indb)
    server = couchdbkit.Server()
    db = server.create_db(outdb)
    show = getShow()
    metadata = getMeta(sdb)
    db.save_docs([show,metadata])
    d= getGrids(sdb)
    tiles = sdb.execute('select zoom_level, tile_column, tile_row, tile_data from tiles;')
    docs=[]
    t=tiles.fetchone()
    while t:
        z = t[0]
        x = t[1]
        y1 = t[2]
        y = flip_y(z,y1)
        r=quad(z,x,y)
        doc={'_id':r,'z':z,'x':x,'y':y,'tile':base64.b64encode(t[3])}
        if d:
            j = getJSON(sdb,z,x,y1,d)
            doc["grid"]=j
        docs.append(doc)
        t = tiles.fetchone()
    db.save_docs(docs)

def getJSON(db,z,x,y,d):
    grids = db.execute('select grid from grids where zoom_level=:z and tile_column =:x and tile_row=:y',{"z":z,"x":x,"y":y}).fetchone()
    jd= json.loads(zlib.decompress(grids[0]))
    data={}
    for k in jd["keys"]:
        if k:
            data[k]=d[k]
    jd["data"]=data
    return json.dumps(jd)

def getGrids(db):
    data = dict(db.execute('select key_name, key_json FROM grid_data').fetchall())
    return data

def getShow():
    s={}
    s["_id"]="_design/m"
    s["shows"]={}
    s["shows"]["tile"]="function(doc, req) {if(doc&&doc.tile){return {base64 :doc.tile,headers : {'Content-Type' :'image/png'}} }else{return {base64 :'iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACAYAAABccqhmAAADGUlEQVR4nO3UMQEAAAiAMPuX1hgebAm4mAWy5jsA+GMAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEHbmUDvFpM58qAAAAABJRU5ErkJggg==',headers : {'Content-Type' :'image/png'}}};}"
    s["shows"]["grid"]="function(doc, req) {if(doc&&doc.grid){return {body :doc.grid,headers : {'Content-Type' :'application/json'}}  }else{return {body :{},headers : {'Content-Type' :'application/json'}}  };}"
    return s
    
def getMeta(db):
    m=dict(db.execute('select name, value from metadata;').fetchall())
    m["_id"]="metadata"
    return m