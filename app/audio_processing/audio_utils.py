import tempfile
from pydub import AudioSegment
import noisereduce as nr
import numpy as np

def process_audio(raw_path: str, big_endian: bool = False) -> str:
    """
    Converts raw PCM data to WAV format, with optional byte order adjustment and noise reduction.
    Args:
        raw_path (str): Path to the raw PCM file.
        big_endian (bool): Whether the PCM data is in big-endian byte order.
    Returns:
        str: Path to the final WAV file.
    """
    try:
        if big_endian:
            print("[DEBUG] Converting PCM data from big-endian to little-endian...")
            with open(raw_path, 'rb') as f:
                raw_data = f.read()
            
            converted_data = bytearray()
            for i in range(0, len(raw_data), 4):
                chunk = raw_data[i:i+4]
                converted_data.extend(chunk[::-1])
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".raw") as temp_file:
                temp_file.write(converted_data)
                temp_file.flush()
                raw_path = temp_file.name
            print(f"[DEBUG] Byte order conversion complete: {raw_path}")

        audio_segment = AudioSegment.from_raw(
            file=raw_path,
            sample_width=4,
            frame_rate=44100,
            channels=1
        )
        print("[DEBUG] Successfully parsed raw PCM to AudioSegment")

        print("[DEBUG] Starting resampling and noise reduction...")
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
        print("[DEBUG] Noise reduction complete.")

        reduced_int16 = reduced_samples.astype(np.int16)

        denoised_segment = AudioSegment(
            data=reduced_int16.tobytes(),
            sample_width=2,
            frame_rate=sr,
            channels=1
        )

        audio_segment = denoised_segment

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as wav_file:
            wav_path = wav_file.name
        audio_segment.export(wav_path, format="wav")
        print(f"[DEBUG] Exported denoised PCM to WAV: {wav_path}")

        return wav_path

    except Exception as e:
        print(f"Error during PCM to WAV conversion: {e}")
        raise