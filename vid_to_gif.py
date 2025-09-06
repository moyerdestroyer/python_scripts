#!/usr/bin/env python3
"""
Video to GIF Converter
Convert video files to animated GIFs with customizable settings.
Requires: ffmpeg to be installed on your system
"""

import argparse
import subprocess
import os
import sys
from pathlib import Path


def check_ffmpeg():
    """Check if ffmpeg is installed."""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_video_duration(input_file):
    """Get the duration of the video in seconds."""
    try:
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            input_file
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError):
        return None


def timestamp_to_seconds(timestamp):
    """Convert timestamp (HH:MM:SS or seconds) to seconds."""
    if timestamp is None:
        return None
    
    # If it's already a number, treat it as seconds
    try:
        return float(timestamp)
    except ValueError:
        pass
    
    # Parse HH:MM:SS or MM:SS format
    parts = timestamp.split(':')
    if len(parts) == 3:
        hours, minutes, seconds = map(float, parts)
        return hours * 3600 + minutes * 60 + seconds
    elif len(parts) == 2:
        minutes, seconds = map(float, parts)
        return minutes * 60 + seconds
    elif len(parts) == 1:
        return float(parts[0])
    else:
        raise ValueError(f"Invalid timestamp format: {timestamp}")


def video_to_gif(input_file, output_file=None, width=None, start=None, end=None, fps=10):
    """
    Convert video to GIF using ffmpeg.
    
    Args:
        input_file: Path to input video file
        output_file: Path to output GIF file (optional)
        width: Width of output GIF in pixels (height scaled proportionally)
        start: Start timestamp (seconds or HH:MM:SS format)
        end: End timestamp (seconds or HH:MM:SS format)
        fps: Frames per second for the output GIF
    """
    
    # Validate input file
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return False
    
    # Generate output filename if not provided
    if output_file is None:
        input_path = Path(input_file)
        output_file = input_path.stem + '.gif'
    
    # Build ffmpeg command
    cmd = ['ffmpeg', '-i', input_file]
    
    # Add start time if specified
    if start is not None:
        start_seconds = timestamp_to_seconds(start)
        cmd.extend(['-ss', str(start_seconds)])
    
    # Add duration if end time is specified
    if end is not None:
        end_seconds = timestamp_to_seconds(end)
        if start is not None:
            start_seconds = timestamp_to_seconds(start)
            duration = end_seconds - start_seconds
            if duration <= 0:
                print("Error: End time must be after start time.")
                return False
            cmd.extend(['-t', str(duration)])
        else:
            cmd.extend(['-t', str(end_seconds)])
    
    # Create filter for scaling and generating palette
    filters = []
    
    # Scale filter
    if width:
        filters.append(f'scale={width}:-1:flags=lanczos')
    else:
        filters.append('scale=-1:-1:flags=lanczos')
    
    # FPS filter
    filters.append(f'fps={fps}')
    
    # Generate palette for better quality
    palette_filters = ','.join(filters) + ',palettegen'
    
    # First pass: generate palette
    palette_cmd = cmd + [
        '-vf', palette_filters,
        '-y', 'palette.png'
    ]
    
    print(f"Generating color palette...")
    try:
        subprocess.run(palette_cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"Error generating palette: {e}")
        return False
    
    # Second pass: use palette to generate GIF
    gif_filters = ','.join(filters) + f'[x];[x][1:v]paletteuse'
    
    gif_cmd = cmd + [
        '-i', 'palette.png',
        '-lavfi', gif_filters,
        '-y', output_file
    ]
    
    print(f"Converting video to GIF...")
    try:
        subprocess.run(gif_cmd, check=True, capture_output=True)
        
        # Clean up palette file
        if os.path.exists('palette.png'):
            os.remove('palette.png')
        
        # Get file size
        file_size = os.path.getsize(output_file) / (1024 * 1024)  # Convert to MB
        print(f"✓ Successfully created: {output_file} ({file_size:.2f} MB)")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error creating GIF: {e}")
        if os.path.exists('palette.png'):
            os.remove('palette.png')
        return False


def main():
    # Recommended widths for common use cases
    RECOMMENDED_WIDTHS = {
        'tiny': 240,
        'small': 320,
        'medium': 480,
        'large': 640,
        'xlarge': 800,
        'hd': 1280
    }
    
    parser = argparse.ArgumentParser(
        description='Convert video files to animated GIFs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  %(prog)s video.mp4
  %(prog)s video.mp4 -w 480
  %(prog)s video.mp4 -w medium
  %(prog)s video.mp4 --start 10 --end 20
  %(prog)s video.mp4 --start 0:30 --end 1:15
  %(prog)s video.mp4 -o output.gif -w small --fps 15

Recommended widths:
  {', '.join([f'{k}={v}px' for k, v in RECOMMENDED_WIDTHS.items()])}
        """
    )
    
    parser.add_argument('input', help='Input video file')
    parser.add_argument('-o', '--output', help='Output GIF file (default: input_name.gif)')
    parser.add_argument(
        '-w', '--width',
        help='Output width in pixels or preset (tiny/small/medium/large/xlarge/hd). Height scales proportionally.'
    )
    parser.add_argument(
        '-s', '--start',
        help='Start timestamp (seconds or HH:MM:SS format)'
    )
    parser.add_argument(
        '-e', '--end',
        help='End timestamp (seconds or HH:MM:SS format)'
    )
    parser.add_argument(
        '--fps',
        type=int,
        default=10,
        help='Frames per second (default: 10, lower = smaller file)'
    )
    parser.add_argument(
        '--list-info',
        action='store_true',
        help='Show video information without converting'
    )
    
    args = parser.parse_args()
    
    # Check if ffmpeg is installed
    if not check_ffmpeg():
        print("Error: ffmpeg is not installed or not in PATH.")
        print("Please install ffmpeg: https://ffmpeg.org/download.html")
        sys.exit(1)
    
    # Show video info if requested
    if args.list_info:
        duration = get_video_duration(args.input)
        if duration:
            minutes, seconds = divmod(duration, 60)
            hours, minutes = divmod(minutes, 60)
            print(f"Video duration: {int(hours):02d}:{int(minutes):02d}:{seconds:05.2f}")
        else:
            print("Could not determine video duration.")
        sys.exit(0)
    
    # Process width argument
    width = None
    if args.width:
        if args.width.lower() in RECOMMENDED_WIDTHS:
            width = RECOMMENDED_WIDTHS[args.width.lower()]
            print(f"Using preset width: {args.width} ({width}px)")
        else:
            try:
                width = int(args.width)
                print(f"Using custom width: {width}px")
            except ValueError:
                print(f"Error: Invalid width '{args.width}'. Use a number or preset name.")
                sys.exit(1)
    else:
        # Default to medium if not specified
        width = RECOMMENDED_WIDTHS['medium']
        print(f"Using default width: medium ({width}px)")
    
    # Validate timestamps
    try:
        if args.start:
            timestamp_to_seconds(args.start)
        if args.end:
            timestamp_to_seconds(args.end)
    except ValueError as e:
        print(f"Error: {e}")
        print("Timestamps should be in seconds (30) or HH:MM:SS (0:00:30) format")
        sys.exit(1)
    
    # Convert video to GIF
    success = video_to_gif(
        args.input,
        args.output,
        width,
        args.start,
        args.end,
        args.fps
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()