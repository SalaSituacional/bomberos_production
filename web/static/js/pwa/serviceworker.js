const CACHE_NAME = 'Cuerpo Bomberos V1';
const urlsToCache = [
  '/',
  '/static/styles.css',
  '/static/js/pwa/manifest.json',
  '/static/assets/icons/29.png',
  '/static/assets/icons/40.png',
  '/static/assets/icons/58.png',
  '/static/assets/icons/60.png',
  '/static/assets/icons/80.png',
  '/static/assets/icons/87.png',
  '/static/assets/icons/114.png',
  '/static/assets/icons/120.png',
  '/static/assets/icons/180.png',
  '/static/assets/icons/1024.png'
];

// Instalación del Service Worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        return cache.addAll(urlsToCache);
      })
  );
});

// Intercepta las solicitudes y devuelve las respuestas en caché
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          return response;
        }
        return fetch(event.request);
      })
  );
});

// Actualización del Service Worker
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
    })
  );
});