importScripts("https://www.gstatic.com/firebasejs/10.7.0/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.7.0/firebase-messaging-compat.js");

firebase.initializeApp({
  apiKey: "AIzaSyByFNMa9xghopKLflgEgD67A5gYGkZ4rs4",
  authDomain: "eatk-f225e.firebaseapp.com",
  projectId: "eatk-f225e",
  storageBucket: "eatk-f225e.firebasestorage.app",
  messagingSenderId: "317346321742",
  appId: "1:317346321742:web:a425d10d6ad27ce690fa1f",
  measurementId: "G-D59BCV931P"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
  console.log("Background message received:", payload);
});