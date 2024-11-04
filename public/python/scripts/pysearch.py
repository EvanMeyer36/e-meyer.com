import os

def find_python_scripts(start_dir):
    python_scripts = []
    for root, dirs, files in os.walk(start_dir):
        for file in files:
            if file.endswith(".py"):
                python_scripts.append(os.path.join(root, file))
    return python_scripts

if __name__ == "__main__":
    # Change this to your desired starting directory, e.g., "C:\\", "/" for root
    start_directory = "C:\\"
    scripts = find_python_scripts(start_directory)
    
    print(f"Found {len(scripts)} Python scripts:")
    for script in scripts:
        print(script)
