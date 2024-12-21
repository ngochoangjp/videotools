import gradio as gr
import os
import shutil
import subprocess
from moviepy.editor import VideoFileClip, concatenate_videoclips

# --- Helper Functions ---

def split_video_at_marks(video_path, marks):
    """Splits a video into multiple clips based on a list of timestamps (marks)."""
    if not video_path:
        raise gr.Error("Please upload a video file.")
    if not marks:
        raise gr.Error("Please enter at least one mark.")

    try:
        marks = sorted([float(m) for m in marks.split(',')])
    except ValueError:
        raise gr.Error("Invalid marks format. Please use comma-separated numbers (e.g., 10,25.5,60).")

    video = VideoFileClip(video_path)
    clips = []
    start = 0
    for i, mark in enumerate(marks):
        end = mark
        clips.append(video.subclip(start, end))
        start = end

    # Add the last clip
    if start < video.duration:
        clips.append(video.subclip(start))

    output_dir = "split_clips_at_marks"
    os.makedirs(output_dir, exist_ok=True)
    for i, clip in enumerate(clips):
        clip.write_videofile(os.path.join(output_dir, f"clip_{i}.mp4"), codec="libx264", audio_codec="aac")

    return get_video_files_from_dir(output_dir)

def split_video_by_duration(video_path, duration):
    """Splits a video into clips of a specified duration."""
    if not video_path:
        raise gr.Error("Please upload a video file.")
    if not duration:
        raise gr.Error("Please enter a duration.")

    try:
        duration = float(duration)
    except ValueError:
        raise gr.Error("Invalid duration format. Please use a number (e.g., 30).")

    video = VideoFileClip(video_path)
    total_duration = video.duration
    clips = []
    start = 0
    while start < total_duration:
        end = min(start + duration, total_duration)
        clips.append(video.subclip(start, end))
        start = end

    output_dir = "split_clips_by_duration"
    os.makedirs(output_dir, exist_ok=True)
    for i, clip in enumerate(clips):
        clip.write_videofile(os.path.join(output_dir, f"clip_{i}.mp4"), codec="libx264", audio_codec="aac")

    return get_video_files_from_dir(output_dir)

def merge_videos(video_paths):
    """Merges a list of video files into a single video."""
    if not video_paths:
        raise gr.Error("Please select at least two video files.")

    clips = [VideoFileClip(path) for path in video_paths]
    final_clip = concatenate_videoclips(clips)

    output_path = "merged_video.mp4"
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

    return output_path

def get_video_files_from_dir(directory):
    """Get a list of video files from a directory."""
    video_extensions = [".mp4", ".avi", ".mov", ".mkv", ".webm"]  # Add more if needed
    video_files = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f)) and os.path.splitext(f)[1].lower() in video_extensions
    ]
    return video_files

# --- Gradio UI Components ---

# Tool 1: Split at Marks
video_input_marks = gr.Video(label="Input Video")
marks_input = gr.Textbox(label="Marks (comma-separated, e.g., 10,25.5,60)")
split_at_marks_button = gr.Button("Split at Marks")
split_at_marks_output = gr.Gallery(label="Output Video Clips")

# Tool 2: Split by Duration
video_input_duration = gr.Video(label="Input Video")
duration_input = gr.Textbox(label="Duration (in seconds)")
split_by_duration_button = gr.Button("Split by Duration")
split_by_duration_output = gr.Gallery(label="Output Video Clips")

# Tool 3: Merge Videos
video_input_merge = gr.File(label="Input Videos (Drop or Click to Upload)", file_count="multiple")
merge_button = gr.Button("Merge Videos")
merged_video_output = gr.Video(label="Output Merged Video")

# --- Event Handlers ---

# Tool 1
split_at_marks_button.click(
    fn=split_video_at_marks,
    inputs=[video_input_marks, marks_input],
    outputs=split_at_marks_output,
)

# Tool 2
split_by_duration_button.click(
    fn=split_video_by_duration,
    inputs=[video_input_duration, duration_input],
    outputs=split_by_duration_output,
)

# Tool 3
merge_button.click(
    fn=merge_videos,
    inputs=video_input_merge,
    outputs=merged_video_output,
)

# --- Gradio Interface Layout ---

demo = gr.Blocks()

with demo:
    gr.Markdown(
        """
    # Video Editor
    This is a simple video editor with 4 tools:
    1. **Split at Marks:** Split a video into multiple clips based on a list of timestamps (marks).
    2. **Split by Duration:** Split a video into clips of a specified duration.
    3. **Merge Videos:** Merge multiple videos into a single video.
    """
    )
    with gr.Tab("Split at Marks"):
        video_input_marks.render()
        marks_input.render()
        split_at_marks_button.render()
        split_at_marks_output.render()

    with gr.Tab("Split by Duration"):
        video_input_duration.render()
        duration_input.render()
        split_by_duration_button.render()
        split_by_duration_output.render()

    with gr.Tab("Merge Videos"):
        video_input_merge.render()
        merge_button.render()
        merged_video_output.render()

demo.launch()