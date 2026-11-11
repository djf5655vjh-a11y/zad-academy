const CACHE="zad-academy-shell-v1";
self.addEventListener("install",e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(["/","/static/style.css","/static/app.js","/static/manifest.json"]))));
self.addEventListener("fetch",e=>{
 if(e.request.method!=="GET") return;
 e.respondWith(caches.match(e.request).then(cached=>cached||fetch(e.request).then(res=>{
  const copy=res.clone(); if(new URL(e.request.url).origin===location.origin) caches.open(CACHE).then(c=>c.put(e.request,copy)); return res;
 }).catch(()=>cached)));
});
