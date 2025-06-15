import os
import time
import requests


def download_faces(num_images: int, output_folder: str = "images"):
    os.makedirs(output_folder, exist_ok=True)

    for i in range(1, num_images + 1):
        try:
            response = requests.get(
                "https://thispersondoesnotexist.com",
                headers={
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
                                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                                  "Chrome/88.0.4324.96 Safari/537.36"
                },
                timeout=10
            )
            if response.status_code == 200:
                filename = os.path.join(output_folder, f"image_{i+200:03d}.jpg")
                with open(filename, "wb") as f:
                    f.write(response.content)
                print(f"[{i}/{num_images}] Zapisano: {filename}")
            else:
                print(f"[{i}/{num_images}] Błąd HTTP: {response.status_code}")
        except Exception as e:
            print(f"[{i}/{num_images}] Wyjątek podczas pobierania: {e}")

        time.sleep(0.5)

if __name__ == "__main__":
    download_faces(num_images=500, output_folder="all")
