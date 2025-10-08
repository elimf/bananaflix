import ffmpeg

def convert_video_with_resolution(input_path, output_path, resolution: int):
    (
        ffmpeg
        .input(input_path)
        .output(
            output_path,
            vcodec="libx265",
            acodec="aac",
            vf=f"scale=-2:{resolution}"
        )
        .run(overwrite_output=True)
    )

def extract_trailer(input_path, output_path):
    (
        ffmpeg
        .input(input_path, ss=0, t=30)
        .output(output_path, vcodec='libx265', acodec='aac')
        .run(overwrite_output=True)
    )
