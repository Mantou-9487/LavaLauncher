import json
import shutil
from os import getenv, listdir, path, mkdir, rename, remove
from os.path import isdir
from typing import Any

import jdk
import requests
import yaml
from git import Repo, NoSuchPathError
from inquirer import text, confirm


def info(obj: Any):
    print(f"[\033[36mi\033[0m] {str(obj)}")


def warning(obj: Any):
    print(f"[\033[33m!\033[0m] {str(obj)}\n")


def success(obj: Any):
    print(f"[\033[32m+\033[0m] {str(obj)}\n")


def main():
    repo = clone_lava()

    update_lava(repo)

    fill_secrets()

    set_ports()

    setup_lava()

    get_java()

    get_lavalink()

    success("Setup complete!")


def clone_lava() -> Repo:
    """
    Clones lava from the git repo
    :return: The repo
    """
    try:
        repo = Repo("./lava")

    except NoSuchPathError:
        info("Cloning Lava...")

        repo = Repo.clone_from(
            getenv("git_repo", "https://github.com/Nat1anWasTaken/Lava.git"), "./lava", branch="master"
        )

    success("Lava cloned successfully!")

    return repo


def update_lava(repo: Repo):
    info("Updating Lava...")

    remote = repo.remote("origin")

    remote.pull()

    success("Lava updated successfully!")


def fill_secrets():
    if path.isfile(".env"):
        warning(".env file already exists, skipping...")

        return

    env_file = open(".env", "w", encoding="utf-8")

    env_file.truncate(0)

    info(".env file doesn't exists, creating one...")

    try:
        token = text("TOKEN")

        env_file.write(f"TOKEN={token}\n")

        if confirm("Do you want to enable Spotify support?"):
            spotify_client_id = text("Spotify Client ID")
            env_file.write(f"SPOTIFY_CLIENT_ID={spotify_client_id}\n")

            spotify_client_secret = text("Spotify Client Secret")
            env_file.write(f"SPOTIFY_CLIENT_SECRET={spotify_client_secret}\n")

        env_file.close()

    except KeyboardInterrupt:
        env_file.close()

        remove(".env")

        raise KeyboardInterrupt

    success(".env file created successfully!")

    return


def set_ports():
    if path.isfile("lava/configs/lavalink.json") and path.isfile("lavalink/application.yml"):
        warning("lavalink.json and application.yml file already exists, skipping...")

        return

    port = text(
        "Please enter the port for lavalink",
        default="2333",
        validate=lambda _, x: x.isdigit()
    )

    with open("configs/lavalink.json", "r+", encoding="utf-8") as f:
        data = json.load(f)

        data["nodes"][0]["port"] = int(port)

        f.truncate(0)

        f.seek(0)

        f.write(json.dumps(data, indent=4))

    with open("configs/application.yml", "r+", encoding="utf-8") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

        data["server"]["port"] = int(port)

        f.truncate(0)

        f.seek(0)

        f.write(yaml.dump(data, indent=4))

    success("Wrote port to lavalink.json and application.yml successfully!")

    return


def setup_lava():
    info("Setting up Lava...")

    shutil.copyfile("configs/lavalink.json", "lava/configs/lavalink.json")

    shutil.copyfile("configs/icons.json", "lava/configs/icons.json")

    success("Lava setup successfully!")


def get_java():
    info("Installing JDK...")

    if not isdir("./java"):
        try:
            jdk.install("17", path="./java", jre=True)
        except StopIteration:
            pass

    for directory in listdir('./java'):
        if directory.startswith('jdk'):
            rename(f"./java/{directory}", f"./java/jdk")
            break

    success("JDK installed successfully!")


def get_lavalink():
    info("Installing Lavalink...")

    if path.isfile("./lavalink/Lavalink.jar"):
        return

    if not path.isdir('./lavalink'):
        mkdir('./lavalink')

    data = requests.get("https://api.github.com/repos/freyacodes/Lavalink/releases/latest").json()

    jar = requests.get(data["assets"][0]["browser_download_url"])

    with open("./lavalink/Lavalink.jar", 'wb') as f:
        f.write(jar.content)

    shutil.copyfile("configs/application.yml", "lavalink/application.yml")

    success("Lavalink installed successfully!")


if __name__ == "__main__":
    main()
