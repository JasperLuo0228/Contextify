import tempfile
import os
from pydub import AudioSegment 
import noisereduce as nr 
import numpy as np 

def process_audio(raw_path: str) -> str:
    """
    Processes raw audio file and returns the path to a denoised WAV file.
    Args:
        raw_path (str): Path to the raw audio file.
    Returns:
        str: Path to the processed WAV file.
    """
    try:
        audio_segment = AudioSegment.from_raw(
            file=raw_path,
            sample_width=4,  
            frame_rate=44100, 
            channels=1   
        )

        print("[DEBUG] Successfully parsed raw PCM to AudioSegment")

        audio_segment = (
            audio_segment
            .set_frame_rate(16000)
            .set_channels(1)
            .set_sample_width(2) 
        )

        samples = np.array(audio_segment.get_array_of_samples())
        sr = audio_segment.frame_rate 
        samples_float = samples.astype(np.float32)

        reduced_samples = nr.reduce_noise(y=samples_float, sr=sr)

        reduced_int16 = reduced_samples.astype(np.int16)

        denoised_segment = AudioSegment(
            data=reduced_int16.tobytes(),
            sample_width=2,  
            frame_rate=sr,
            channels=1
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as wav_file:
            wav_path = wav_file.name
        denoised_segment.export(wav_path, format="wav")
        print(f"[DEBUG] Processed WAV file exported: {wav_path}")

        return wav_path

    except Exception as e:
        print(f"Error during audio processing: {e}")
        raise
