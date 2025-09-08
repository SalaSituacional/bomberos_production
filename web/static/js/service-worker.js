// Este Service Worker no hace caching.
// Se registra y activa, pero no intercepta las solicitudes de red.

self.addEventListener('install', (event) => {
    console.info('Service Worker: Evento de instalación.');
    // No usamos `event.waitUntil` porque no hay cache para precargar.
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    console.info('Service Worker: Evento de activación.');
    // No hay cache para limpiar.
    event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (event) => {
    // Este `fetch` listener es vacío, lo que significa que
    // no interceptamos ni almacenamos en cache ninguna solicitud.
    // Todas las peticiones van directamente a la red.
    console.info('Service Worker: Petición de red detectada, se permite pasar.');
});