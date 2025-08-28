import sys, requests
from node.server import create_app

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
    my_address = f"http://localhost:{port}"

    app = create_app(difficulty=4)       # atau baca dari env/arg
    peers = app.config["peers"]

    # bootstrap ke node 5001 (kalau bukan bootstrap)
    if port != 5001:
        try:
            resp = requests.post("http://localhost:5001/register_node",
                                 json={"node": my_address}, timeout=3)
            if resp.ok and "peers" in resp.json():
                for p in resp.json()["peers"]:
                    if p != my_address:
                        peers.add(p)
            # sync setelah daftar
            app.sync_chain()
        except Exception as e:
            print("Bootstrap failed:", e)

    app.run(host="0.0.0.0", port=port)
