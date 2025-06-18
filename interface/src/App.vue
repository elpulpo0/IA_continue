<template>
  <div class="app">

    <div v-if="!accessToken">
      <h2>Connexion</h2>
      <input v-model="email" placeholder="Email" type="email" />
      <input v-model="password" placeholder="Mot de passe" type="password" />
      <button @click="login">Se connecter</button>
      <p v-if="errorMsg" style="color:red">{{ errorMsg }}</p>
    </div>

    <div v-else>
      <h2>Actions</h2>
      <button @click="getCurrentUser">Afficher mon profil</button>
      <button @click="getAllUsers">Afficher tous les utilisateurs (admin)</button>
      <button @click="doRefreshToken">Rafraîchir token</button>
      <button @click="logout">Déconnexion</button>

      <h3>Services API</h3>
      <button @click="checkHealth">Vérifier la santé du service (/health)</button>
      <button @click="generateDataset">Générer un dataset (/generate)</button>
      <button @click="retrainModel">Réentraîner le modèle (/retrain)</button>
      <button @click="predict">Prédire (/predict)</button>

      <pre>{{ response }}</pre>
      <p v-if="errorMsg" style="color:red">{{ errorMsg }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import axios from "axios";

const FASTAPI_URL = import.meta.env.VITE_FASTAPI_URL || "http://localhost:8069";
const USERS_URL = import.meta.env.VITE_USERS_URL || "http://localhost:8099";

const email = ref("");
const password = ref("");
const accessToken = ref(localStorage.getItem("access_token") || null);
const refreshToken = ref(localStorage.getItem("refresh_token") || null);
const response = ref("");
const errorMsg = ref("");

function saveTokens(tokens) {
  accessToken.value = tokens.access_token;
  refreshToken.value = tokens.refresh_token;
  localStorage.setItem("access_token", tokens.access_token);
  localStorage.setItem("refresh_token", tokens.refresh_token);
}

async function login() {
  errorMsg.value = "";
  try {
    const data = new URLSearchParams();
    data.append("username", email.value);
    data.append("password", password.value);

    const res = await axios.post(`${USERS_URL}/auth/login`, data);
    saveTokens(res.data);
    response.value = "Connexion réussie !";
  } catch (err) {
    errorMsg.value = `Erreur de connexion : ${err.response?.data?.detail || err.message}`;
  }
}

function logout() {
  accessToken.value = null;
  refreshToken.value = null;
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  response.value = "Déconnecté";
}

async function getCurrentUser() {
  errorMsg.value = "";
  try {
    const res = await axios.get(`${USERS_URL}/users/users/me`, {
      headers: { Authorization: `Bearer ${accessToken.value}` },
    });
    response.value = JSON.stringify(res.data, null, 2);
  } catch (err) {
    errorMsg.value = `Erreur: ${err.response?.status} ${err.response?.data || err.message}`;
  }
}

async function getAllUsers() {
  errorMsg.value = "";
  try {
    const res = await axios.get(`${USERS_URL}/users/users`, {
      headers: { Authorization: `Bearer ${accessToken.value}` },
    });
    response.value = JSON.stringify(res.data, null, 2);
  } catch (err) {
    errorMsg.value = `Erreur: ${err.response?.status} ${err.response?.data || err.message}`;
  }
}

async function doRefreshToken() {
  errorMsg.value = "";
  try {
    const res = await axios.post(`${USERS_URL}/auth/refresh`, null, {
      headers: { Authorization: `Bearer ${refreshToken.value}` },
    });
    saveTokens(res.data);
    response.value = "Token rafraîchi";
  } catch (err) {
    errorMsg.value = "Erreur de rafraîchissement";
  }
}

async function checkHealth() {
  errorMsg.value = "";
  try {
    const res = await axios.get(`${FASTAPI_URL}/health`);
    response.value = `Service OK: ${JSON.stringify(res.data)}`;
  } catch (err) {
    errorMsg.value = `Erreur connexion: ${err.message}`;
  }
}

async function generateDataset() {
  errorMsg.value = "";
  try {
    const res = await axios.post(`${FASTAPI_URL}/generate`);
    response.value = res.data.message;
  } catch (err) {
    errorMsg.value = `Erreur: ${err.response?.status} ${err.response?.data || err.message}`;
  }
}

async function retrainModel() {
  errorMsg.value = "";
  try {
    const res = await axios.post(`${FASTAPI_URL}/retrain`);
    response.value = res.data.message;
  } catch (err) {
    errorMsg.value = `Erreur: ${err.response?.status} ${err.response?.data || err.message}`;
  }
}

async function predict() {
  errorMsg.value = "";
  try {
    const res = await axios.get(`${FASTAPI_URL}/predict`);
    response.value = `Prédiction: ${res.data.prediction}`;
  } catch (err) {
    errorMsg.value = `Erreur: ${err.response?.status} ${err.response?.data || err.message}`;
  }
}
</script>

<style>
.app {
  max-width: 600px;
  margin: auto;
  background-color: #000; /* fond noir */
  color: #00ff00; /* vert néon */
  font-family: 'Courier New', Courier, monospace; /* monospace rétro */
  padding: 20px;
  border: 3px solid #00ff00;
  box-shadow:
    0 0 10px #00ff00,
    inset 0 0 15px #00ff00;
  position: relative;
  user-select: none;
}

/* Effet scanlines */
.app::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  pointer-events: none;
  background: repeating-linear-gradient(
    0deg,
    rgba(0, 255, 0, 0.1) 0,
    rgba(0, 255, 0, 0.1) 1px,
    transparent 2px,
    transparent 4px
  );
  mix-blend-mode: screen;
  z-index: 10;
}

button {
  background: transparent;
  border: 1px solid #00ff00;
  color: #00ff00;
  padding: 6px 12px;
  margin: 5px 5px 5px 0;
  font-family: 'Courier New', Courier, monospace;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}

button:hover {
  background: #00ff00;
  color: #000;
}

input {
  background-color: #000;
  border: 1px solid #00ff00;
  color: #00ff00;
  font-family: 'Courier New', Courier, monospace;
  display: block;
  margin: 10px 0;
  padding: 8px;
  width: 100%;
  max-width: 300px;
  outline: none;
}

input::placeholder {
  color: #006600;
  font-style: italic;
}

pre {
  background-color: #000;
  border: 1px solid #00ff00;
  color: #00ff00;
  padding: 10px;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Courier New', Courier, monospace;
  box-shadow: inset 0 0 5px #00ff00;
  overflow-x: auto;
}
</style>
