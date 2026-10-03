# random-scripts
Collect of random scripts written for various reasons

## Personal asset viewer

Run from the repository root with Python 3:

```sh
python3 -m http.server 4173
```

Open [http://localhost:4173/asset_viewer.html](http://localhost:4173/asset_viewer.html). The page loads React and Babel from public CDNs, so an internet connection is required. Account and goal data is saved in the browser's local storage.
