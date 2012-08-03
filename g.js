var crypto = require('crypto');

function hashfile(file,cb){

var s = crypto.createHash('sha256');
    s.update(file);
    var d = s.digest('base64');
 cb(false,d,file);
 
}
exports.h=hashfile;

function quad(z,x,y){
var bx = x.toString(2);
var by = y.toString(2);
while(bx.length<z){
bx = '0'+bx;
}
while(by.length<z){
by = '0'+by;
}
var i = 0;
var tab={"0":{"0":"a","1":"b"},"1":{"0":"c","1":"d"}};
var r =[];

while(i<z){
r.push(tab[bx[i]][by[i]]);
i++;
}
return r.join('');
}
exports.q=quad;

function xyz(q){
 var z =q.length;
 var vx = [];
 var vy=[];
 var i = 0;
 while(i<z){
     var a =q[i];
     var tab ={
      a:{x:"0",y:"0"},
      b:{x:"0",y:"1"},
      c:{x:"1",y:"0"},
      d:{x:"1",y:"1"}
     };
     vx.push(tab[a].x);
     vy.push(tab[a].y);
     i++;
 }
  var bx=vx.join("");
     var by=vy.join("");
     var x = parseInt(bx,2);
     var y = parseInt(by,2);
     return [z,x,y];
}
exports.i = xyz;
//for now, just use some objects
var bases ={};
bases.h={};

bases.h.obj=function(){
    var _this=this;
 
        function addHash(h,f){
            if(_this[h]){
             _this[h].n+=1;   
            }else{
             _this[h]={file:f,n:1};
            }
        }
        function rmHash(h){
         if(_this[h]){
          if(_this[h].n===1){
           delete _this[h];   
          }else if(_this[h].n>1){
           _this[h].n-=1;   
          }
         }
        }
        function getTile(h,cb){
         if(_this[h]){
             if(cb){
                 cb(false,_this[h].f);
            }else{return _this[h].f;}  
         }else  {
             if(cb){cb(true);}else{return false;}  
         }
        }
_this.add=addHash;
_this.rm=rmHash;
_this.get=getTile;
return _this;
};

function hashBase(type){
    type = type||"obj";
   
        return new bases.h[type]();   
    
}
bases.t={};

bases.t.obj=function(h){
    var _this=this;
    _this.l={};
    var xyz={};
    xyz.addTile = function(z,x,y,f){
        addTile(quad(z,x,y),f);
    };
    function addTile(q,f){
        
        
        hashfile(f,function(e,hash){
           
           if(_this.l[q]){
               if(_this.l[q]!==hash){
                   h.rm(hash);
                   h.add(hash,f);
                   _this.l[q]=hash;
               }}
           else{
               h.add(hash,f);
               _this.l[q]=hash;
           }
        });
       
    }
    xyz.rmTile=function (z,x,y){
     return rmTile(quad(z,x,y));
    };
    function rmTile(q){
     
        if(_this.l[q]){
         h.rm(_this.l[q]);
         delete _this.l[q];
         return true;
        }else{return false;}
    }
    xyz.getTile=function(z,x,y,cb){
     if(cb){
      getTile(quad(z,x,y),cb);
     }else{
      return getTile(quad(z,x,y));
     }
        
    };
    function getTile(q,cb){
      
        if(cb){
         h.get(_this.l[q],cb);
        }else{
         return h.get(_this.l[q]);
        }
    }
    xyz.getHash= function(z,x,y,cb){
        if(cb){
      getHash(quad(z,x,y),cb);
     }else{
      return getHash(quad(z,x,y));
     }
        
    };
    function getHash(q,cb){
       
        if(_this.l[q]){
            if(cb){cb(false,_this.l[q]);}
         return _this.l[q];   
        }else{if(cb){cb(true);}else{return false;}}
        
    }
    
_this.add=addTile;
_this.rm=rmTile;
_this.get=getTile;
_this.getHash=getHash;
_this.xyz=xyz;
return _this;    
};
function tileBase(h,type){
     type = type||"obj";
 
        return new bases.t[type](h);   
  
    };
exports.t=tileBase;
exports.h=hashBase;
