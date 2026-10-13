"""
Demonstration runner showing how an edge worker registers its dynamic tunnel URL.
"""

from tunnel_manager import ResilientTunnelManager

def main():
    manager = ResilientTunnelManager(local_port=8080)
    print("Starting Resilient Tunnel Manager...")
    try:
        url, provider = manager.start_tunnel()
        print(f"-> Active Tunnel URL : {url}")
        print(f"-> Active Provider   : {provider}")
        print("Ready to publish registration packet to MQTT control plane...")
    finally:
        manager.terminate()
        print("Tunnel shut down cleanly.")

if __name__ == "__main__":
    main()