import ast
import hashlib
import os
import time
import shutil
import subprocess
from glob import glob

ON_WINDOWS = False
ON_UNIX = False
if os.name == "nt":
    # Windows specific imports and setup
    ON_WINDOWS = True
    # noinspection PyUnresolvedReferences
    import win32api
    import psutil
elif os.name == "posix":
    # Unix specific imports and setup
    ON_UNIX = True


SRC_DIRECTORY = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"
)
DEPLOY_DIRECTORY = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "deploy"
)


def exclude_from_deploy(filename):
    # This function tells the program which files to ignore while scanning the "deploy" directory
    return filename.endswith(".svg") or filename.endswith("~") or filename.startswith("~")


MAIN_PROGRAM = os.path.join(SRC_DIRECTORY, "main.py")

DRIVE_IDENTIFIER_STRING = "VEX"
FIND_VEX_DISK_MAX_ATTEMPTS = 10
FIND_VEX_DISK_TIME_BETWEEN_ATTEMPTS = 1
VEX_BUILTIN_MODULES = [
    "micropython",
    "uasyncio.event",
    "urandom",
    "_thread",
    "motorgroup",
    "uasyncio.funcs",
    "ure",
    "_uasyncio",
    "python_vm_init",
    "uasyncio.lock",
    "uselect",
    "builtins",
    "smartdrive",
    "uasyncio.stream",
    "ustruct",
    "cmath",
    "sys",
    "ubinascii",
    "utime",
    "drivetrain",
    "uarray",
    "ucollections",
    "utimeq",
    "gc",
    "uasyncio",
    "uio",
    "vex",
    "math",
    "uasyncio.core",
    "ujson",
    "vexdev",
]


def mount_drive(drive_path):
    if ON_WINDOWS:
        pass
    elif ON_UNIX:
        subprocess.run(["mount", drive_path], check=True)


def unmount_drive(drive_path):
    if ON_WINDOWS:
        eject_command = (
            "powershell $driveEject = New-Object -comObject Shell.Application;"
        )
        eject_command += f'$driveEject.Namespace(17).ParseName("""{drive_path}""").InvokeVerb("""Eject""")'
        subprocess.run(eject_command, check=True)
    elif ON_UNIX:
        subprocess.run(["umount", drive_path], check=True)


def get_vex_disk() -> str:
    """
    Find the first mounted disk that has a name including the DRIVE_IDENTIFIED_STRING

    Returns: str
    Raises: FileNotFoundError
    """
    if ON_WINDOWS:
        disks = psutil.disk_partitions()
        for disk in disks:
            if disk.fstype:
                drive_name = win32api.GetVolumeInformation(disk.device)[0]
                deploy_path = disk.mountpoint
                if DRIVE_IDENTIFIER_STRING in drive_name:
                    return deploy_path
    elif ON_UNIX:
        mount_point_dir = os.path.join(os.sep, "media", os.getenv("USER"))
        mount_points = os.listdir(mount_point_dir)
        for mount_point in mount_points:
            drive_name = os.path.basename(mount_point)
            deploy_path = os.path.join(mount_point_dir, drive_name)
            if DRIVE_IDENTIFIER_STRING in drive_name:
                return deploy_path
    raise FileNotFoundError("Could not find sd card mount point")


def get_available_modules(library_directory):
    """Scan a directory for all python files and return a dictionary relating their module names to their file"""
    available_modules = {}
    for file in glob(os.path.join(library_directory, "*.py")):
        available_modules[os.path.basename(file.split(os.sep)[-1].split(".")[0])] = file
    return available_modules


def detect_dependencies(file_path, available_libraries, visited=None):
    """
    Find the dependencies of a python file recursively (all dependencies must be in SRC_DIRECTORY)

    Args:
        file_path: The initial file to detect dependencies of
        available_libraries: A dictionary relating the names of the available libraries to their paths
        visited: The set of previously visited files. This prevents infinite recursion and defaults to an empty set

    Returns:
        A set with the names of all required modules that are not in VEX_BUILTIN_MODULES
    """

    if visited is None:
        visited = set()

    with open(file_path, "r") as file:
        file_content = file.read()

    tree = ast.parse(file_content)
    imported_modules = set()

    for node in ast.walk(tree):
        module_names = []
        if isinstance(node, ast.Import):
            module_names = [name.name for name in node.names]
        elif isinstance(node, ast.ImportFrom):
            module_names = [node.module]
        for module in module_names:
            if module not in visited and module not in VEX_BUILTIN_MODULES:
                # Add the module to the visited set
                visited.add(module)
                # Add the module to the imported set
                imported_modules.add(module)
                # Ensure the imported module exists in
                if module not in available_libraries:
                    raise ModuleNotFoundError(
                        f'File {file_path} references module "{module}" but, it could not be found in {SRC_DIRECTORY}'
                    )
                # Recurse until no additional modules can be found
                imported_modules.update(
                    detect_dependencies(
                        available_libraries[module], available_libraries, visited
                    )
                )

    return imported_modules


def get_checksum(file_path: str) -> str:
    """
    Get the MD5 checksum of a file

    Args:
        file_path: The path of the file

    Returns:
        The checksum of the file

    """
    return hashlib.md5(open(file_path, "rb").read()).hexdigest()


def copy_libraries(libraries, directory):
    for file in libraries:
        if os.path.isfile(directory):
            os.remove(directory)
        if not os.path.exists(directory):
            os.mkdir(directory)
        file_to_copy_checksum = get_checksum(file)
        file_to_overwrite = os.path.join(directory, (file.split(os.sep)[-1]))
        file_to_overwrite_checksum = None
        if os.path.isfile(file_to_overwrite):
            file_to_overwrite_checksum = get_checksum(file_to_overwrite)
        elif os.path.isdir(file_to_overwrite):
            print(f"{file_to_overwrite} exists as folder, removing it")
            os.rmdir(file_to_overwrite)
            shutil.copy(file, directory)
        if file_to_copy_checksum != file_to_overwrite_checksum:
            if file_to_overwrite_checksum:
                print(
                    f"{file_to_overwrite} exists but has invalid checksum: {file_to_overwrite_checksum}, pushing"
                )
                os.remove(file_to_overwrite)
            else:
                print(f"{file_to_overwrite} does not exist, pushing")
            shutil.copy(file, directory)


def main():
    failure_count = 0
    while failure_count < FIND_VEX_DISK_MAX_ATTEMPTS - 1:
        try:
            vex_disk = get_vex_disk()
            print(f"Found vex disk at {vex_disk}")
            break  # We have found the disk
        except FileNotFoundError:
            vex_disk = None
            failure_count += 1
            print(
                f"Could not find vex disk, retrying in {FIND_VEX_DISK_TIME_BETWEEN_ATTEMPTS} seconds... ({FIND_VEX_DISK_MAX_ATTEMPTS - failure_count} attempt(s) remaining)"
            )
            time.sleep(FIND_VEX_DISK_TIME_BETWEEN_ATTEMPTS)

    if failure_count >= FIND_VEX_DISK_MAX_ATTEMPTS - 1:
        raise FileNotFoundError("Could not find sd card mount point")

    available_libraries = get_available_modules(SRC_DIRECTORY)

    required_libraries = detect_dependencies(MAIN_PROGRAM, available_libraries)

    libraries_to_copy = {}

    for library in required_libraries:
        if library in available_libraries:
            libraries_to_copy[library] = available_libraries[library]
        else:
            raise ModuleNotFoundError(f'Couldn\'t find library "{library}"')

    deploy_objects = []

    for dependency in glob(DEPLOY_DIRECTORY + "/**", recursive=True):
        if os.path.isfile(dependency):
            if not exclude_from_deploy(dependency):
                deploy_objects.append(os.path.join(DEPLOY_DIRECTORY, dependency))

    print("Pushing libraries")
    # Copy all source files (main.py and it's dependencies) into the root directory
    copy_libraries(libraries_to_copy.values(), vex_disk)
    # copy all deploy objects to the "deploy" directory
    copy_libraries(deploy_objects, os.path.join(vex_disk, "deploy"))

    if not os.path.isdir(os.path.join(vex_disk, "logs")):
        os.mkdir(os.path.join(vex_disk, "logs"))

    print("Unmounting drive")

    unmount_drive(vex_disk)
    print("Safe to remove drive")


if __name__ == "__main__":
    main()
