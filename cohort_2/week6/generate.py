import json
import requests


def find_package_json(extension_name):
    # https://raw.githubusercontent.com/raycast/extensions/main/extensions/spotify-player/package.json
    # All commands follow this pattern.
    return f"https://raw.githubusercontent.com/raycast/extensions/main/extensions/{extension_name}/package.json"


def get_package_json(extension_name):
    print(f"Downloading package.json for {extension_name}")
    package_json_url = find_package_json(extension_name)
    response = requests.get(package_json_url)

    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to download package.json for {extension_name}")


def generate_commands(extensions):
    commands = []
    for extension_name in extensions:
        package_json = get_package_json(extension_name)
        package_json = json.loads(package_json)
        excluded_commands = [
            "set-presence",
            "searchSelectText",
        ]
        for command in package_json["commands"]:
            if command["name"] in excluded_commands:
                continue

            attrs = {
                "source_name": command["name"],
                "source_description": command["description"],
                "extension_name": extension_name
                if extension_name != "messages"
                else "imessage",
            }
            command.update(attrs)
            if "preferences" in command:
                del command["preferences"]
            commands.append(command)

    with open("raw_commands.json", "w") as f:
        json.dump(commands, f, indent=2)


if __name__ == "__main__":
    command_extensions = [
        # Issue Tracking
        "jira",
        "github",
        # Note Taking Application
        "confluence-search",
        "notion",
        "obsidian",
        "apple-notes",
        # Search
        "google-search",
        "amazon-search",
        "arxiv",
    ]
    generate_commands(command_extensions)
