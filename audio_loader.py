"""
audio_loader.py
録音したWAV音声ファイルを読み込んでバイナリ形式で返すモジュール
"""

import os
import io
import numpy as np
import scipy.io.wavfile as wavfile

AUDIO_DIR = "audio"

def load_interval_audio(filename: str) -> bytes:
    """
    audio/ ディレクトリ配下の指定WAVファイルを読み込み、バイナリデータを返す。
    ※ ファイルが未配置の場合は、動作テスト用のダミー音を自動生成して返す。
    """
    filepath = os.path.join(AUDIO_DIR, filename)
    
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            return f.read()
            
    # ファイルが見つからない場合のテスト用ダミー音
    sample_rate = 44100
    duration = 2.0
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    dummy_signal = (np.sin(2 * np.pi * 440 * t) * 0.5 * 32767).astype(np.int16)
    
    byte_io = io.BytesIO()
    wavfile.write(byte_io, sample_rate, dummy_signal)
    return byte_io.getvalue()