// ============================================================
// CONFIGURACIÓN FIREBASE - ADMON SANTIANTZ
// ============================================================
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-firestore.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js";
import { getStorage } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-storage.js";

const firebaseConfig = {
  apiKey: "AIzaSyDXxnBBOQ4bnBSTJMBzLymBA3qPxtMne0o",
  authDomain: "admon-santiantz.firebaseapp.com",
  projectId: "admon-santiantz",
  storageBucket: "admon-santiantz.firebasestorage.app",
  messagingSenderId: "144865446825",
  appId: "1:144865446825:web:309c7779fbdb4ce6df92b8"
};

const app = initializeApp(firebaseConfig);
export const db = getFirestore(app);
export const auth = getAuth(app);
export const storage = getStorage(app);
export default app;
