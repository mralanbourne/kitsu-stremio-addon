<p align="center">
  <img src="https://raw.githubusercontent.com/mralanbourne/kitsu-stremio-addon/main/static/fox.png" width="300" alt="Kitsu Logo">
</p>

<h1 align="center">Kitsu Tracker for Stremio</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Stremio-Addon-8a5a9e?style=for-the-badge&logo=stremio" alt="Stremio Addon">
  <img src="https://img.shields.io/badge/Status-Online-success?style=for-the-badge" alt="Status Online">
  <img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="License MIT">
</p>

<p align="center">
  <strong>The fully fledged bridge between Stremio and Kitsu. Sync your progress automatically without lifting a finger.</strong>
</p>

<div align="center">
  <h3>🌐 Community Instance</h3>
  <a href="https://kitsu-stremio-addon.vercel.app">kitsu-stremio-addon.vercel.app</a>
  <br />
  <br />
  <a href="https://kitsu-stremio-addon.vercel.app">
    <img src="https://img.shields.io/badge/INSTALL_NOW-CLICK_HERE-FD755C?style=for-the-badge&logo=rocket" alt="Install Button" height="55">
  </a>
</div>

---

> [!WARNING]
> ### 🔒 Privacy & Security Notice
> Kitsu currently lacks standard OAuth2 for third-party apps, meaning you need to log in directly via this interface. I take your data security very seriously:
>
> * **Zero Password Storage:** Your password is strictly used **once** to generate a secure Kitsu access token. It is never stored in the database or logged anywhere.
> * **Encrypted Client Sessions:** Your active session is cryptographically signed and stored locally in your browser's cookies. The server does not keep your session in its memory.
> * **Minimal Data:** I only store your Kitsu ID, the generated tokens, and your watch progress to make the sync work.
> * **100% Open Source:** Don't trust, verify! The entire architecture is public.

### ✨ Features
* **⚡ Auto-Tracking:** Your episode progress updates automatically on Kitsu in the background the moment you press play.
* **🔍 Native Kitsu Search:** Search for anime directly through the addon. This ensures Stremio uses proper `kitsu:` IDs, allowing brand new shows to be auto-added to your "Watching" list automatically!
* **📂 Personal Catalogs:** Browse your Kitsu lists (Watching, Planned, Completed, etc.) directly as native Stremio rows.
* **🚀 High Performance:** Powered by a fully asynchronous serverless engine with smart Edge-Caching for lightning-fast catalog loading.

### 🦊 Quick Start
1. **Login:** Open the **[Community Instance](https://kitsu-stremio-addon.vercel.app)** and sign in with your Kitsu account.
2. **Setup:** Choose which catalogs you want to see in Stremio and click **Save**.
3. **Install:** Use the **Install** buttons provided on the dashboard to add the addon to your Stremio client.

> [!IMPORTANT]
> **Tracking New Anime:** To ensure a completely new anime is added to your Kitsu list automatically, always search for it in Stremio and select the result under the **"Kitsu: Search"** category (not the default Cinemeta result).
> 
> **Syncing Note:** Stremio caches catalogs aggressively. It can take **up to 5 minutes** for list changes (like moving a show to "Completed") to visually update on your home screen. However, your actual watch progress on the Kitsu servers is saved instantly! 😘

---

<details>
<summary>💻 <strong>Self-Hosting Instructions (Developers)</strong></summary>

### How to host your own instance
If you prefer to have absolute control over your credentials and the code, you can easily host this yourself for free.

1. **Clone the Repo:** `git clone https://github.com/mralanbourne/kitsu-stremio-addon.git`
2. **Setup MongoDB:** Create a free cluster on [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
3. **Deploy to Vercel:**
   - Connect your GitHub account to Vercel.
   - Import this repository.
   - **Important:** Add the following Environment Variables in Vercel settings:

| Variable | Description |
| :--- | :--- |
| `MONGO_URI` | Your full MongoDB connection string |
| `SECRET_KEY` | A random long string for secure cookie encryption |
| (optional) `MONGO_DB` | Your database name (standard: `kitsu_db`) |
| (optional) `MONGO_UID_MAP_COLLECTION` | Collection name (standard: `users`) |

4. **Certificates:** This project uses `certifi` for secure connections. The configuration is already set in `app/services/db.py`.

</details>

---

### ☕ Support
I'm hosting this instance for free for the community. If you find this service useful, consider supporting the development to keep the server running as the user base grows!

<a href="https://ko-fi.com/mralanbourne" target="_blank">
  <img src="https://storage.ko-fi.com/cdn/kofi2.png?v=3" height="40" alt="Buy Me a Coffee at ko-fi.com" />
</a>

<br>

<p align="center">
  Made with ❤️ for the Anime Community.<br>
  <sub>Based on the architecture of <a href="https://github.com/SageTendo/mal-stremio-addon">MAL-Stremio Addon</a> by SageTendo.</sub>
</p>
