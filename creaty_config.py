import shutil
import yaml
import os

def copy_config():
    # Copy the example config file to a new config file
    shutil.copy('config.example.yaml', 'config.yaml')
    print("Copied config.example.yaml to config.yaml")

def update_config(user_variables):
    # Load the existing config.yaml
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    # Update the config with user-specific variables
    config['dataset'].update(user_variables)

    # Write the updated config back to config.yaml
    with open('config.yaml', 'w') as file:
        yaml.dump(config, file)

    print("Updated config.yaml with user-specific variables")

def main():
    # Check if the example config file exists
    if not os.path.exists('config.example.yaml'):
        print("Error: config.example.yaml does not exist.")
        return

    # Copy the example config to a new config file
    copy_config()

    # Gather user-specific variables
    user_variables = {}
    user_variables['base_dir'] = input("Enter the base directory of the dataset: ")

    # Update the config file with user-specific variables
    update_config(user_variables)

if __name__ == "__main__":
    main()