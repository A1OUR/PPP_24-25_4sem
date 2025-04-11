def main():
    try:
        from audio_client import run_client
        run_client()
    except ConnectionRefusedError:
        from audio_server import run_server
        run_server()
    pass

if __name__ == "__main__":
    main()

