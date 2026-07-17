import pyfiglet
import subprocess
import os
import json
import socket
import time

FIELD_LABELS = {
    "ami_id": "AMI ID (Ubuntu 24.04)",
    "aws_region": "AWS Region",
    "instance_type": "EC2 Instance Type",
    "key_name": "SSH Key Pair Name",
    "subnet_id": "Subnet ID",
    "private_key_path": "Private Key Path",
    "model_name": "Ollama Model"
}

CONFIG_FIELDS = {
    "aws_region": ("ap-south-1", ["us-east-1", "us-west-2", "eu-west-1"]),
    "instance_type": ("t3.micro", ["t3.small", "t3.medium"]),
    "ami_id": ("ami-01a00762f46d584a1", []),
    "key_name": ("", []),
    "subnet_id": ("", []),
    "private_key_path": ("", []),
    "model_name": ("smollm:135m",["llama3.2","llama3.1:8b", "mistral", "gemma2"]),
}


def banner():
    print(pyfiglet.figlet_format("EC2 x OLLAMA"))


def ask_value(name, default, choices):
    print(f"\n{FIELD_LABELS.get(name, name)}")

    options = choices.copy()

    if default:
        options.insert(0, default)

    for i, value in enumerate(options, 1):
        mark = " (default)" if default and value == default else ""
        print(f"{i}. {value}{mark}")

    print(f"{len(options)+1}. Custom value")

    while True:
        choice = input("Select: ")

        if choice.isdigit():
            choice = int(choice)

            if 1 <= choice <= len(options):
                return options[choice - 1]

            if choice == len(options) + 1:
                return input(f"Enter {name}: ")

        print("Invalid choice. Try again.")

def collect_config():
    config = {}

    for name, (default, options) in CONFIG_FIELDS.items():
        config[name] = ask_value(name, default, options)

    return config


def show_config(config):
    print("\nConfiguration:")
    print("-" * 40)

    for key, value in config.items():
        print(f"{key}: {value}")

    print("-" * 40)

def create_tfvars(config, filename="terraform/terraform.tfvars"):
    with open(filename, "w") as file:
        for key, value in config.items():
            file.write(f'{key} = "{value}"\n')

    print(f"{filename} created successfully")


def run_terraform(terraform_dir="terraform"):

    subprocess.run(
        ["terraform", "init"],
        cwd=terraform_dir,
        check=True
    )

    subprocess.run(
        ["terraform", "apply", "-auto-approve"],
        cwd=terraform_dir,
        check=True
    )

    print("Terraform deployment completed successfully.")

def get_terraform_outputs(terraform_dir="terraform"):

    result = subprocess.run(
        [
            "terraform",
            "output",
            "-json"
        ],
        cwd=terraform_dir,
        capture_output=True,
        text=True,
        check=True
    )

    return json.loads(result.stdout)

def get_ssh_user(ami_id):

    ami_users = {

        # Ubuntu
        "ubuntu": "ubuntu",

        # Amazon Linux
        "amazon": "ec2-user",

        # Debian
        "debian": "admin",

        # CentOS
        "centos": "centos"
    }


    ami_id = ami_id.lower()

    if "ubuntu" in ami_id:
        return "ubuntu"

    if "amazon" in ami_id:
        return "ec2-user"

    if "debian" in ami_id:
        return "admin"

    if "centos" in ami_id:
        return "centos"


    # fallback
    return "ec2-user"


def create_inventory(terraform_output, private_key_path, inventory_dir="ansible"):

    os.makedirs(inventory_dir, exist_ok=True)

    public_ip = terraform_output["ec2_public_ip"]["value"]

    inventory_file = os.path.join(
        inventory_dir,
        "inventory.ini"
    )

    content = f"""[ollama]

ec2-server ansible_host={public_ip} ansible_user=ubuntu ansible_ssh_private_key_file={private_key_path} ansible_ssh_common_args='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'
"""

    with open(inventory_file, "w") as file:
        file.write(content)

    print(f"\nInventory created: {inventory_file}")
    print(content)

def wait_for_ssh(host, port=22, timeout=300):
    """
    Wait until SSH is accepting connections.
    """

    print(f"Waiting for SSH on {host}...")

    start = time.time()

    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=5):
                print("SSH is ready.")
                return
        except OSError:
            print("SSH not ready yet...")
            time.sleep(5)

    raise TimeoutError("Timed out waiting for SSH.")

def run_ansible(config):
    subprocess.run(
        [
            "ansible-playbook",
            "-i",
            "ansible/inventory.ini",
            "ansible/playbook.yml",
            "-e",f"ollama_model={config['model_name']}"
        ],
        check=True,
    )

def show_endpoint(public_ip):
    print("\n" + "=" * 50)
    print("Deployment Complete!")
    print(f"Ollama Endpoint : http://{public_ip}:11434")
    print("=" * 50)

def destroy_menu():

    while True:
        print("\n")
        print("1. Destroy infrastructure")
        print("2. Exit")

        choice = input("Select: ")

        if choice == "1":
            destroy_terraform()
            break

        elif choice == "2":
            print("Exiting...")
            break

        else:
            print("Invalid option.")

def destroy_terraform(terraform_dir="terraform"):

    subprocess.run(
        [
            "terraform",
            "destroy",
            "-auto-approve"
        ],
        cwd=terraform_dir,
        check=True
    )

    print("Infrastructure destroyed.")
    
def deploy():
    banner()

    config = collect_config()
    show_config(config)

    create_tfvars(config)
    # run_terraform()
    try:
        run_terraform()
    except subprocess.CalledProcessError:
        print("Deployment failed.")
        return

    terraform_data = get_terraform_outputs()
    public_ip = terraform_data["ec2_public_ip"]["value"]

    create_inventory(
        terraform_data,
        config["private_key_path"]
    )

    wait_for_ssh(public_ip)

    run_ansible(config)

    show_endpoint(public_ip)

    destroy_menu()


if __name__ == "__main__":
    deploy()