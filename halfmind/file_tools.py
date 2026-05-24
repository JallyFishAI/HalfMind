import PyPDF4
import os
import shutil
import zipfile
import screeninfo




def get_files(path: str) -> list:
    """Returns evers File in a specific Directory as a List"""
    files = []
    for root, dirs, filenames in os.walk(path):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    return files

def write_file(path: str, content: str) -> bool:
    """Creates a File and writes content into it."""
    with open(path, "w") as f:
        f.write(content)
    if os.path.exists(path):
        return True
    else:
        return False

def create_directory(path: str):
    """Creates a Directory"""
    if os.path.exists(path):
        return True
    else:
        os.mkdir(path)
        return True

def read_file(path: str) -> str:
    """Reads the content of a file.
    
    Args:
        path: Path to the file to read
    
    Returns:
        Content of the file as a string
        
    Raises:
        FileNotFoundError: If the file does not exist
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def read_file_lines(path: str) -> list:
    """Reads a file and returns its content as a list of lines.
    
    Args:
        path: Path to the file to read
    
    Returns:
        List of lines from the file
        
    Raises:
        FileNotFoundError: If the file does not exist
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.readlines()


def append_file(path: str, content: str) -> bool:
    """Appends content to an existing file.
    
    Args:
        path: Path to the file
        content: Content to append
    
    Returns:
        True if successful
    """
    with open(path, "a", encoding="utf-8") as f:
        f.write(content)
    return True


def delete_file(path: str) -> bool:
    """Deletes a file.
    
    Args:
        path: Path to the file to delete
    
    Returns:
        True if the file was deleted, False if it didn't exist
    """
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


def copy_file(source: str, destination: str) -> bool:
    """Copies a file from source to destination.
    
    Args:
        source: Path to the source file
        destination: Path to the destination file
    
    Returns:
        True if the file was copied successfully
        
    Raises:
        FileNotFoundError: If the source file does not exist
    """
    if not os.path.exists(source):
        raise FileNotFoundError(f"Source file not found: {source}")
    shutil.copy2(source, destination)
    return os.path.exists(destination)


def move_file(source: str, destination: str) -> bool:
    """Moves a file from source to destination.
    
    Args:
        source: Path to the source file
        destination: Path to the destination file
    
    Returns:
        True if the file was moved successfully
        
    Raises:
        FileNotFoundError: If the source file does not exist
    """
    if not os.path.exists(source):
        raise FileNotFoundError(f"Source file not found: {source}")
    shutil.move(source, destination)
    return os.path.exists(destination)


def file_exists(path: str) -> bool:
    """Checks if a file exists.
    
    Args:
        path: Path to the file
    
    Returns:
        True if the file exists, False otherwise
    """
    return os.path.exists(path)


def file_size(path: str) -> int:
    """Returns the size of a file in bytes.
    
    Args:
        path: Path to the file
    
    Returns:
        Size of the file in bytes
        
    Raises:
        FileNotFoundError: If the file does not exist
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    return os.path.getsize(path)


def rename_file(old_path: str, new_path: str) -> bool:
    """Renames a file.
    
    Args:
        old_path: Current path of the file
        new_path: New path for the file
    
    Returns:
        True if the file was renamed successfully
        
    Raises:
        FileNotFoundError: If the old file does not exist
    """
    if not os.path.exists(old_path):
        raise FileNotFoundError(f"File not found: {old_path}")
    os.rename(old_path, new_path)
    return os.path.exists(new_path)


def get_file_extension(path: str) -> str:
    """Returns the file extension.
    
    Args:
        path: Path to the file
    
    Returns:
        File extension (e.g., '.txt', '.py')
    """
    return os.path.splitext(path)[1]


def get_file_name(path: str) -> str:
    """Returns the file name without extension.
    
    Args:
        path: Path to the file
    
    Returns:
        File name without extension
    """
    return os.path.splitext(os.path.basename(path))[0]


def get_directory(path: str) -> str:
    """Returns the directory of a file path.
    
    Args:
        path: Path to the file
    
    Returns:
        Directory path
    """
    return os.path.dirname(path)


def list_directory(path: str) -> list:
    """Lists all files and directories in a path.
    
    Args:
        path: Path to the directory
    
    Returns:
        List of files and directories
        
    Raises:
        FileNotFoundError: If the directory does not exist
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Directory not found: {path}")
    return os.listdir(path)


def create_file(path: str, content: str = "") -> bool:
    """Creates a new file with optional content.
    
    Args:
        path: Path to the new file
        content: Initial content for the file (default empty)
    
    Returns:
        True if the file was created successfully
    """
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return os.path.exists(path)


def delete_directory(path: str, recursive: bool = False) -> bool:
    """Deletes a directory.
    
    Args:
        path: Path to the directory
        recursive: If True, delete directory and all its contents
    
    Returns:
        True if the directory was deleted, False if it didn't exist
    """
    if not os.path.exists(path):
        return False
    if recursive:
        shutil.rmtree(path)
    else:
        os.rmdir(path)
    return not os.path.exists(path)
    










