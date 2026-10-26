const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const mime = {'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.ttf':'font/ttf'};
http.createServer((req,res)=>{
  const pathname = decodeURIComponent(new URL(req.url,'http://localhost').pathname);
  const file = path.resolve(root,'.'+(pathname==='/'?'/prototype/index.html':pathname));
  if (!file.startsWith(root+path.sep)) {res.writeHead(403);return res.end('Forbidden')}
  fs.readFile(file,(err,body)=>{
    if(err){res.writeHead(404);return res.end('Not found')}
    res.writeHead(200,{'Content-Type':mime[path.extname(file)]||'application/octet-stream','Cache-Control':'no-store'});
    res.end(body);
  });
}).listen(8765,'127.0.0.1',()=>console.log('Khonnai prototype: http://127.0.0.1:8765/'));
