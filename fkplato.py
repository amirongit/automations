from subprocess import run
from tempfile import TemporaryDirectory
from uuid import uuid4


AUDIO_FORMAT = "m4a"
POSITIVE_INPUTS = ('yes', '1', 'true')


def create_delimiter(dest: str, length: int) -> str:
    out = f"{dest}/{uuid4()}.{AUDIO_FORMAT}"
    exit_if_not_successful(f"ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t {length} {out}")
    return out


def get_ordered_files_list(files: list[str], delimiter: str) -> list[str]:
    out: list[str] = []
    for item in files:
        out.append(f"file '{item}'\n")
        out.append(f"file '{delimiter}'\n")
    out.pop()
    return out


def download(urls: list[str], high_quality: bool, use_inf_retries: bool, proxy: str, dest: str) -> list[str]:
    file_path_templat = dest + "/{fid}"
    cmnd = (
        f"yt-dlp -x {"-f ba" if high_quality else "-f wa"} "
        "-o '{file_path}' --audio-format "
        f"{AUDIO_FORMAT} --retries {"infinite" if use_inf_retries else 10}"
    )
    if proxy:
        cmnd += f" --proxy {proxy}"

    out: list[str] = []
    for u in urls:
        exit_if_not_successful(f"{cmnd.format(file_path=(file_path := file_path_templat.format(fid=uuid4())))} {u}")
        out.append(f"{file_path}.{AUDIO_FORMAT}")

    return out


def read_urls(file: str) -> list[str]:
    with open(file, 'r') as f:
        return [u.removesuffix('\n') for u in f.readlines()]


def exit_if_not_successful(command: str) -> None:
    if (returncode := (res := run(command, shell=True, capture_output=True, text=True)).returncode) != 0:
        print(f"{command} caused this: \n{res.stderr}")
        exit(returncode)


if __name__ == "__main__":
    with TemporaryDirectory(delete=False) as tmpdir:
        print(f"using {tmpdir} as working directory...")
        with open(files_list := f"{tmpdir}/fileslist.txt", "w") as fl:
            fl.writelines(
                get_ordered_files_list(
                    download(
                        read_urls(
                            input("file containing urls (one per line): ")
                        ),
                        input("high quality? ").lower() in POSITIVE_INPUTS,
                        input("infinite retries? ").lower() in POSITIVE_INPUTS,
                        input("proxy (could be empty): "),
                        tmpdir,
                    ),
                    create_delimiter(
                        tmpdir,
                        int(input("length of silence between tracks: "))
                    )
                )
            )
        exit_if_not_successful(
            f"ffmpeg -y -f concat -safe 0 -i {files_list} -c copy "
            f"{input(f"output file (full path with {AUDIO_FORMAT} extension): ")}"
        )
