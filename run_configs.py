import glob
import subprocess
from multiprocessing import Pool


def run_one(path: str):
    try:
        subprocess.run(
            [
                "java",
                "-Xmx1G",
                "-cp",
                "target:lib/ECLA.jar:lib/DTNConsoleConnection.jar",
                "core.DTNSim",
                "-b",
                "1",
                path,
            ],
            capture_output=True,
            check=True,
        )
        return f"Logrado: {path}"
    except subprocess.CalledProcessError as e:
        with open("errors/" + path.split("/")[1], "a") as file:
            file.writelines(
                [
                    f"Command '{e.cmd}' exited with non-zero exit status {e.returncode}.",
                    f"Output: {e.stderr}",
                    f"{e.stdout}",
                    "-----------------------------\n",
                ]
            )
        return f"Error: {path}"
    except Exception as e:
        print("ERROR!")
        with open("errors/" + path.split("/")[1], "a") as file:
            file.writelines([e, "-----------------------------\n"])
        return f"Error: {path}"


if __name__ == "__main__":
    print("Empezando")
    paths = [
        "configs/" + path.split("/")[1] for path in glob.glob("errors/config_*.txt")
    ]
    print(paths)
    with Pool() as pool:
        res = pool.imap_unordered(run_one, paths)
        for r in res:
            print(r)
