const CACHE_NAME = 'cuerpo-bomberos-v1';
const urlsToCache = [
  '/',
  './static/styles.css',
  '/static/js/pwa/manifest.json',
  'https://i.postimg.cc/CLr88W67/29.png',
  'https://i.postimg.cc/52ZF78JF/40.png',
  'https://i.postimg.cc/63K4wwyW/58.png',
  'https://i.postimg.cc/NGp2h3Yt/60.png',
  'https://i.postimg.cc/15Xnyv5q/80.png',
  'https://i.postimg.cc/X7PZq9pD/87.png',
  'https://i.postimg.cc/GpF9XNzZ/114.png',
  'https://i.postimg.cc/DZ50TX96/120.png',
  'https://i.postimg.cc/90nf4jFq/180.png',
  'https://i.postimg.cc/44Ly2pbN/1024.png'
];

// Instalación del Service Worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

// Intercepta las solicitudes y devuelve las respuestas en caché
self.addEventListener('fetch', event => {
  if (event.request.url.startsWith('http')) { // Solo manejar solicitudes HTTP(S)
    event.respondWith(
      caches.match(event.request)
        .then(response => {
          if (response) {
            return response;
          }
          return fetch(event.request).then(
            response => {
              if (!response || response.status !== 200 || response.type !== 'basic') {
                return response;
              }
              const responseToCache = response.clone();
              caches.open(CACHE_NAME)
                .then(cache => {
                  cache.put(event.request, responseToCache);
                });
              return response;
            }
          );
        })
    );
  }
});

// Limpieza de caché y actualización del Service Worker
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (!cacheWhitelist.includes(cacheName)) {
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      return self.clients.claim();
    })
  );
});
