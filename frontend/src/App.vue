<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
// REMOVED: No longer need to import the datepicker
// import Datepicker from 'vue-datepicker-next';
// import 'vue-datepicker-next/index.css';

// --- State Management ---
const accounts = ref([]);
const posts = ref([]);
const isLoading = ref(true);
const newAccountUsername = ref('');
const newAccountPassword = ref('');
const verifyingId = ref(null);
const postContent = ref('');
const scheduledAt = ref(null);
const isPosting = ref(false);

const API_BASE_URL = 'http://127.0.0.1:8001';

// --- Helper Functions ---
const formatStatusClass = (status) => {
  if (!status) return '';
  return status.toLowerCase().replace(/[\s/]+/g, '-');
};

// --- Account Functions ---
const fetchAccounts = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/accounts/`);
    accounts.value = response.data;
  } catch(e) {
    console.error("Failed to fetch accounts", e);
  } finally {
     isLoading.value = false;
  }
};

const addAccount = async () => {
  if (!newAccountUsername.value || !newAccountPassword.value) {
    alert('Please enter both a username and a password.');
    return;
  }
  try {
    await axios.post(`${API_BASE_URL}/accounts/`, {
      username: newAccountUsername.value,
      password: newAccountPassword.value
    });
    newAccountUsername.value = '';
    newAccountPassword.value = '';
    await fetchAccounts(); 
  } catch (err) {
    alert('Failed to add account. The username might already exist.');
    console.error(err);
  }
};

const deleteAccount = async (accountId) => {
  if (confirm('Are you sure you want to delete this account?')) {
    try {
      await axios.delete(`${API_BASE_URL}/accounts/${accountId}`);
      await fetchAccounts();
    } catch (err) {
      alert('Failed to delete account.');
      console.error(err);
    }
  }
};

const verifyAccount = async (accountId) => {
  verifyingId.value = accountId;
  try {
    await axios.post(`${API_BASE_URL}/accounts/${accountId}/verify`);
    await fetchAccounts();
  } catch (err) {
    alert('Verification failed. Check the backend console for errors.');
  } finally {
    verifyingId.value = null;
  }
};

// --- Post Functions ---
const fetchPosts = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/posts/`);
    posts.value = response.data;
  } catch(e) {
    console.error("Failed to fetch posts", e);
  }
};

const schedulePost = async () => {
  if (!postContent.value.trim()) {
    alert('Please write something to post.');
    return;
  }
  isPosting.value = true;
  try {
    await axios.post(`${API_BASE_URL}/posts/`, {
      content: postContent.value,
      scheduled_at: scheduledAt.value
    });
    postContent.value = '';
    scheduledAt.value = null;
    await fetchPosts();
  } catch (e) {
    alert('Failed to schedule post.');
    console.error(e);
  } finally {
    isPosting.value = false;
  }
};

// --- Lifecycle Hook ---
onMounted(() => {
  fetchAccounts();
  fetchPosts();
});
</script>

<template>
  <main class="container">
    <h1>Account Dashboard</h1>
    
    <article>
      <header><strong>Schedule a New Post</strong></header>
      <textarea v-model="postContent" placeholder="What's on your mind?"></textarea>
      <label for="schedule-time">
        Schedule for later (optional)
        <input v-model="scheduledAt" type="datetime-local" id="schedule-time" />
      </label>
      
      <button @click="schedulePost" :disabled="isPosting" style="margin-top: 1rem;">
        {{ isPosting ? 'Scheduling...' : 'Schedule Post' }}
      </button>
    </article>

    <h2>Managed Accounts</h2>
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Username</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="account in accounts" :key="account.id">
          <td>{{ account.id }}</td>
          <td>{{ account.username }}</td>
          <td>
            <span :class="['status', formatStatusClass(account.status)]">
              {{ account.status }}
            </span>
          </td>
          <td>
            <button @click="verifyAccount(account.id)" :disabled="verifyingId === account.id || isPosting">
              {{ verifyingId === account.id ? 'Verifying...' : 'Verify' }}
            </button>
            <button @click="deleteAccount(account.id)" class="secondary" :disabled="isPosting">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>

    <h2>Scheduled & Past Posts</h2>
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Content</th>
          <th>Scheduled At</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="post in posts" :key="post.id">
          <td>{{ post.id }}</td>
          <td>{{ post.content.substring(0, 50) }}...</td>
          <td>{{ post.scheduled_at ? new Date(post.scheduled_at).toLocaleString() : 'Immediate' }}</td>
          <td>{{ post.status }}</td>
        </tr>
      </tbody>
    </table>
  </main>
</template>

<style scoped>
/* All styles remain the same */
.container {
  max-width: 960px;
  margin: 2rem auto;
  padding: 1rem;
}
.status {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  color: white;
  background-color: #757575; /* Default grey for 'active' */
}
.status.success { background-color: #4caf50; /* Green */ }
.status.login-failed-checkpoint { background-color: #f44336; /* Red */ }
.status.posting, .status.api-error { background-color: #ff9800; /* Orange */ }
.status.post-successful { background-color: #2196f3; /* Blue */ }
.status.post-failed { background-color: #f44336; /* Red */ }
textarea {
  width: 100%;
  resize: vertical;
  margin-bottom: 1rem;
}
</style>