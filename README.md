# Kitsu Tracker for Stremio

A fully serverless Stremio addon that seamlessly synchronizes your anime watch progress with your Kitsu account in the background.

##  Features
* **Auto-Tracking:** Automatically updates your Kitsu episode progress the moment you start watching a stream in Stremio.
* **Catalog Sync:** Brings your personal Kitsu lists (`Currently Watching`, `Plan to Watch`, `Completed`, `On Hold`, `Dropped`) directly to your Stremio board.
* **Dynamic Configuration:** Adjust which lists are visible in Stremio at any time through the web interface, without needing to reinstall the addon.
* **Serverless Ready:** Built with Quart and optimized for Vercel deployment with MongoDB Atlas.

## ☕ Support
If this addon makes your anime tracking easier, consider supporting the project!

<a href="https://ko-fi.com/mralanbourne" target="_blank"><img src="https://storage.ko-fi.com/cdn/kofi2.png?v=3" height="36" alt="Buy Me a Coffee at ko-fi.com" /></a>

## 🛠 Self-Hosting (Optional)
This addon is designed to be hosted on Vercel (free tier). 
1. Clone the repository
2. Set up a free MongoDB Atlas Cluster
3. Add the `MONGO_URI` variable to your Vercel Environment Variables
4. Deploy using `vercel.json`