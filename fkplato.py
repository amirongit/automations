from itertools import count
from subprocess import run
from tempfile import TemporaryDirectory
from uuid import uuid4


AUDIO_FORMAT = "m4a"


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


def read_urls() -> list[str]:
    print("urls (empty to finish) ")
    out: list[str] = []
    for c in count():
        if in_ := input(f"{c}: "):
            out.append(in_)
        else:
            break
    return out


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
                        read_urls(),
                        input("is your life ruined by plato's dualism? ").lower() in ('no', '0', 'false'),
                        input("how severely are you cooked? ").lower() == "well done",
                        input("what's the solution to fix this problem a little? (empty if don't have to deal with it) "),
                        tmpdir,
                    ),
                    create_delimiter(tmpdir, int(input("how much do you know about silence?! ")))
                )
            )
        exit_if_not_successful(
            f"ffmpeg -y -f concat -safe 0 -i {files_list} -c copy "
            f"{input(f"and, what's your claim against plato? (full path with {AUDIO_FORMAT} extension please!) ")}"
        )
