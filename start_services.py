#!/usr/bin/env python3
"""
start_services.py

This script starts the local AI stack.
"""

import os
import subprocess
import shutil
import argparse
import platform
import time


def run_command(cmd, cwd=None):
    """Run a shell command and print it."""
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)


def compose_base_command(profile=None, environment=None):
    """Build the base Docker Compose command for this project."""
    cmd = ["docker", "compose", "-p", "localai"]
    if profile and profile != "none":
        cmd.extend(["--profile", profile])
    cmd.extend(["-f", "docker-compose.yml"])
    if environment == "private":
        cmd.extend(["-f", "docker-compose.override.private.yml"])
    if environment == "public":
        cmd.extend(["-f", "docker-compose.override.public.yml"])
    return cmd


def get_update_services(profile=None):
    """Return Compose services that should be refreshed for Ollama/Open WebUI updates."""
    services = ["open-webui"]

    if profile == "gpu-amd":
        services.append("ollama-gpu-amd")
    elif profile == "gpu-nvidia":
        services.append("ollama-gpu")
    elif profile == "cpu":
        services.append("ollama-cpu")

    return services


def pull_services_with_retry(profile=None, environment=None, services=None, retries=3, delay_seconds=3):
    """Pull Docker Compose services with retries to handle transient failures."""
    services = services or []
    if not services:
        return

    for attempt in range(1, retries + 1):
        print(
            f"Pulling services {', '.join(services)} "
            f"(attempt {attempt}/{retries})..."
        )
        cmd = compose_base_command(profile=profile, environment=environment)
        cmd.extend(["pull", *services])
        result = subprocess.run(cmd, check=False)
        if result.returncode == 0:
            print("Successfully pulled update services.")
            return

        if attempt < retries:
            print(f"Pull failed. Retrying in {delay_seconds} seconds...")
            time.sleep(delay_seconds)

    raise RuntimeError(
        f"Failed to pull services {', '.join(services)} after {retries} attempts."
    )


def update_ollama_and_openwebui_images(profile=None, environment=None):
    """Pull fresh, Compose-compatible Ollama and Open WebUI images."""
    print("Updating Ollama and Open WebUI images...")
    services = get_update_services(profile)
    pull_services_with_retry(profile=profile, environment=environment, services=services)


def verify_compose_configuration(profile=None, environment=None):
    """Validate Docker Compose configuration before deployment actions."""
    print("Verifying Docker Compose configuration...")
    cmd = compose_base_command(profile=profile, environment=environment)
    cmd.extend(["config", "-q"])
    run_command(cmd)


def stop_existing_containers(profile=None, environment=None):
    print("Stopping and removing existing containers for the unified project 'localai'...")
    cmd = compose_base_command(profile=profile, environment=environment)
    cmd.append("down")
    run_command(cmd)


def start_local_ai(profile=None, environment=None):
    """Start the local AI services (using its compose file)."""
    print("Starting local AI services...")
    cmd = compose_base_command(profile=profile, environment=environment)
    cmd.extend(["up", "-d"])
    run_command(cmd)


def refresh_running_ollama_and_openwebui(profile=None, environment=None):
    """Update running Ollama/Open WebUI containers with latest images."""
    print("Refreshing running Ollama and Open WebUI services...")
    services = get_update_services(profile)
    update_ollama_and_openwebui_images(profile=profile, environment=environment)

    cmd = compose_base_command(profile=profile, environment=environment)
    cmd.extend(["up", "-d", "--no-deps", "--force-recreate", *services])
    run_command(cmd)


def generate_searxng_secret_key():
    """Generate a secret key for SearXNG based on the current platform."""
    print("Checking SearXNG settings...")

    settings_path = os.path.join("searxng", "settings.yml")
    settings_base_path = os.path.join("searxng", "settings-base.yml")

    if not os.path.exists(settings_base_path):
        print(f"Warning: SearXNG base settings file not found at {settings_base_path}")
        return

    if not os.path.exists(settings_path):
        print(f"SearXNG settings.yml not found. Creating from {settings_base_path}...")
        try:
            shutil.copyfile(settings_base_path, settings_path)
            print(f"Created {settings_path} from {settings_base_path}")
        except Exception as e:
            print(f"Error creating settings.yml: {e}")
            return
    else:
        print(f"SearXNG settings.yml already exists at {settings_path}")

    print("Generating SearXNG secret key...")

    system = platform.system()

    try:
        if system == "Windows":
            print("Detected Windows platform, using PowerShell to generate secret key...")
            ps_command = [
                "powershell", "-Command",
                "$randomBytes = New-Object byte[] 32; " +
                "(New-Object Security.Cryptography.RNGCryptoServiceProvider).GetBytes($randomBytes); " +
                "$secretKey = -join ($randomBytes | ForEach-Object { \"{0:x2}\" -f $_ }); " +
                "(Get-Content searxng/settings.yml) -replace 'ultrasecretkey', $secretKey | Set-Content searxng/settings.yml"
            ]
            subprocess.run(ps_command, check=True)

        elif system == "Darwin":
            print("Detected macOS platform, using sed command with empty string parameter...")
            openssl_cmd = ["openssl", "rand", "-hex", "32"]
            random_key = subprocess.check_output(openssl_cmd).decode('utf-8').strip()
            sed_cmd = ["sed", "-i", "", f"s|ultrasecretkey|{random_key}|g", settings_path]
            subprocess.run(sed_cmd, check=True)

        else:
            print("Detected Linux/Unix platform, using standard sed command...")
            openssl_cmd = ["openssl", "rand", "-hex", "32"]
            random_key = subprocess.check_output(openssl_cmd).decode('utf-8').strip()
            sed_cmd = ["sed", "-i", f"s|ultrasecretkey|{random_key}|g", settings_path]
            subprocess.run(sed_cmd, check=True)

        print("SearXNG secret key generated successfully.")

    except Exception as e:
        print(f"Error generating SearXNG secret key: {e}")
        print("You may need to manually generate the secret key using the commands:")
        print("  - Linux: sed -i \"s|ultrasecretkey|$(openssl rand -hex 32)|g\" searxng/settings.yml")
        print("  - macOS: sed -i '' \"s|ultrasecretkey|$(openssl rand -hex 32)|g\" searxng/settings.yml")
        print("  - Windows (PowerShell):")
        print("    $randomBytes = New-Object byte[] 32")
        print("    (New-Object Security.Cryptography.RNGCryptoServiceProvider).GetBytes($randomBytes)")
        print("    $secretKey = -join ($randomBytes | ForEach-Object { \"{0:x2}\" -f $_ })")
        print("    (Get-Content searxng/settings.yml) -replace 'ultrasecretkey', $secretKey | Set-Content searxng/settings.yml")


def check_and_fix_docker_compose_for_searxng():
    """Check and modify docker-compose.yml for SearXNG first run."""
    docker_compose_path = "docker-compose.yml"
    if not os.path.exists(docker_compose_path):
        print(f"Warning: Docker Compose file not found at {docker_compose_path}")
        return

    try:
        with open(docker_compose_path, 'r') as file:
            content = file.read()

        is_first_run = True

        try:
            container_check = subprocess.run(
                ["docker", "ps", "--filter", "name=searxng", "--format", "{{.Names}}"],
                capture_output=True, text=True, check=True
            )
            searxng_containers = container_check.stdout.strip().split('\n')

            if any(container for container in searxng_containers if container):
                container_name = next(container for container in searxng_containers if container)
                print(f"Found running SearXNG container: {container_name}")

                container_check = subprocess.run(
                    ["docker", "exec", container_name, "sh", "-c", "[ -f /etc/searxng/uwsgi.ini ] && echo 'found' || echo 'not_found'"],
                    capture_output=True, text=True, check=False
                )

                if "found" in container_check.stdout:
                    print("Found uwsgi.ini inside the SearXNG container - not first run")
                    is_first_run = False
                else:
                    print("uwsgi.ini not found inside the SearXNG container - first run")
                    is_first_run = True
            else:
                print("No running SearXNG container found - assuming first run")
        except Exception as e:
            print(f"Error checking Docker container: {e} - assuming first run")

        if is_first_run and "cap_drop: - ALL" in content:
            print("First run detected for SearXNG. Temporarily removing 'cap_drop: - ALL' directive...")
            modified_content = content.replace("cap_drop: - ALL", "# cap_drop: - ALL  # Temporarily commented out for first run")

            with open(docker_compose_path, 'w') as file:
                file.write(modified_content)

            print("Note: After the first run completes successfully, you should re-add 'cap_drop: - ALL' to docker-compose.yml for security reasons.")
        elif not is_first_run and "# cap_drop: - ALL  # Temporarily commented out for first run" in content:
            print("SearXNG has been initialized. Re-enabling 'cap_drop: - ALL' directive for security...")
            modified_content = content.replace("# cap_drop: - ALL  # Temporarily commented out for first run", "cap_drop: - ALL")

            with open(docker_compose_path, 'w') as file:
                file.write(modified_content)

    except Exception as e:
        print(f"Error checking/modifying docker-compose.yml for SearXNG: {e}")


def main():
    parser = argparse.ArgumentParser(description='Start the local AI services.')
    parser.add_argument('--profile', choices=['cpu', 'gpu-nvidia', 'gpu-amd', 'none'], default='gpu-nvidia',
                      help='Profile to use for Docker Compose (default: gpu-nvidia)')
    parser.add_argument('--environment', choices=['private', 'public'], default='private',
                      help='Environment to use for Docker Compose (default: private)')
    parser.add_argument('--update-images', action='store_true',
                      help='Pull the latest Ollama and Open WebUI images before restarting services')
    parser.add_argument('--update-running-images', action='store_true',
                      help='Pull and recreate only running Ollama/Open WebUI services without full stack restart')
    args = parser.parse_args()

    if args.update_images and args.update_running_images:
        parser.error("--update-images and --update-running-images cannot be used together")

    verify_compose_configuration(args.profile, args.environment)

    if args.update_running_images:
        refresh_running_ollama_and_openwebui(args.profile, args.environment)
        return

    generate_searxng_secret_key()
    check_and_fix_docker_compose_for_searxng()

    if args.update_images:
        update_ollama_and_openwebui_images(args.profile, args.environment)

    stop_existing_containers(args.profile, args.environment)
    start_local_ai(args.profile, args.environment)


if __name__ == "__main__":
    main()
