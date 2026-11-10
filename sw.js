"use strict";
/*
 * Clubhouse Player Door — service worker.
 *
 * Its job is installability plus a resilient shell, nothing more:
 *  - It caches ONLY this site's own same-origin shell files
 *    (the page, the manifest, the icons) under a versioned cache.
 *  - Cross-origin traffic — above all the Supabase league book's
 *    API/RPC calls — is passed straight through and NEVER cached.
 *    The Door always works live against the league book.
 *  - Navigations are network-first, so a fresh deploy wins; the
 *    cached shell is only a fallback when the network is gone.
 */
var CACHE_NAME = "clubhouse-door-shell-v11";
var SHELL_FILES = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./icon-192.png",
  "./icon-512.png",
  "./icon-maskable-512.png",
  "./apple-touch-icon.png"
];

self.addEventListener("install", function (event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function (cache) {
      return cache.addAll(SHELL_FILES);
    }).then(function () {
      return self.skipWaiting();
    })
  );
});

self.addEventListener("activate", function (event) {
  event.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.map(function (key) {
        if (key !== CACHE_NAME) return caches.delete(key);
        return null;
      }));
    }).then(function () {
      return self.clients.claim();
    })
  );
});

self.addEventListener("fetch", function (event) {
  var request = event.request;
  if (request.method !== "GET") return; // writes always go straight out

  var url = new URL(request.url);
  if (url.origin !== self.location.origin) return; // Supabase & fonts: pass through, never cache

  if (request.mode === "navigate") {
    // Network-first for the page itself; cache is only a fallback.
    event.respondWith(
      fetch(request).then(function (response) {
        var copy = response.clone();
        caches.open(CACHE_NAME).then(function (cache) {
          cache.put("./index.html", copy);
        });
        return response;
      }).catch(function () {
        return caches.match("./index.html");
      })
    );
    return;
  }

  // Same-origin shell assets: cache-first, then network (and cache it).
  event.respondWith(
    caches.match(request).then(function (cached) {
      if (cached) return cached;
      return fetch(request).then(function (response) {
        var copy = response.clone();
        caches.open(CACHE_NAME).then(function (cache) {
          cache.put(request, copy);
        });
        return response;
      });
    })
  );
});
