<p align="center">
  <img src="https://kitsu.io/kitsu-256-ed442f7567271af715884ca3080e8240.png" width="80" alt="Kitsu Logo">
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
</div>

---

### ✨ Features
* **⚡ Auto-Tracking:** Your progress updates automatically in the background while you watch.
* **📂 Kitsu Catalogs:** Browse your personal lists (Watching, Planned, etc.) directly as Stremio catalogs.
* **🛠 Dynamic Config:** Enable or disable lists via the dashboard—no reinstallation needed.
* **☁️ Privacy First:** Your password is never stored. We use secure one-time tokens for API access.

### 🦊 Quick Start
1. **Login:** Open the **[Community Instance](https://kitsu-stremio-addon.vercel.app)** and sign in with Kitsu.
2. **Setup:** Choose your catalogs and click **Save**.
3. **Install:** Use the **Install** button to add it to your Stremio client.

> [!IMPORTANT]
> **Syncing Note:** Stremio caches catalogs aggressively. It can take **up to 5 minutes** for list changes (e.g., moving to "Completed") to visually appear, but your watch progress is saved instantly! 😘

---

### ☕ Support
If you find this service useful, consider supporting the instance to keep it running smoothly!

<a href="https://ko-fi.com/mralanbourne" target="_blank">
  <img src="https://storage.ko-fi.com/cdn/kofi2.png?v=3" height="40" alt="Buy Me a Coffee at ko-fi.com" />
</a>

---

<details>
<summary>💻 <strong>Self-Hosting Instructions (Developers)</strong></summary>

### How to host your own instance
1. **Clone the Repo:** `git clone https://github.com/mralanbourne/kitsu-stremio-addon.git`
2. **Setup MongoDB:** Create a free cluster on [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
3. **Deploy to Vercel:**
   - Connect your GitHub account to Vercel.
   - Import this repository.
   - **Important:** Add the following Environment Variables in Vercel settings:

| Variable | Description |
| :--- | :--- |
| `MONGO_URI` | Your full MongoDB connection string |
| `SECRET_KEY` | A random long string for session encryption |
| (optional) `MONGO_DB` | Your database name (standard: `kitsu_db`) |
| (optional) `MONGO_UID_MAP_COLLECTION` | Collection name (standard: `users`) |

4. **Certificates:** This project uses `certifi` for secure connections. The configuration is already set in `app/services/db.py`.

</details>

<p align="center">Made with ❤️ for the Anime Community.</p>
