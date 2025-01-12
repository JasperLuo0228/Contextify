import tempfile
from pydub import AudioSegment
import noisereduce as nr  # 降噪模块
import numpy as np  # 用于降噪处理

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
        # 如果是大端序，先调整字节顺序
        if big_endian:
            print("[DEBUG] Converting PCM data from big-endian to little-endian...")
            with open(raw_path, 'rb') as f:
                raw_data = f.read()
            
            converted_data = bytearray()
            for i in range(0, len(raw_data), 4):  # 假设 sample_width=4 (32位浮点)
                chunk = raw_data[i:i+4]
                converted_data.extend(chunk[::-1])  # 每 4 字节翻转字节序
            
            # 写入临时文件替代原始路径
            with tempfile.NamedTemporaryFile(delete=False, suffix=".raw") as temp_file:
                temp_file.write(converted_data)
                temp_file.flush()
                raw_path = temp_file.name
            print(f"[DEBUG] Byte order conversion complete: {raw_path}")

        # 从 PCM 数据生成 AudioSegment
        audio_segment = AudioSegment.from_raw(
            file=raw_path,
            sample_width=4,   # 假设是 32 位浮点数；根据实际格式调整
            frame_rate=44100, # 假设采样率 44100 Hz
            channels=1        # 假设单声道；根据实际格式调整
        )
        print("[DEBUG] Successfully parsed raw PCM to AudioSegment")

        # 重采样、降噪
        print("[DEBUG] Starting resampling and noise reduction...")
        audio_segment = (
            audio_segment
            .set_frame_rate(16000)  # 重新采样到 16kHz
            .set_channels(1)        # 确保单声道
            .set_sample_width(2)    # 确保 16 位采样宽度
        )

        # 转换为 NumPy 数组以用于降噪
        samples = np.array(audio_segment.get_array_of_samples())
        sr = audio_segment.frame_rate  # 获取采样率
        samples_float = samples.astype(np.float32)  # 转为浮点数

        # 使用 noisereduce 进行降噪
        reduced_samples = nr.reduce_noise(y=samples_float, sr=sr)
        print("[DEBUG] Noise reduction complete.")

        # 将降噪后的数据转换回整数
        reduced_int16 = reduced_samples.astype(np.int16)

        # 用降噪后的数据创建新的 AudioSegment
        denoised_segment = AudioSegment(
            data=reduced_int16.tobytes(),
            sample_width=2,  # 降噪后为 16 位整型
            frame_rate=sr,
            channels=1
        )

        # 替换为降噪后的音频
        audio_segment = denoised_segment

        # 导出为 WAV 文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as wav_file:
            wav_path = wav_file.name
        audio_segment.export(wav_path, format="wav")
        print(f"[DEBUG] Exported denoised PCM to WAV: {wav_path}")

        return wav_path

    except Exception as e:
        print(f"Error during PCM to WAV conversion: {e}")
        raise